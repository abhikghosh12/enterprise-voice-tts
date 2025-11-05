# 🎙️ Enterprise Voice TTS Platform

**Production-ready, ultra-low latency text-to-speech platform with voice recording and AI chat.**

## ⚡ Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg** (for voice recording):
   ```bash
   # Windows (run as Administrator)
   choco install ffmpeg
   
   # Mac
   brew install ffmpeg
   
   # Linux  
   sudo apt install ffmpeg
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ollama pull llama3.2:1b
   ```

4. **Start Server**:
   ```bash
   python ollama_api_server.py
   ```

5. **Open UI**: http://localhost:8000

## 🎯 Features

- **Voice Chat**: Record voice → AI responds with voice
- **Multiple TTS Engines**: Google TTS, Edge TTS, System TTS
- **Voice Cloning**: Upload voice samples for custom voices
- **Fast Models**: Optimized for llama3.2:1b (sub-second responses)
- **100% Local**: No cloud dependencies (except Google TTS)

## 📁 Key Files

- `ollama_api_server.py` - Main server
- `public/voice-ui.html` - Web interface
- `simple_tts.py` - TTS engine manager
- `requirements.txt` - Dependencies
- `INSTALL.md` - Setup guide

## 🔧 Configuration

Edit settings in the web UI:
- **Model**: llama3.2:1b (fastest) or others
- **TTS Engine**: Google TTS (recommended)
- **Voice**: Choose from 40+ voices

## 📞 Voice AI Contact Center

See `voice-ai-agent/` for Twilio integration and phone-based AI assistant.

## 🐳 Docker

```bash
docker-compose up -d
```

## 📄 License

MIT License - see LICENSE file.