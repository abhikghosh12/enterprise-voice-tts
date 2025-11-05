# ⚡ Quick Reference Card

## 🏃 Quick Start Commands

### First Time Setup:
```powershell
# On Windows
cd C:\git\enterprise-voice-tts
.\setup.ps1
```

### Run the App:
```bash
npm start
# or double-click start.bat
```

### Build Installer:
```bash
npm run build:win    # Windows
npm run build:mac    # macOS
npm run build:linux  # Linux
# or double-click build.bat on Windows
```

## ⌨️ Keyboard Shortcuts

- `Enter` in URL bar → Navigate
- `Shift+Enter` in chat → New line
- `Enter` in chat → Send message
- `Ctrl+R` → Refresh page

## 🎤 Using Voice Features

1. Click 🎤 button
2. Speak your message
3. Wait for "Listening..." indicator
4. Message auto-sends when you stop

## 🤖 AI Assistant Tips

**Quick Actions:**
- 📄 Summarize Page - Get page summary
- 💡 Explain Selection - Highlight text first
- 🌐 Translate - Translate page

**Best Prompts:**
- "Summarize this article"
- "Explain quantum computing in simple terms"
- "What are the main points on this page?"
- "Translate this to Spanish"

## 🔧 Ollama Commands

```bash
ollama serve              # Start Ollama
ollama pull llama3.2      # Download model
ollama pull mistral       # Download another model
ollama list               # Show installed models
ollama rm llama3.2        # Remove model
```

## 📁 Important Files

- `setup.ps1` - First-time setup
- `start.bat` - Quick start
- `build.bat` - Build installer
- `README.md` - Full docs
- `package.json` - Configuration

## 🐛 Quick Fixes

**Ollama Not Connected:**
```bash
ollama serve
```

**Voice Not Working:**
- Check mic permissions
- Requires internet connection

**Build Failed:**
```bash
rm -rf node_modules
npm install
```

**Port Already in Use:**
```bash
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## 📊 Model Recommendations

**Fast & Light:**
- `llama3.2` (2GB)
- `phi3` (2.3GB)

**Balanced:**
- `llama3.1` (8GB)
- `mistral` (4GB)

**Best Quality:**
- `llama3.1:70b` (requires 32GB+ RAM)
- `mixtral` (26GB)

## 🌐 Useful URLs

- Ollama Models: https://ollama.ai/library
- Node.js: https://nodejs.org/
- Electron Docs: https://electronjs.org/
- Project Issues: [Your GitHub repo]

## 💾 File Locations

**Windows:**
- Project: `C:\git\enterprise-voice-tts`
- Build output: `C:\git\enterprise-voice-tts\dist`
- Ollama models: `C:\Users\<You>\.ollama\models`

**Linux:**
- Project: `/home/claude/enterprise-voice-tts`
- Build output: `./dist`
- Ollama models: `~/.ollama/models`

## 🎯 First-Time Checklist

- [ ] Install Node.js
- [ ] Install Ollama
- [ ] Pull at least one model: `ollama pull llama3.2`
- [ ] Start Ollama: `ollama serve`
- [ ] Run setup: `.\setup.ps1` or `npm install`
- [ ] Start app: `npm start`
- [ ] Test voice input
- [ ] Test AI chat
- [ ] Try quick actions

## 📞 Getting Help

1. Read `README.md`
2. Check `WINDOWS_INSTALL.md`
3. Review `APP_STORE_GUIDE.md`
4. Check Ollama logs
5. Check browser console (F12)

---

**Keep this file handy for quick reference!**
