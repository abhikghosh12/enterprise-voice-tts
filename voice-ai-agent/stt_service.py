"""
Speech-to-Text Service using OpenAI Whisper
Provides real-time audio transcription with streaming support
"""

import asyncio
import io
import wave
from typing import AsyncGenerator, Optional
from faster_whisper import WhisperModel
import numpy as np
import soundfile as sf
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class TranscriptionConfig(BaseModel):
    """Configuration for transcription"""
    model_size: str = "base"  # tiny, base, small, medium, large
    language: Optional[str] = None  # Auto-detect if None
    device: str = "cpu"  # cpu or cuda
    compute_type: str = "int8"  # int8, float16, float32
    beam_size: int = 5
    vad_filter: bool = True  # Use Voice Activity Detection


class TranscriptionResult(BaseModel):
    """Transcription result"""
    text: str
    language: str
    confidence: float
    segments: list = []
    duration: float = 0.0


class STTService:
    """Speech-to-Text Service using Faster Whisper"""
    
    def __init__(self, config: TranscriptionConfig = None):
        self.config = config or TranscriptionConfig()
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.config.model_size}")
            self.model = WhisperModel(
                self.config.model_size,
                device=self.config.device,
                compute_type=self.config.compute_type
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> TranscriptionResult:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            
        Returns:
            TranscriptionResult with transcription
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Transcribe with Whisper
            segments, info = self.model.transcribe(
                audio_array,
                language=self.config.language,
                beam_size=self.config.beam_size,
                vad_filter=self.config.vad_filter,
                task="transcribe"
            )
            
            # Collect segments
            text_segments = []
            full_text = ""
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                text_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text,
                    'confidence': segment.avg_logprob
                })
                full_text += segment.text + " "
                total_confidence += segment.avg_logprob
                segment_count += 1
            
            avg_confidence = total_confidence / segment_count if segment_count > 0 else 0.0
            
            return TranscriptionResult(
                text=full_text.strip(),
                language=info.language,
                confidence=float(np.exp(avg_confidence)),  # Convert log prob to confidence
                segments=text_segments,
                duration=info.duration
            )
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    async def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            TranscriptionResult
        """
        try:
            # Read audio file
            audio_array, sample_rate = sf.read(audio_path)
            
            # Convert to mono if stereo
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)
            
            # Convert to bytes
            audio_bytes = (audio_array * 32768).astype(np.int16).tobytes()
            
            return await self.transcribe_audio(audio_bytes, sample_rate)
            
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            raise
    
    async def transcribe_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        chunk_duration: float = 2.0
    ) -> AsyncGenerator[TranscriptionResult, None]:
        """
        Transcribe streaming audio
        
        Args:
            audio_stream: Async generator yielding audio chunks
            chunk_duration: Duration of each chunk in seconds
            
        Yields:
            TranscriptionResult for each chunk
        """
        buffer = bytearray()
        sample_rate = 16000
        chunk_size = int(chunk_duration * sample_rate * 2)  # 2 bytes per sample
        
        try:
            async for audio_chunk in audio_stream:
                buffer.extend(audio_chunk)
                
                # Process when we have enough data
                while len(buffer) >= chunk_size:
                    # Extract chunk
                    chunk = bytes(buffer[:chunk_size])
                    buffer = buffer[chunk_size:]
                    
                    # Transcribe chunk
                    result = await self.transcribe_audio(chunk, sample_rate)
                    
                    if result.text.strip():  # Only yield non-empty results
                        yield result
            
            # Process remaining buffer
            if len(buffer) > 0:
                result = await self.transcribe_audio(bytes(buffer), sample_rate)
                if result.text.strip():
                    yield result
                    
        except Exception as e:
            logger.error(f"Stream transcription error: {e}")
            raise


class DeepgramSTT:
    """
    Deepgram STT as fallback/alternative
    (Requires API key and internet)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepgram.com/v1/listen"
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> TranscriptionResult:
        """Transcribe using Deepgram API"""
        import aiohttp
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav"
        }
        
        params = {
            "model": "nova-2",
            "smart_format": "true",
            "punctuate": "true",
            "language": "en"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    params=params,
                    data=audio_data
                ) as response:
                    result = await response.json()
                    
                    transcript = result["results"]["channels"][0]["alternatives"][0]
                    
                    return TranscriptionResult(
                        text=transcript["transcript"],
                        language="en",
                        confidence=transcript["confidence"],
                        segments=[],
                        duration=0.0
                    )
                    
        except Exception as e:
            logger.error(f"Deepgram error: {e}")
            raise


# ============================================
# Example Usage
# ============================================

async def main():
    """Example usage"""
    import sys
    
    # Initialize STT service
    config = TranscriptionConfig(
        model_size="base",  # Fast and accurate
        device="cpu",
        vad_filter=True
    )
    
    stt = STTService(config)
    
    if len(sys.argv) > 1:
        # Transcribe file
        audio_file = sys.argv[1]
        print(f"Transcribing: {audio_file}")
        
        result = await stt.transcribe_file(audio_file)
        
        print(f"\nTranscription:")
        print(f"Text: {result.text}")
        print(f"Language: {result.language}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Duration: {result.duration:.2f}s")
        
        if result.segments:
            print(f"\nSegments:")
            for seg in result.segments:
                print(f"  [{seg['start']:.2f}s - {seg['end']:.2f}s]: {seg['text']}")
    else:
        print("Usage: python stt_service.py <audio_file>")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
