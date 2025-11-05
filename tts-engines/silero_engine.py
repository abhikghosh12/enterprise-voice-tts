"""
Silero TTS Engine - Ultra-fast lightweight TTS
Optimized for Russian and English
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, List
import torch
import soundfile as sf

logger = logging.getLogger(__name__)


class SileroTTSEngine:
    """Silero TTS - Fast and lightweight"""
    
    VOICES = {
        # Russian voices
        "ru-RU-aidar": {"name": "Aidar (Russian Male)", "language": "ru", "speaker": "aidar"},
        "ru-RU-baya": {"name": "Baya (Russian Female)", "language": "ru", "speaker": "baya"},
        "ru-RU-kseniya": {"name": "Kseniya (Russian Female)", "language": "ru", "speaker": "kseniya"},
        "ru-RU-xenia": {"name": "Xenia (Russian Female)", "language": "ru", "speaker": "xenia"},
        
        # English voices
        "en-US-lj": {"name": "LJ (US Female)", "language": "en", "speaker": "lj"},
    }
    
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir) / "silero"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.models = {}
        self.device = torch.device('cpu')  # Silero runs well on CPU
        
        logger.info("⚡ Silero TTS engine initialized")
    
    async def _load_model(self, language: str):
        """Load Silero model for specific language"""
        if language in self.models:
            return self.models[language]
        
        logger.info(f"📦 Loading Silero {language} model...")
        
        try:
            # Load model from torch hub
            if language == "ru":
                model, _ = torch.hub.load(
                    repo_or_dir='snakers4/silero-models',
                    model='silero_tts',
                    language=language,
                    speaker='v3_1_ru'
                )
            else:  # English
                model, _ = torch.hub.load(
                    repo_or_dir='snakers4/silero-models',
                    model='silero_tts',
                    language=language,
                    speaker='lj_16khz'
                )
            
            model.to(self.device)
            self.models[language] = model
            
            logger.info(f"✅ Silero {language} model loaded")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load Silero model: {e}")
            raise
    
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        sample_rate: int = 48000,
        **kwargs
    ) -> Dict:
        """
        Synthesize speech using Silero
        
        Silero features:
        - Very fast (real-time on CPU)
        - Small model size (~40MB)
        - Good quality
        - Works offline
        - Best for Russian and English
        """
        if voice_id not in self.VOICES:
            voice_id = self._map_voice(voice_id)
        
        voice_info = self.VOICES[voice_id]
        language = voice_info["language"]
        speaker = voice_info["speaker"]
        
        # Load model
        model = await self._load_model(language)
        
        try:
            # Run synthesis in thread pool
            loop = asyncio.get_event_loop()
            
            def _synthesize():
                audio = model.apply_tts(
                    text=text,
                    speaker=speaker,
                    sample_rate=sample_rate
                )
                return audio.numpy()
            
            audio_data = await loop.run_in_executor(None, _synthesize)
            
            # Save audio file
            sf.write(output_path, audio_data, sample_rate)
            
            # Calculate duration
            audio_duration = len(audio_data) / sample_rate
            
            return {
                "success": True,
                "audio_duration": audio_duration,
                "sample_rate": sample_rate
            }
            
        except Exception as e:
            logger.error(f"Silero synthesis error: {e}")
            raise
    
    def _map_voice(self, voice_id: str) -> str:
        """Map common voice IDs to Silero voices"""
        if voice_id.startswith("ru-"):
            return "ru-RU-aidar"  # Default Russian male
        return "en-US-lj"  # Default English female
    
    async def preload_model(self, voice_id: str):
        """Preload model"""
        if voice_id in self.VOICES:
            voice_info = self.VOICES[voice_id]
            await self._load_model(voice_info["language"])
    
    def get_voices(self) -> List[Dict]:
        """Get list of available Silero voices"""
        return [
            {
                "id": voice_id,
                "name": info["name"],
                "language": info["language"]
            }
            for voice_id, info in self.VOICES.items()
        ]
