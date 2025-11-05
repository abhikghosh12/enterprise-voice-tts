"""
Edge TTS Engine - Microsoft Edge Text-to-Speech
Free, high-quality voices from Microsoft
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, List
import edge_tts

logger = logging.getLogger(__name__)


class EdgeTTSEngine:
    """Microsoft Edge TTS - Free high-quality voices"""
    
    # Comprehensive voice list
    VOICES = {
        # US English
        "en-US-GuyNeural": {"name": "Guy (Morgan Freeman-like)", "language": "en-US", "gender": "Male"},
        "en-US-JennyNeural": {"name": "Jenny (US Female)", "language": "en-US", "gender": "Female"},
        "en-US-AriaNeural": {"name": "Aria (US Female)", "language": "en-US", "gender": "Female"},
        "en-US-DavisNeural": {"name": "Davis (US Male)", "language": "en-US", "gender": "Male"},
        "en-US-TonyNeural": {"name": "Tony (US Male)", "language": "en-US", "gender": "Male"},
        
        # UK English  
        "en-GB-RyanNeural": {"name": "Ryan (UK Male)", "language": "en-GB", "gender": "Male"},
        "en-GB-SoniaNeural": {"name": "Sonia (UK Female)", "language": "en-GB", "gender": "Female"},
        "en-GB-LibbyNeural": {"name": "Libby (UK Female)", "language": "en-GB", "gender": "Female"},
        
        # Indian English
        "en-IN-NeerjaNeural": {"name": "Neerja (Indian Female)", "language": "en-IN", "gender": "Female"},
        "en-IN-PrabhatNeural": {"name": "Prabhat (Indian Male)", "language": "en-IN", "gender": "Male"},
        
        # Hindi
        "hi-IN-SwaraNeural": {"name": "Swara (Hindi Female)", "language": "hi-IN", "gender": "Female"},
        "hi-IN-MadhurNeural": {"name": "Madhur (Hindi Male)", "language": "hi-IN", "gender": "Male"},
        
        # German
        "de-DE-KatjaNeural": {"name": "Katja (German Female)", "language": "de-DE", "gender": "Female"},
        "de-DE-ConradNeural": {"name": "Conrad (German Male)", "language": "de-DE", "gender": "Male"},
        
        # French
        "fr-FR-DeniseNeural": {"name": "Denise (French Female)", "language": "fr-FR", "gender": "Female"},
        "fr-FR-HenriNeural": {"name": "Henri (French Male)", "language": "fr-FR", "gender": "Male"},
        
        # Spanish
        "es-ES-ElviraNeural": {"name": "Elvira (Spanish Female)", "language": "es-ES", "gender": "Female"},
        "es-ES-AlvaroNeural": {"name": "Alvaro (Spanish Male)", "language": "es-ES", "gender": "Male"},
        
        # Portuguese
        "pt-BR-FranciscaNeural": {"name": "Francisca (Portuguese Female)", "language": "pt-BR", "gender": "Female"},
        "pt-BR-AntonioNeural": {"name": "Antonio (Portuguese Male)", "language": "pt-BR", "gender": "Male"},
        
        # Japanese
        "ja-JP-NanamiNeural": {"name": "Nanami (Japanese Female)", "language": "ja-JP", "gender": "Female"},
        "ja-JP-KeitaNeural": {"name": "Keita (Japanese Male)", "language": "ja-JP", "gender": "Male"},
        
        # Chinese
        "zh-CN-XiaoxiaoNeural": {"name": "Xiaoxiao (Chinese Female)", "language": "zh-CN", "gender": "Female"},
        "zh-CN-YunxiNeural": {"name": "Yunxi (Chinese Male)", "language": "zh-CN", "gender": "Male"},
    }
    
    def __init__(self):
        logger.info("☁️ Edge TTS engine initialized")
    
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        sample_rate: int = 24000,
        **kwargs
    ) -> Dict:
        """
        Synthesize speech using Edge TTS
        
        Edge TTS features:
        - 200+ voices
        - 100+ languages
        - Free to use
        - Good quality
        - Requires internet connection
        """
        if voice_id not in self.VOICES:
            # Try to find a matching voice
            voice_id = self._find_voice(voice_id)
        
        try:
            # Create Edge TTS communicator
            communicate = edge_tts.Communicate(text, voice_id)
            
            # Save audio
            await communicate.save(output_path)
            
            # Get audio duration
            import soundfile as sf
            data, sr = sf.read(output_path)
            audio_duration = len(data) / sr
            
            return {
                "success": True,
                "audio_duration": audio_duration,
                "sample_rate": sr
            }
            
        except Exception as e:
            logger.error(f"Edge TTS synthesis error: {e}")
            raise
    
    def _find_voice(self, voice_id: str) -> str:
        """Find closest matching voice"""
        # If exact match exists, use it
        if voice_id in self.VOICES:
            return voice_id
        
        # Try to match language prefix
        lang_prefix = voice_id.split("-")[0] + "-" + voice_id.split("-")[1] if "-" in voice_id else "en-US"
        
        for vid in self.VOICES:
            if vid.startswith(lang_prefix):
                return vid
        
        # Default to US English male
        return "en-US-GuyNeural"
    
    async def preload_model(self, voice_id: str):
        """Edge TTS doesn't need preloading"""
        pass
    
    def get_voices(self) -> List[Dict]:
        """Get list of available Edge TTS voices"""
        return [
            {
                "id": voice_id,
                "name": info["name"],
                "language": info["language"],
                "gender": info["gender"]
            }
            for voice_id, info in self.VOICES.items()
        ]
    
    async def list_all_voices(self) -> List[Dict]:
        """Get all available voices from Edge TTS service"""
        try:
            voices = await edge_tts.list_voices()
            return [
                {
                    "id": v["ShortName"],
                    "name": v["FriendlyName"],
                    "language": v["Locale"],
                    "gender": v["Gender"]
                }
                for v in voices
            ]
        except Exception as e:
            logger.error(f"Failed to list Edge voices: {e}")
            return self.get_voices()
