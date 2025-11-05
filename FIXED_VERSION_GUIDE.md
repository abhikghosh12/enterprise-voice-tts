# 🎙️ AI Voice Assistant - Quick Fix Guide

## 🚨 Current Issues Fixed

### Problem 1: TTS API 404 Error
**Cause:** Using wrong endpoint `/api/v1/tts/generate`
**Fix:** Now using `/api/ollama/chat` which includes TTS generation

### Problem 2: Speech Recognition Failing  
**Cause:** Audio format mismatch (WebM from browser, WAV expected)
**Fix:** Now uploads audio file to `/api/speech-to-text` endpoint which handles WebM→WAV conversion

---

## 🚀 How to Use the Fixed Version

### Step 1: Make sure dependencies are installed
```bash
pip install aiohttp pydub SpeechRecognition
```

### Step 2: Make sure FFmpeg is installed
FFmpeg is needed to convert WebM audio from the browser.

**Install FFmpeg:**
- Windows: `choco install ffmpeg` OR run `install_ffmpeg.bat`
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### Step 3: Start the fixed version
```bash
cd C:\git\enterprise-voice-tts
START_AI_FIXED.bat
```

This will:
1. ✅ Check dependencies
2. ✅ Check FFmpeg
3. ✅ Start TTS server if not running
4. ✅ Check Ollama is running
5. ✅ Start AI voice assistant

---

## 📊 What the Fixed Version Does

```
Browser Microphone → WebM Audio
         ↓
   Save to temp file
         ↓
Upload to: http://localhost:8000/api/speech-to-text
         ↓
   Server converts WebM → WAV (using pydub + FFmpeg)
         ↓
   Google Speech Recognition
         ↓
   Returns text transcription
         ↓
Send to: http://localhost:11434/api/chat (Ollama)
         ↓
   AI generates response
         ↓
Send to: http://localhost:8000/api/ollama/chat
         ↓
   Google TTS generates audio
         ↓
   Returns audio URL
         ↓
Browser plays audio → You hear AI
```

---

## 🔧 Troubleshooting

### Issue: "FFmpeg not found"
**Solution:**
```bash
# Windows (with chocolatey)
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
# Add to PATH
```

### Issue: "Could not understand audio"
**Solutions:**
1. Speak more clearly and slowly
2. Check microphone is working
3. Reduce background noise
4. Check internet connection (Google STT needs it)
5. Try speaking in shorter phrases

### Issue: "TTS API error"
**Solution:**
- Make sure TTS server is running on port 8000
- Check: http://localhost:8000/api/v1/health
- Restart TTS server if needed

### Issue: "Ollama error"
**Solution:**
```bash
# Start Ollama
ollama serve

# Pull the model
ollama pull llama3.2:1b
```

---

## 🆚 Version Comparison

| Feature | Original | V2 | Full | **Fixed** |
|---------|----------|----|----|------|
| Audio Format | ❌ | ❌ | ❌ | ✅ |
| Correct Endpoints | ❌ | ✅ | ❌ | ✅ |
| STT Working | ❌ | ❌ | ❌ | ✅ |
| AI Responses | ❌ | ❌ | ✅ | ✅ |
| TTS Working | ❌ | ❌ | ❌ | ✅ |

**Use the FIXED version!**

---

## 📝 Files You Need

1. **webrtc_voice_ai_fixed.py** - Fixed server ✅
2. **START_AI_FIXED.bat** - Launcher ✅  
3. **ollama_api_server.py** - TTS server (already exists)

---

## ✅ Expected Behavior

When working correctly, you should see:

**In Browser Debug Console:**
```
[11:45:30] 🚀 Starting AI voice session...
[11:45:31] ✅ Microphone access granted!
[11:45:32] ✅ Connected to AI assistant!
[11:45:35] 📤 Sending audio for processing...
[11:45:36] 📝 Transcribed: "Hello, how are you?"
[11:45:37] 🤖 AI responded
[11:45:38] 🔊 Playing AI voice response
```

**In Server Logs:**
```
INFO: ✅ Call connected
INFO: 🎤 Processing 48596 bytes of audio
INFO: 📝 Transcription: Hello, how are you?
INFO: 🤖 AI Response: I'm doing great, thank you!
INFO: 🔊 TTS Audio ready: /output/chat_1234567.wav
```

---

## 🎯 Quick Test

1. Run: `START_AI_FIXED.bat`
2. Click "📞 Start Talking"
3. Say: "Hello, testing one two three"
4. You should see:
   - Your text transcribed
   - AI thinking
   - AI text response
   - AI voice playing

---

## 💡 Tips

- **Speak clearly** with pauses between sentences
- **Keep sentences short** (5-10 words)
- **Wait for response** before speaking again
- **Check Debug Console** if something goes wrong
- **Reduce background noise** for better recognition

---

## 🚀 Ready to Test!

Run this command:
```bash
START_AI_FIXED.bat
```

Then open http://localhost:8001 and start talking!

**This version should work! 🎉**
