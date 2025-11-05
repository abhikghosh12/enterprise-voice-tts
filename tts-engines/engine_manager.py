"""
Enterprise TTS Engine Manager
Supports multiple TTS engines with automatic model caching and optimization
"""
import os
import time
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TTSEngineManager:
    """Manages multiple TTS engines with automatic fallback and caching"""
    
    def __init__(self, cache_dir: str = "./models_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.engines = {}
        self.model_cache = {}
        
        logger.info("🚀 Initializing TTS Engine Manager")
        
    async def initialize_engines(self, engines: List[str] = None):
        """Initialize requested TTS engines"""
        if engines is None:
            engines = ["edge", "piper", "coqui", "silero"]  # Try all engines
        
        print("🚀 Initializing TTS engines...")
        for engine_name in engines:
            try:
                await self._initialize_engine(engine_name)
            except Exception as e:
                logger.error(f"Failed to initialize {engine_name}: {e}")
        
        if not self.engines:
            logger.warning("⚠️ No TTS engines available - using fallback")
            # Create a simple fallback engine
            self.engines["fallback"] = SimpleFallbackEngine()
        
        print(f"✅ TTS engines ready: {list(self.engines.keys())}")
    
    async def _initialize_engine(self, engine_name: str):
        """Initialize a specific TTS engine"""
        if engine_name == "piper":
            try:
                from tts_engines.piper_engine import PiperTTSEngine
                self.engines["piper"] = PiperTTSEngine(str(self.cache_dir))
                logger.info("✅ Piper TTS engine initialized (Ultra-fast)")
            except ImportError:
                logger.warning("⚠️ Piper TTS not available (requires piper-tts package)")
            
        elif engine_name == "edge":
            try:
                from tts_engines.edge_engine import EdgeTTSEngine
                self.engines["edge"] = EdgeTTSEngine()
                logger.info("✅ Edge TTS engine initialized")
            except ImportError:
                logger.warning("⚠️ Edge TTS not available (requires edge-tts package)")
            
        elif engine_name == "coqui":
            try:
                from tts_engines.coqui_engine import CoquiTTSEngine
                self.engines["coqui"] = CoquiTTSEngine(str(self.cache_dir))
                logger.info("✅ Coqui TTS engine initialized (High quality)")
            except ImportError:
                logger.warning("⚠️ Coqui TTS not available (requires TTS package)")
            
        elif engine_name == "silero":
            try:
                from tts_engines.silero_engine import SileroTTSEngine
                self.engines["silero"] = SileroTTSEngine(str(self.cache_dir))
                logger.info("✅ Silero TTS engine initialized (Fast)")
            except ImportError:
                logger.warning("⚠️ Silero TTS not available (requires silero package)")
    
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        engine: str = "auto",
        sample_rate: int = 24000,
        **kwargs
    ) -> Dict:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice_id: Voice identifier
            output_path: Path to save audio file
            engine: TTS engine to use ('auto', 'piper', 'edge', 'coqui', 'silero')
            sample_rate: Audio sample rate
            **kwargs: Additional engine-specific parameters
        
        Returns:
            Dictionary with synthesis results
        """
        start_time = time.time()
        
        # Auto-select best engine based on requirements
        if engine == "auto":
            engine = self._select_best_engine(text, voice_id)
        
        if engine not in self.engines:
            raise ValueError(f"Engine '{engine}' not available. Available: {list(self.engines.keys())}")
        
        logger.info(f"🎙️ Synthesizing with {engine} engine: {voice_id}")
        
        try:
            # Perform synthesis
            result = await self.engines[engine].synthesize(
                text=text,
                voice_id=voice_id,
                output_path=output_path,
                sample_rate=sample_rate,
                **kwargs
            )
            
            elapsed_time = time.time() - start_time
            
            # Get file size
            file_size = Path(output_path).stat().st_size
            
            logger.info(f"✨ Synthesis completed in {elapsed_time:.2f}s ({file_size/1024:.1f}KB)")
            
            return {
                "success": True,
                "engine": engine,
                "voice_id": voice_id,
                "duration": elapsed_time,
                "file_size": file_size,
                "output_path": output_path,
                "sample_rate": result.get("sample_rate", sample_rate),
                "audio_duration": result.get("audio_duration", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Synthesis failed: {e}")
            
            # Try fallback to Edge TTS if available
            if engine != "edge" and "edge" in self.engines:
                logger.info("🔄 Attempting fallback to Edge TTS")
                return await self.synthesize(
                    text, voice_id, output_path, engine="edge", sample_rate=sample_rate
                )
            
            raise
    
    def _select_best_engine(self, text: str, voice_id: str) -> str:
        """Automatically select the best engine based on requirements"""
        
        # For very short text, use fastest engine
        if len(text) < 100:
            if "piper" in self.engines:
                return "piper"
        
        # For English voices, prefer Piper or Coqui
        if voice_id.startswith("en-"):
            if "piper" in self.engines:
                return "piper"
            if "coqui" in self.engines:
                return "coqui"
        
        # For other languages, use Edge TTS
        if "edge" in self.engines:
            return "edge"
        
        # Default to first available engine
        return list(self.engines.keys())[0]
    
    def get_available_voices(self, engine: str = None) -> List[Dict]:
        """Get list of available voices"""
        if engine and engine in self.engines:
            return self.engines[engine].get_voices()
        
        # Return voices from all engines
        all_voices = []
        for eng_name, eng in self.engines.items():
            voices = eng.get_voices()
            for voice in voices:
                voice["engine"] = eng_name
                all_voices.append(voice)
        
        return all_voices
    
    async def preload_models(self, voices: List[str]):
        """Preload models for faster first synthesis"""
        logger.info(f"📦 Preloading models for {len(voices)} voices")
        
        for voice_id in voices:
            for engine in self.engines.values():
                try:
                    await engine.preload_model(voice_id)
                except:
                    pass  # Skip if voice not supported by this engine
    
    def get_engine_stats(self) -> Dict:
        """Get statistics about loaded engines"""
        return {
            "engines_loaded": list(self.engines.keys()),
            "total_engines": len(self.engines),
            "cache_dir": str(self.cache_dir),
            "models_cached": len(self.model_cache)
        }


class SimpleFallbackEngine:
    """Simple fallback TTS engine using system TTS"""
    
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.available = True
        except:
            self.available = False
    
    async def synthesize(self, text, voice_id, output_path, **kwargs):
        if not self.available:
            raise Exception("No TTS engines available")
        
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        
        return {
            "sample_rate": 22050,
            "audio_duration": len(text) * 0.1  # Rough estimate
        }
    
    def get_voices(self):
        return [{"id": "system", "name": "System Voice", "language": "en"}]


# Singleton instance
_engine_manager = None

def get_engine_manager() -> TTSEngineManager:
    """Get or create the global engine manager instance"""
    global _engine_manager
    if _engine_manager is None:
        _engine_manager = TTSEngineManager()
    return _engine_manager
