# Enterprise TTS Engines - Technical Documentation

## 🎯 Overview

This directory contains multiple high-performance TTS engines optimized for different use cases:

| Engine | Speed | Quality | Languages | Offline | Best For |
|--------|-------|---------|-----------|---------|----------|
| **Piper** | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 40+ | ✅ | Ultra-low latency, real-time |
| **Silero** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 5 | ✅ | Fast CPU inference |
| **Edge TTS** | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 100+ | ❌ | High quality, many voices |
| **Coqui XTTS** | ⚡⚡ | ⭐⭐⭐⭐⭐ | 13 | ✅ | Voice cloning, best quality |

## 📊 Performance Benchmarks

### Latency Tests (100-word text)

```
Piper TTS:      0.3s - 0.8s   (CPU)
Silero TTS:     0.5s - 1.2s   (CPU)
Edge TTS:       1.5s - 3.0s   (Network)
Coqui XTTS:     2.0s - 4.0s   (CPU), 0.5s - 1.5s (GPU)
```

### Real-Time Factor (RTF)

Lower is better (< 1.0 means faster than real-time)

```
Piper:          RTF 0.1 - 0.3   ⚡ Fastest
Silero:         RTF 0.2 - 0.4
Edge TTS:       RTF 0.5 - 1.0
Coqui XTTS:     RTF 0.3 - 0.6 (GPU), 1.0 - 2.0 (CPU)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd tts-engines
pip install -r requirements.txt
```

### 2. Run Worker

```bash
# Set Redis connection
export REDIS_URL=redis://localhost:6379

# Start worker
python tts_worker.py
```

### 3. Test Engines

```python
from engine_manager import get_engine_manager
import asyncio

async def test():
    manager = get_engine_manager()
    await manager.initialize_engines(["piper", "edge", "coqui"])
    
    # Synthesize with auto engine selection
    result = await manager.synthesize(
        text="Hello, this is a test of the TTS system.",
        voice_id="en-US-GuyNeural",
        output_path="./output/test.mp3",
        engine="auto"
    )
    
    print(f"Generated in {result['duration']:.2f}s")
    print(f"Engine used: {result['engine']}")

asyncio.run(test())
```

## 🎙️ Engine Details

### Piper TTS (Recommended for Low Latency)

**Features:**
- Ultra-fast ONNX inference
- 40+ voices in 15+ languages
- Runs on CPU with <1s latency
- Small model sizes (20-50MB)

**Usage:**
```python
from piper_engine import PiperTTSEngine

engine = PiperTTSEngine("./models_cache")
result = await engine.synthesize(
    text="Fast and efficient speech synthesis",
    voice_id="en-US-lessac-medium",
    output_path="./output/piper.wav"
)
```

**Available Voices:**
- `en-US-lessac-medium` - US Male (Morgan Freeman-like)
- `en-US-libritts-high` - US Female 
- `en-GB-alan-medium` - UK Male
- And 30+ more languages

**Optimization Tips:**
- Use `medium` quality for fastest speed
- Use `high` quality for better quality (still fast!)
- Models are cached after first download

---

### Silero TTS (Best for Russian)

**Features:**
- Fast CPU inference
- Excellent Russian voices
- Single model for multiple speakers
- Very lightweight (40MB)

**Usage:**
```python
from silero_engine import SileroTTSEngine

engine = SileroTTSEngine("./models_cache")
result = await engine.synthesize(
    text="Быстрый и качественный синтез речи",
    voice_id="ru-RU-aidar",
    output_path="./output/silero.wav"
)
```

**Available Voices:**
- Russian: aidar, baya, kseniya, xenia
- English: lj (female)

**Optimization Tips:**
- Use 48kHz for best quality
- Cache model in memory for repeat syntheses
- Very efficient on CPU

---

### Edge TTS (Most Voices)

**Features:**
- 200+ voices
- 100+ languages and dialects
- High quality
- Free to use

**Usage:**
```python
from edge_engine import EdgeTTSEngine

engine = EdgeTTSEngine()
result = await engine.synthesize(
    text="High quality speech in many languages",
    voice_id="en-US-GuyNeural",
    output_path="./output/edge.mp3"
)
```

**Popular Voices:**
- `en-US-GuyNeural` - US Male (deep voice)
- `en-GB-RyanNeural` - UK Male (David Attenborough-like)
- `hi-IN-MadhurNeural` - Hindi Male
- `de-DE-ConradNeural` - German Male
- And 200+ more...

**Limitations:**
- Requires internet connection
- Slightly higher latency (1-3s)
- Rate limiting possible

---

### Coqui XTTS-v2 (Best Quality)

**Features:**
- State-of-the-art quality
- Voice cloning from 6-second samples
- 13 languages supported
- Emotion and style control

**Usage:**
```python
from coqui_engine import CoquiTTSEngine

engine = CoquiTTSEngine("./models_cache")

# Standard synthesis
result = await engine.synthesize(
    text="The highest quality text-to-speech available",
    voice_id="en-XTTS",
    output_path="./output/xtts.wav"
)

# Voice cloning
result = await engine.clone_voice(
    text="This will sound like the target speaker",
    speaker_audio_path="./speaker_sample.wav",
    output_path="./output/cloned.wav",
    language="en"
)
```

**Supported Languages:**
- English, Spanish, French, German, Italian
- Portuguese, Polish, Turkish, Russian, Dutch
- Czech, Arabic, Chinese (Mandarin)

**Hardware Requirements:**
- CPU: 4-8GB RAM, 2-4s per sentence
- GPU: 2GB VRAM, <1s per sentence

**Optimization Tips:**
- Use GPU for best performance
- Preload model to avoid startup time
- Batch process multiple texts

---

## 🔧 Advanced Configuration

### Engine Selection Strategy

The `engine_manager.py` automatically selects the best engine based on:

1. **Text length**
   - Short (<100 chars): Piper (fastest)
   - Medium (100-1000): Auto-select based on voice
   - Long (>1000): Consider splitting

2. **Language**
   - English: Piper or Coqui
   - Russian: Silero
   - Other languages: Edge TTS

3. **Quality requirements**
   - Ultra-low latency: Piper
   - High quality: Coqui XTTS
   - Balance: Edge TTS or Silero

### Custom Engine Selection

```python
# Force specific engine
result = await manager.synthesize(
    text="Important announcement",
    voice_id="en-US-GuyNeural",
    output_path="output.wav",
    engine="coqui"  # Force Coqui for best quality
)
```

### Preloading Models

```python
# Preload models for faster first synthesis
await manager.preload_models([
    "en-US-GuyNeural",
    "hi-IN-MadhurNeural",
    "de-DE-ConradNeural"
])
```

### Batch Processing

```python
# Process multiple texts efficiently
texts = [
    ("Hello world", "en-US-GuyNeural"),
    ("Bonjour le monde", "fr-FR-HenriNeural"),
    ("Hola mundo", "es-ES-AlvaroNeural")
]

tasks = []
for i, (text, voice) in enumerate(texts):
    task = manager.synthesize(
        text=text,
        voice_id=voice,
        output_path=f"./output/batch_{i}.wav",
        engine="auto"
    )
    tasks.append(task)

results = await asyncio.gather(*tasks)
```

## 🐛 Troubleshooting

### Model Download Issues

```python
# Manually download Piper model
import urllib.request
url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
urllib.request.urlretrieve(url, "./models_cache/piper/en-US-lessac-medium.onnx")
```

### Memory Issues

```python
# Clear model cache
del engine_manager.engines["coqui"]
import gc
gc.collect()
torch.cuda.empty_cache()  # If using GPU
```

### Slow Performance

1. **Use Piper for speed:**
   ```python
   manager.synthesize(text, voice, output, engine="piper")
   ```

2. **Enable GPU for Coqui:**
   ```bash
   # Install CUDA-enabled PyTorch
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Reduce sample rate:**
   ```python
   manager.synthesize(text, voice, output, sample_rate=16000)
   ```

## 📈 Production Deployment

### Scaling Workers

```bash
# Run multiple workers in parallel
for i in {1..4}; do
    python tts_worker.py &
done
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose-enhanced.yml up -d --scale tts-worker=4
```

### Monitoring

```python
# Get engine statistics
stats = manager.get_engine_stats()
print(f"Engines: {stats['engines_loaded']}")
print(f"Models cached: {stats['models_cached']}")
```

## 📚 API Reference

See [API.md](../docs/API.md) for complete API documentation.

## 🤝 Contributing

To add a new TTS engine:

1. Create `new_engine.py` implementing the interface:
   ```python
   async def synthesize(text, voice_id, output_path, **kwargs)
   async def preload_model(voice_id)
   def get_voices()
   ```

2. Register in `engine_manager.py`

3. Add tests and documentation

## 📄 License

MIT License - see LICENSE file

---

**Built with ❤️ for Enterprise Voice Applications**
