"""
Voice Activity Detection (VAD) Service
Detects when someone is speaking in audio stream
"""

import torch
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class VADService:
    """Voice Activity Detection using Silero VAD"""
    
    def __init__(
        self,
        threshold: float = 0.5,
        sampling_rate: int = 16000,
        window_size: int = 512
    ):
        """
        Initialize VAD service
        
        Args:
            threshold: Detection threshold (0-1)
            sampling_rate: Audio sample rate
            window_size: Size of analysis window
        """
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Load Silero VAD model"""
        try:
            logger.info("Loading Silero VAD model")
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            
            self.get_speech_timestamps = utils[0]
            logger.info("VAD model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load VAD model: {e}")
            raise
    
    def detect_speech(
        self,
        audio_data: bytes,
        return_timestamps: bool = False
    ) -> Tuple[bool, List[dict]]:
        """
        Detect speech in audio data
        
        Args:
            audio_data: Raw audio bytes
            return_timestamps: Return speech segment timestamps
            
        Returns:
            (has_speech: bool, timestamps: List[dict])
        """
        try:
            # Convert bytes to tensor
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            audio_tensor = torch.from_numpy(audio_array)
            
            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                threshold=self.threshold,
                sampling_rate=self.sampling_rate,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100
            )
            
            has_speech = len(speech_timestamps) > 0
            
            if return_timestamps:
                return has_speech, speech_timestamps
            else:
                return has_speech, []
                
        except Exception as e:
            logger.error(f"VAD detection error: {e}")
            return False, []
    
    def is_speaking(self, audio_chunk: bytes) -> bool:
        """
        Quick check if audio chunk contains speech
        
        Args:
            audio_chunk: Audio chunk bytes
            
        Returns:
            True if speech detected
        """
        has_speech, _ = self.detect_speech(audio_chunk, return_timestamps=False)
        return has_speech
    
    def get_speech_segments(
        self,
        audio_data: bytes
    ) -> List[Tuple[float, float]]:
        """
        Get speech segments from audio
        
        Args:
            audio_data: Full audio bytes
            
        Returns:
            List of (start_time, end_time) tuples in seconds
        """
        has_speech, timestamps = self.detect_speech(audio_data, return_timestamps=True)
        
        if not has_speech:
            return []
        
        segments = []
        for ts in timestamps:
            start_time = ts['start'] / self.sampling_rate
            end_time = ts['end'] / self.sampling_rate
            segments.append((start_time, end_time))
        
        return segments
    
    def filter_silence(
        self,
        audio_data: bytes,
        pad_ms: int = 100
    ) -> bytes:
        """
        Remove silence from audio, keeping only speech
        
        Args:
            audio_data: Raw audio bytes
            pad_ms: Padding around speech segments (milliseconds)
            
        Returns:
            Filtered audio bytes
        """
        try:
            # Get speech segments
            segments = self.get_speech_segments(audio_data)
            
            if not segments:
                return b''  # No speech detected
            
            # Convert audio to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate padding in samples
            pad_samples = int(pad_ms * self.sampling_rate / 1000)
            
            # Extract speech segments with padding
            filtered_audio = []
            for start_time, end_time in segments:
                start_sample = max(0, int(start_time * self.sampling_rate) - pad_samples)
                end_sample = min(len(audio_array), int(end_time * self.sampling_rate) + pad_samples)
                
                filtered_audio.append(audio_array[start_sample:end_sample])
            
            # Concatenate segments
            if filtered_audio:
                result = np.concatenate(filtered_audio)
                return result.tobytes()
            else:
                return b''
                
        except Exception as e:
            logger.error(f"Silence filtering error: {e}")
            return audio_data  # Return original on error


class StreamingVAD:
    """
    Streaming VAD for real-time detection
    Maintains state across chunks
    """
    
    def __init__(self, vad_service: VADService):
        self.vad = vad_service
        self.is_speaking = False
        self.speech_started_at = None
        self.silence_duration = 0
        self.speech_duration = 0
        self.max_silence_ms = 500  # End speech after 500ms silence
        self.min_speech_ms = 250   # Minimum speech duration
    
    def process_chunk(
        self,
        audio_chunk: bytes,
        chunk_duration_ms: int = 100
    ) -> dict:
        """
        Process audio chunk and update state
        
        Args:
            audio_chunk: Audio chunk bytes
            chunk_duration_ms: Duration of chunk in milliseconds
            
        Returns:
            {
                'has_speech': bool,
                'speech_started': bool,
                'speech_ended': bool,
                'speech_duration': float
            }
        """
        has_speech = self.vad.is_speaking(audio_chunk)
        
        speech_started = False
        speech_ended = False
        
        if has_speech:
            if not self.is_speaking:
                # Speech just started
                self.is_speaking = True
                self.speech_started_at = 0
                self.speech_duration = 0
                speech_started = True
                logger.debug("Speech started")
            
            # Reset silence counter
            self.silence_duration = 0
            self.speech_duration += chunk_duration_ms
            
        else:
            if self.is_speaking:
                # In speech but current chunk is silent
                self.silence_duration += chunk_duration_ms
                
                # Check if silence threshold exceeded
                if self.silence_duration >= self.max_silence_ms:
                    # Check if speech was long enough
                    if self.speech_duration >= self.min_speech_ms:
                        speech_ended = True
                        logger.debug(f"Speech ended (duration: {self.speech_duration}ms)")
                    
                    # Reset state
                    self.is_speaking = False
                    self.speech_started_at = None
                    self.silence_duration = 0
                    self.speech_duration = 0
        
        return {
            'has_speech': has_speech,
            'speech_started': speech_started,
            'speech_ended': speech_ended,
            'speech_duration': self.speech_duration / 1000.0,  # Convert to seconds
            'is_speaking': self.is_speaking
        }


# ============================================
# Example Usage
# ============================================

async def main():
    """Example usage"""
    import sys
    import soundfile as sf
    
    vad = VADService(threshold=0.5)
    
    if len(sys.argv) > 1:
        # Analyze file
        audio_file = sys.argv[1]
        print(f"Analyzing: {audio_file}")
        
        # Read audio file
        audio_array, sample_rate = sf.read(audio_file)
        if len(audio_array.shape) > 1:
            audio_array = audio_array.mean(axis=1)
        
        audio_bytes = (audio_array * 32768).astype(np.int16).tobytes()
        
        # Detect speech
        has_speech, timestamps = vad.detect_speech(audio_bytes, return_timestamps=True)
        
        print(f"\nSpeech detected: {has_speech}")
        
        if has_speech:
            print(f"\nSpeech segments:")
            for ts in timestamps:
                start = ts['start'] / sample_rate
                end = ts['end'] / sample_rate
                duration = end - start
                print(f"  {start:.2f}s - {end:.2f}s (duration: {duration:.2f}s)")
            
            # Filter silence
            print("\nFiltering silence...")
            filtered = vad.filter_silence(audio_bytes)
            print(f"Original size: {len(audio_bytes)} bytes")
            print(f"Filtered size: {len(filtered)} bytes")
            print(f"Compression: {(1 - len(filtered)/len(audio_bytes)) * 100:.1f}%")
    else:
        print("Usage: python vad_service.py <audio_file>")


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
