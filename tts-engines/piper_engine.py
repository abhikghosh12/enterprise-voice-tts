"""
Piper TTS Engine - Ultra-fast local TTS
High performance with minimal latency
"""
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import json

logger = logging.getLogger(__name__)


class PiperTTSEngine:
    """Piper TTS - Ultra-fast neural text-to-speech"""
    
    # Available Piper voices (high quality, fast)
    VOICES = {
        # English voices
        "en-US-lessac-medium": {
            "name": "US English Male (Lessac)",
            "language": "en-US",
            "gender": "male",
            "quality": "medium",
            "speed": "very_fast",
            "model_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
        },
        "en-US-lessac-high": {
            "name": "US English Male (Lessac HQ)",
            "language": "en-US",
            "gender": "male",
            "quality": "high",
            "speed": "fast",
            "model_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx"
        },
        "en-US-libritts-high": {
            "name": "US English Female (LibriTTS)",
            "language": "en-US",
            "gender": "female",
            "quality": "high",
            "speed": "fast",
            "model_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx"
        },
        "en-GB-alan-medium": {
            "name": "British English Male (Alan)",
            "language": "en-GB",
            "gender": "male",
            "quality": "medium",
            "speed": "very_fast",
            "model_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx"
        },
        # Add more voices as needed
    }
    
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir) / "piper"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.models_loaded = {}
        
        logger.info(f"🎯 Piper TTS engine initialized (cache: {self.cache_dir})")
    
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        sample_rate: int = 22050,
        **kwargs
    ) -> Dict:
        """
        Synthesize speech using Piper
        
        Piper is extremely fast but requires ONNX models to be downloaded first
        """
        # Map common voice IDs to Piper voices
        piper_voice = self._map_voice_id(voice_id)
        
        if not piper_voice:
            raise ValueError(f"Voice {voice_id} not supported by Piper engine")
        
        # Ensure model is downloaded
        model_path = await self._ensure_model(piper_voice)
        
        # Run Piper TTS
        try:
            command = [
                "piper",
                "--model", str(model_path),
                "--output_file", output_path,
            ]
            
            # Use subprocess for fast execution
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=text.encode())
            
            if process.returncode != 0:
                raise Exception(f"Piper TTS failed: {stderr.decode()}")
            
            # Get audio duration
            import wave
            with wave.open(output_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                audio_duration = frames / float(rate)
            
            return {
                "success": True,
                "audio_duration": audio_duration,
                "sample_rate": sample_rate
            }
            
        except Exception as e:
            logger.error(f"Piper synthesis error: {e}")
            raise
    
    def _map_voice_id(self, voice_id: str) -> Optional[str]:
        """Map standard voice IDs to Piper voice names"""
        mapping = {
            "en-US-GuyNeural": "en-US-lessac-medium",
            "en-US-JennyNeural": "en-US-libritts-high",
            "en-GB-RyanNeural": "en-GB-alan-medium",
        }
        return mapping.get(voice_id, voice_id if voice_id in self.VOICES else None)
    
    async def _ensure_model(self, voice_id: str) -> Path:
        """Download and cache Piper model if not present"""
        if voice_id not in self.VOICES:
            raise ValueError(f"Unknown Piper voice: {voice_id}")
        
        model_file = self.cache_dir / f"{voice_id}.onnx"
        config_file = self.cache_dir / f"{voice_id}.onnx.json"
        
        if model_file.exists() and config_file.exists():
            return model_file
        
        logger.info(f"📥 Downloading Piper model: {voice_id}")
        
        # Download model
        model_url = self.VOICES[voice_id]["model_url"]
        config_url = model_url + ".json"
        
        try:
            import urllib.request
            urllib.request.urlretrieve(model_url, model_file)
            urllib.request.urlretrieve(config_url, config_file)
            logger.info(f"✅ Model downloaded: {voice_id}")
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
        
        return model_file
    
    async def preload_model(self, voice_id: str):
        """Preload a model into memory"""
        piper_voice = self._map_voice_id(voice_id)
        if piper_voice:
            await self._ensure_model(piper_voice)
    
    def get_voices(self) -> List[Dict]:
        """Get list of available Piper voices"""
        return [
            {
                "id": voice_id,
                "name": info["name"],
                "language": info["language"],
                "gender": info["gender"],
                "quality": info["quality"],
                "speed": info["speed"]
            }
            for voice_id, info in self.VOICES.items()
        ]
