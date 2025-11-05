"""
Simple TTS engines for Python 3.13 compatibility
"""
import os
import asyncio
from pathlib import Path

class SimpleTTSManager:
    def __init__(self):
        self.engines = {}
        
    async def initialize_engines(self, engines=None):
        print("Initializing simple TTS engines...")
        
        # Try Edge TTS
        try:
            import edge_tts
            self.engines["edge"] = EdgeTTSSimple()
            print("Edge TTS ready")
        except ImportError:
            print("Warning: Edge TTS not available")
        
        # Try gTTS
        try:
            from gtts import gTTS
            self.engines["gtts"] = GTTSSimple()
            print("Google TTS ready")
        except ImportError:
            print("Warning: Google TTS not available")
        
        # Try system TTS
        try:
            import pyttsx3
            self.engines["system"] = SystemTTSSimple()
            print("System TTS ready")
        except ImportError:
            print("Warning: System TTS not available")
        
        if not self.engines:
            print("Error: No TTS engines available")
        else:
            print(f"TTS engines ready: {list(self.engines.keys())}")
    
    async def synthesize(self, text, voice_id, output_path, engine="auto", **kwargs):
        if engine == "auto":
            engine = list(self.engines.keys())[0] if self.engines else None
        
        if not engine or engine not in self.engines:
            raise Exception(f"Engine {engine} not available")
        
        return await self.engines[engine].synthesize(text, voice_id, output_path, **kwargs)
    
    def get_available_voices(self):
        voices = []
        for name, engine in self.engines.items():
            engine_voices = engine.get_voices()
            for voice in engine_voices:
                voice["engine"] = name
                voices.append(voice)
        return voices

class EdgeTTSSimple:
    async def synthesize(self, text, voice_id, output_path, **kwargs):
        import edge_tts
        
        # Use default voice if not specified
        if not voice_id or voice_id == "auto":
            voice_id = "en-US-AriaNeural"
        
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(output_path)
        
        return {
            "sample_rate": 24000,
            "audio_duration": len(text) * 0.1
        }
    
    def get_voices(self):
        return [
            {"id": "en-US-AriaNeural", "name": "Aria (US)", "language": "en-US"},
            {"id": "en-US-JennyNeural", "name": "Jenny (US)", "language": "en-US"},
            {"id": "en-GB-SoniaNeural", "name": "Sonia (UK)", "language": "en-GB"},
        ]

class GTTSSimple:
    def __init__(self):
        self.lang_map = {
            "gtts-en": "en",
            "gtts-en-uk": "en", 
            "gtts-en-au": "en",
            "gtts-es": "es",
            "gtts-fr": "fr", 
            "gtts-de": "de",
            "gtts-it": "it",
            "gtts-pt": "pt",
            "gtts-ru": "ru",
            "gtts-ja": "ja",
            "gtts-ko": "ko",
            "gtts-zh": "zh",
            "gtts-hi": "hi",
            "gtts-ar": "ar"
        }
    
    async def synthesize(self, text, voice_id, output_path, **kwargs):
        from gtts import gTTS
        import asyncio
        
        # Get language code
        lang = self.lang_map.get(voice_id, "en")
        
        # Run in thread since gTTS is blocking
        def _synthesize():
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
        
        await asyncio.get_event_loop().run_in_executor(None, _synthesize)
        
        return {
            "sample_rate": 24000,
            "audio_duration": len(text) * 0.1
        }
    
    def get_voices(self):
        return [
            {"id": "gtts-en", "name": "Google English (US)", "language": "en"},
            {"id": "gtts-es", "name": "Google Spanish", "language": "es"},
            {"id": "gtts-fr", "name": "Google French", "language": "fr"},
            {"id": "gtts-de", "name": "Google German", "language": "de"},
        ]

class SystemTTSSimple:
    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()
    
    async def synthesize(self, text, voice_id, output_path, **kwargs):
        import asyncio
        
        def _synthesize():
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
        
        await asyncio.get_event_loop().run_in_executor(None, _synthesize)
        
        return {
            "sample_rate": 22050,
            "audio_duration": len(text) * 0.1
        }
    
    def get_voices(self):
        return [
            {"id": "system", "name": "System Voice", "language": "en"},
        ]

# Global instance
_simple_tts = None

def get_simple_tts():
    global _simple_tts
    if _simple_tts is None:
        _simple_tts = SimpleTTSManager()
    return _simple_tts