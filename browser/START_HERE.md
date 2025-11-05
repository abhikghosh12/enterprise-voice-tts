# 🚀 START HERE - Enterprise Voice Browser

## The Problem

You're seeing "⚫ Ollama (Not connected)" because either:
1. The browser hasn't started yet
2. Ollama isn't running
3. There's a connection issue

## ✅ Solution (Step by Step)

### Step 1: Make Sure Ollama is Running

**Option A: Check if already running**
Open PowerShell or CMD and run:
```powershell
curl http://localhost:11434/api/tags
```

If you see JSON with models → Ollama is running ✅
If you see error → Continue to Option B

**Option B: Start Ollama**
```powershell
ollama serve
```
**IMPORTANT**: Leave this window open!

### Step 2: Pull a Model (if you haven't)

In a **NEW** PowerShell/CMD window:
```powershell
ollama pull llama3.2:1b
```

This downloads a fast, small model (1.3GB).

### Step 3: Start the Browser

**IMPORTANT**: Don't use Git Bash! Use **PowerShell** or **CMD**.

```powershell
cd C:\git\enterprise-voice-tts\browser
npm start
```

**Or** simply double-click: `start-browser.bat`

### Step 4: Verify Connection

When the browser opens:

1. Look at **bottom-right** status bar
2. You should see: **"🟢 Ollama"**
3. If you see **"⚫ Ollama"**, continue to Step 5

### Step 5: Configure Settings (if needed)

1. Click the **⚙️ Settings** button (top-right toolbar)
2. **Important**: The endpoint should be: `http://127.0.0.1:11434`
   - Use `127.0.0.1` NOT `localhost` (fixes IPv6/IPv4 issues)
3. Click **"Test Connection"**
   - If SUCCESS → Click "Save Settings"
   - If FAILED → See Troubleshooting below
4. Close settings
5. Status bar should now show **"🟢 Ollama"**

### Step 6: Test Chat

1. Click the **🤖** button (top-right) to open AI sidebar
2. Type: "Hello!"
3. Press Enter or click "Send"
4. You should see streaming response!

---

## 🔧 Troubleshooting

### "npm start" gives error about "app"

This happens in Git Bash. **Use PowerShell or CMD instead**:

```powershell
# Open PowerShell (not Git Bash)
cd C:\git\enterprise-voice-tts\browser
npm start
```

### "⚫ Ollama" persists after Steps 1-5

**Check 1**: Is Ollama actually running?
```powershell
curl http://localhost:11434/api/tags
```

**Check 2**: Do you have models?
```powershell
ollama list
```

**Check 3**: Try different endpoint in Settings:
- Try: `http://127.0.0.1:11434`
- Try: `http://[::1]:11434`

**Check 4**: Check Windows Firewall
- Open "Windows Defender Firewall"
- Allow Electron/Node.js through firewall

### Browser won't start at all

```powershell
# Clean install
cd C:\git\enterprise-voice-tts\browser
Remove-Item -Recurse -Force node_modules
npm install
npm start
```

### "No models found" in dropdown

```powershell
ollama pull llama3.2:1b
ollama pull llama3.2
ollama pull mistral
```

Then refresh browser or click Settings → Test Connection.

---

## 🎯 Quick Commands Cheat Sheet

### Terminal 1 (Keep Open):
```powershell
ollama serve
```

### Terminal 2:
```powershell
# Pull models (one time)
ollama pull llama3.2:1b

# Start browser
cd C:\git\enterprise-voice-tts\browser
npm start
```

---

## 📝 What Should Be Running

When everything works, you should have:

1. ✅ **Terminal 1**: Running `ollama serve` (don't close!)
2. ✅ **Browser**: Enterprise Voice Browser window open
3. ✅ **Status**: "🟢 Ollama" in bottom-right
4. ✅ **Models**: Visible in dropdown when AI sidebar open

---

## 🎬 Complete Fresh Start (Nuclear Option)

If nothing works, try this complete reset:

### 1. Stop Everything
- Close the browser
- Press Ctrl+C in the Ollama terminal
- Close all terminals

### 2. Fresh Ollama Start
```powershell
# Terminal 1
ollama serve
```

### 3. Verify Ollama
```powershell
# Terminal 2
curl http://localhost:11434/api/tags
ollama list
```

### 4. Pull Model (if needed)
```powershell
ollama pull llama3.2:1b
```

### 5. Fresh Browser Install
```powershell
cd C:\git\enterprise-voice-tts\browser
Remove-Item -Recurse -Force node_modules
npm install
```

### 6. Start Browser
```powershell
npm start
```

### 7. Configure in Browser
- Open Settings (⚙️)
- Endpoint: `http://localhost:11434`
- Test Connection
- Save Settings

---

## 🆘 Still Stuck?

### Enable Debug Mode

Edit `main.js` line 25:
```javascript
// Change from:
// mainWindow.webContents.openDevTools();

// To:
mainWindow.webContents.openDevTools();
```

Then restart browser and check Console tab for errors.

### Run Diagnostics
```powershell
cd C:\git\enterprise-voice-tts\browser
.\diagnose.bat
```

### Check These Files

Make sure these exist in `C:\git\enterprise-voice-tts\browser\`:
- ✅ `main.js`
- ✅ `renderer.js`
- ✅ `preload.js`
- ✅ `index.html`
- ✅ `styles.css`
- ✅ `package.json`
- ✅ `node_modules/` (folder with many packages)

---

## ✨ Success Checklist

When working properly:

- ✅ Ollama terminal shows "Listening on http://127.0.0.1:11434"
- ✅ Browser opens without errors
- ✅ Status bar shows "🟢 Ollama" (green)
- ✅ Status bar shows "🟢 Voice" (green)
- ✅ AI sidebar has model dropdown with options
- ✅ Can send messages and get responses
- ✅ Streaming text appears smoothly

---

## 📚 Next Steps After It Works

1. **Try Voice Input**: Click 🎤 and speak
2. **Enable Voice Output**: Toggle 🔊 to hear AI responses
3. **Browse with AI**: Visit websites and use quick actions
4. **Experiment with Models**: Try different models from dropdown
5. **Read Full Docs**: Check [QUICKSTART.md](QUICKSTART.md)

---

## 🔗 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Full getting started guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Technical details
- [README.md](README.md) - Original documentation

---

**Last Updated**: 2025-10-27
**Version**: 2.0

**Remember**: The most common issue is running from Git Bash instead of PowerShell/CMD!
