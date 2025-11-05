"""
Coqui TTS Engine - High Quality Multi-lingual TTS
Supports XTTS-v2 for voice cloning and multiple languages
"""
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import torch

logger = logging.getLogger(__name__)


class CoquiTTSEngine:
    """Coqui TTS - High quality neural TTS with voice cloning"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir) / "coqui"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🎨 Coqui TTS engine initialized (device: {self.device})")
        
    async def _load_model(self):
        """Load XTTS-v2 model (lazy loading for memory efficiency)"""
        if self.model is not None:
            return
        
        logger.info("📦 Loading Coqui XTTS-v2 model...")
        
        try:
            from TTS.api import TTS
            
            # Load XTTS-v2 model (supports 13 languages)
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            
            logger.info("✅ XTTS-v2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Coqui model: {e}")
            raise
    
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        sample_rate: int = 24000,
        **kwargs
    ) -> Dict:
        """
        Synthesize speech using Coqui XTTS-v2
        
        XTTS-v2 features:
        - 13 languages supported
        - Voice cloning from 6-second samples
        - High quality output
        - Emotion and style control
        """
        await self._load_model()
        
        # Extract language from voice_id
        language = self._extract_language(voice_id)
        
        # Get speaker voice (can use default or custom speaker samples)
        speaker_wav = kwargs.get("speaker_wav", None)
        
        try:
            # Run synthesis in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _synthesize():
                if speaker_wav:
                    # Voice cloning mode
                    self.model.tts_to_file(
                        text=text,
                        speaker_wav=speaker_wav,
                        language=language,
                        file_path=output_path
                    )
                else:
                    # Use default speaker
                    self.model.tts_to_file(
                        text=text,
                        language=language,
                        file_path=output_path
                    )
            
            await loop.run_in_executor(None, _synthesize)
            
            # Calculate audio duration
            import soundfile as sf
            data, samplerate = sf.read(output_path)
            audio_duration = len(data) / samplerate
            
            return {
                "success": True,
                "audio_duration": audio_duration,
                "sample_rate": samplerate
            }
            
        except Exception as e:
            logger.error(f"Coqui synthesis error: {e}")
            raise
    
    def _extract_language(self, voice_id: str) -> str:
        """Extract language code from voice ID"""
        # Map voice IDs to XTTS language codes
        lang_map = {
            "en-": "en",
            "hi-": "hi",  # Hindi
            "de-": "de",  # German
            "fr-": "fr",  # French
            "es-": "es",  # Spanish
            "it-": "it",  # Italian
            "pt-": "pt",  # Portuguese
            "pl-": "pl",  # Polish
            "tr-": "tr",  # Turkish
            "ru-": "ru",  # Russian
            "nl-": "nl",  # Dutch
            "cs-": "cs",  # Czech
            "ar-": "ar",  # Arabic
            "zh-": "zh-cn",  # Chinese
        }
        
        for prefix, lang_code in lang_map.items():
            if voice_id.startswith(prefix):
                return lang_code
        
        return "en"  # Default to English
    
    async def clone_voice(
        self,
        text: str,
        speaker_audio_path: str,
        output_path: str,
        language: str = "en"
    ) -> Dict:
        """
        Clone a voice from a speaker sample
        
        Args:
            text: Text to synthesize
            speaker_audio_path: Path to 6+ second audio sample of target voice
            output_path: Where to save output
            language: Language code
        """
        await self._load_model()
        
        return await self.synthesize(
            text=text,
            voice_id=f"{language}-CUSTOM",
            output_path=output_path,
            speaker_wav=speaker_audio_path
        )
    
    async def preload_model(self, voice_id: str):
        """Preload model"""
        await self._load_model()
    
    def get_voices(self) -> List[Dict]:
        """Get list of supported languages"""
        return [
            {"id": "en-XTTS", "name": "English (XTTS)", "language": "en", "quality": "high"},
            {"id": "hi-XTTS", "name": "Hindi (XTTS)", "language": "hi", "quality": "high"},
            {"id": "de-XTTS", "name": "German (XTTS)", "language": "de", "quality": "high"},
            {"id": "fr-XTTS", "name": "French (XTTS)", "language": "fr", "quality": "high"},
            {"id": "es-XTTS", "name": "Spanish (XTTS)", "language": "es", "quality": "high"},
            {"id": "it-XTTS", "name": "Italian (XTTS)", "language": "it", "quality": "high"},
            {"id": "pt-XTTS", "name": "Portuguese (XTTS)", "language": "pt", "quality": "high"},
            {"id": "pl-XTTS", "name": "Polish (XTTS)", "language": "pl", "quality": "high"},
            {"id": "tr-XTTS", "name": "Turkish (XTTS)", "language": "tr", "quality": "high"},
            {"id": "ru-XTTS", "name": "Russian (XTTS)", "language": "ru", "quality": "high"},
            {"id": "nl-XTTS", "name": "Dutch (XTTS)", "language": "nl", "quality": "high"},
            {"id": "cs-XTTS", "name": "Czech (XTTS)", "language": "cs", "quality": "high"},
            {"id": "ar-XTTS", "name": "Arabic (XTTS)", "language": "ar", "quality": "high"},
            {"id": "zh-XTTS", "name": "Chinese (XTTS)", "language": "zh-cn", "quality": "high"},
        ]
