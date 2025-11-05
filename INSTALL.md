# Installation Guide

## 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 2. Install FFmpeg (Required for Voice Recording)

### Windows:
```cmd
# Run PowerShell as Administrator
choco install ffmpeg
```

### Mac:
```bash
brew install ffmpeg
```

### Linux:
```bash
sudo apt install ffmpeg
```

## 3. Verify FFmpeg Installation
```bash
ffmpeg -version
```

## 4. Start Server
```bash
python ollama_api_server.py
```

## 5. Access UI
Open http://localhost:8000

## Features Available:
- ✅ Text chat with Ollama
- ✅ Voice responses (TTS)
- ✅ Voice input (with FFmpeg)
- ✅ Voice cloning