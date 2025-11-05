# TTS Engines Package

# Make engines importable
try:
    from .engine_manager import TTSEngineManager, get_engine_manager
except ImportError:
    pass

__all__ = ['TTSEngineManager', 'get_engine_manager']
