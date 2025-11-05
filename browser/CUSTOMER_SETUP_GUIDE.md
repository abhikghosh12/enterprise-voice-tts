# 🚀 Enterprise Voice Browser - Complete Setup Guide for Users

## Welcome!

This guide will help you install and set up Enterprise Voice Browser on your Windows computer.

---

## ⚠️ Important: Two Things to Install

Enterprise Voice Browser requires **two separate installations**:

1. **Ollama** (AI engine - install first)
2. **Enterprise Voice Browser** (this application)

**Why two installs?**
- Ollama is the AI "brain" that runs models
- The browser is the "interface" that talks to Ollama
- They work together but are separate applications

**Installation time**: ~15 minutes total

---

## 📋 System Requirements

### Minimum:
- ✅ Windows 10 or Windows 11
- ✅ 8GB RAM
- ✅ 10GB free disk space
- ✅ Internet connection (for initial setup)

### Recommended:
- ✅ 16GB+ RAM
- ✅ 50GB+ free disk space (for larger AI models)
- ✅ Modern CPU (i5/Ryzen 5 or better)
- ✅ Optional: NVIDIA GPU (for faster AI responses)

---

## 🎯 Complete Installation (3 Steps)

---

## STEP 1: Install Ollama (AI Engine)

### Download Ollama

1. **Visit**: [https://ollama.com/download](https://ollama.com/download)
2. **Click**: "Download for Windows"
3. **Save**: `OllamaSetup.exe` to your Downloads folder
4. **Size**: ~500MB

### Install Ollama

1. **Double-click**: `OllamaSetup.exe`
2. **Allow**: Admin permissions if prompted
3. **Follow**: Installation wizard
4. **Wait**: ~2 minutes for installation
5. **Done**: Ollama is now installed!

### Start Ollama

**Method 1: Automatic (Recommended)**

Ollama usually starts automatically. Check if it's running:
- Look for Ollama icon in system tray (bottom-right, near clock)

**Method 2: Manual**

If Ollama isn't running:

1. **Open PowerShell**:
   - Press `Windows Key + X`
   - Click "Windows PowerShell" or "Terminal"

2. **Type and press Enter**:
   ```powershell
   ollama serve
   ```

3. **Keep this window open** (minimized is fine)

### Download an AI Model

You need at least one AI model. We recommend starting with `llama3.2:1b` (fast and small):

1. **Open a NEW PowerShell window**:
   - Press `Windows Key + X`
   - Click "Windows PowerShell" or "Terminal"

2. **Download a model** (choose one):

   **Recommended for beginners** (fastest, 1.3GB):
   ```powershell
   ollama pull llama3.2:1b
   ```

   **Better quality** (2GB):
   ```powershell
   ollama pull llama3.2
   ```

   **Best quality** (but slower, 5GB):
   ```powershell
   ollama pull deepseek-r1
   ```

3. **Wait**: 2-10 minutes depending on model size

4. **Verify installation**:
   ```powershell
   ollama list
   ```

   You should see your model listed!

### Test Ollama

Quick test to make sure it works:

```powershell
ollama run llama3.2:1b "Say hello"
```

If you see a response, Ollama is working! ✅

---

## STEP 2: Install Enterprise Voice Browser

### Download the Browser

You received a download link from us. Click it to download:
- **File**: `Enterprise Voice Browser Setup 2.0.0.exe`
- **Size**: ~200MB

### Install the Browser

1. **Locate**: Downloaded file (usually in Downloads folder)

2. **Double-click**: `Enterprise Voice Browser Setup 2.0.0.exe`

3. **Windows SmartScreen warning** may appear:
   ```
   Windows protected your PC
   Microsoft Defender SmartScreen prevented...
   ```

   **This is normal!** The app is safe but unsigned.

   **Click**: "More info" → "Run anyway"

4. **Follow installation wizard**:
   - Choose installation folder (default is fine)
   - Select "Create Desktop shortcut" ✅
   - Select "Create Start Menu shortcut" ✅
   - Click "Install"

5. **Wait**: ~1 minute

6. **Click**: "Finish"

7. **Browser launches automatically!** 🎉

---

## STEP 3: Configure and Use

### First Launch Configuration

When the browser opens for the first time:

1. **Check status bar** (bottom-right corner):
   - Look for **"🟢 Ollama"** (green circle)
   - If you see **"⚫ Ollama"** (black circle), continue below

2. **If Ollama shows as disconnected**:

   **Click** the ⚙️ **Settings** button (top-right toolbar)

   **Verify endpoint**: Should be `http://127.0.0.1:11434`

   **Click**: "Test Connection"

   - ✅ **Success**: "Connected! Found X model(s)"
   - ❌ **Failed**: See troubleshooting below

   **Click**: "Save Settings"

   **Close** settings window

3. **Status bar should now show**: "🟢 Ollama" ✅

### Start Using the Browser

1. **Open AI sidebar**:
   - Click the **🤖** button (top-right)

2. **Select AI model**:
   - Click the dropdown (should show your installed models)
   - Select your model (e.g., "llama3.2:1b")

3. **Start chatting**:
   - Type a message: "Hello! Tell me about yourself"
   - Press **Enter** or click **Send**
   - Watch the AI respond in real-time! ✨

4. **Try voice input** (optional):
   - Click **🎤** microphone button
   - Speak your question
   - AI responds automatically

5. **Enable voice output** (optional):
   - Click **🔊** speaker button to toggle
   - AI will speak responses

---

## 🎮 Features to Try

### Web Browsing with AI

1. **Navigate** to any website (use URL bar at top)
2. **Click**: "📄 Summarize Page" to get a summary
3. **Highlight** text and click "💡 Explain Selection"
4. **Click**: "🌐 Translate" for translation

### Voice Chat

1. **Click**: 🎤 microphone
2. **Speak** your question
3. **AI responds** (with voice if 🔊 is enabled)

### Settings

1. **Click**: ⚙️ Settings
2. **Configure**: Ollama endpoint
3. **Test**: Connection
4. **Clear**: Chat history

---

## 🔧 Troubleshooting

### "⚫ Ollama (Not connected)"

**Problem**: Browser can't connect to Ollama

**Solution 1**: Start Ollama
```powershell
ollama serve
```
Keep this window open!

**Solution 2**: Check Ollama is running
- Look for Ollama icon in system tray
- Or open PowerShell and run: `curl http://127.0.0.1:11434/api/tags`

**Solution 3**: Configure endpoint
- Click ⚙️ Settings
- Make sure endpoint is: `http://127.0.0.1:11434`
- Test connection
- Save

### "No models found"

**Problem**: Ollama is connected but no models

**Solution**: Download a model
```powershell
ollama pull llama3.2:1b
```
Then restart browser or click Settings → Test Connection

### "Windows Defender blocked the app"

**Problem**: Windows SmartScreen warning

**Solution**:
1. Click "More info"
2. Click "Run anyway"
3. This is normal for unsigned applications

### "App is slow to respond"

**Possible causes**:

1. **Large model**: Try smaller model (llama3.2:1b)
2. **Low RAM**: Close other applications
3. **CPU busy**: Wait for other tasks to finish

**To use faster model**:
- Click 🤖 AI sidebar
- Select "llama3.2:1b" from dropdown

### "Voice input not working"

**Requirements**:
- Microphone connected
- Internet connection (voice recognition uses online service)
- Microphone permissions granted

**Solution**:
- Check Windows microphone settings
- Grant browser microphone permission

### "Can't find the installed app"

**Location**:
- **Desktop**: Look for shortcut
- **Start Menu**: Search "Enterprise Voice Browser"
- **Installed location**: `C:\Program Files\Enterprise Voice Browser\`

---

## 📊 Understanding the Interface

### Top Toolbar (Left to Right):

- **← → ⟳**: Navigation buttons (back, forward, refresh)
- **🏠**: Home button
- **URL Bar**: Enter web addresses
- **Go**: Navigate to URL
- **🎤**: Voice input
- **🔊**: Toggle voice output
- **⚙️**: Settings
- **🤖**: AI assistant sidebar

### Bottom Status Bar:

- **Left**: Current status (Ready, Loading, etc.)
- **Right**:
  - **🟢 Ollama**: Connected to AI
  - **🟢 Voice**: Voice features available

### AI Sidebar (click 🤖):

- **Model dropdown**: Select AI model
- **Chat area**: Conversation history
- **Input box**: Type messages
- **🎤**: Voice input
- **Send**: Send message
- **Quick actions**: Summarize, Explain, Translate

---

## 💡 Usage Tips

### Best Practices:

1. **Keep Ollama running**: Minimize PowerShell window, don't close
2. **Start with small models**: llama3.2:1b for testing
3. **Upgrade to larger models**: For better responses
4. **Clear history**: If app gets slow (Settings → Clear History)
5. **Use voice features**: Very convenient!

### Model Recommendations:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3.2:1b | 1.3GB | ⚡⚡⚡⚡ | ⭐⭐ | Quick testing |
| llama3.2 | 2GB | ⚡⚡⚡ | ⭐⭐⭐ | Daily use |
| deepseek-r1 | 5GB | ⚡⚡ | ⭐⭐⭐⭐ | Complex tasks |

### Cloud Models (Optional):

For access to massive models without downloading:

```powershell
# Sign in to Ollama Cloud
ollama signin

# Pull cloud models (don't download, run in cloud)
ollama pull gpt-oss:120b-cloud
ollama pull deepseek-v3.1:671b-cloud
```

Then select cloud models in the browser dropdown!

---

## 🆘 Getting Help

### Check These First:

1. **Ollama running?**: Open PowerShell → `ollama serve`
2. **Models downloaded?**: PowerShell → `ollama list`
3. **Connection working?**: Browser Settings → Test Connection
4. **Restart both**: Close browser and Ollama, start again

### Still Need Help?

**Contact**: [Your support email or link]

**Documentation**: [Link to more docs]

**Report Bug**: [Link to issue tracker]

---

## ✅ Quick Start Checklist

After installation, verify:

- [ ] Ollama installed
- [ ] At least one model downloaded
- [ ] Ollama server running (`ollama serve`)
- [ ] Browser installed
- [ ] Browser shows "🟢 Ollama"
- [ ] Can send messages to AI
- [ ] AI responds successfully
- [ ] Voice input works (optional)
- [ ] Voice output works (optional)

---

## 🎉 You're All Set!

**Everything working?** Great!

Now you can:
- ✅ Browse the web with AI assistance
- ✅ Chat with AI models
- ✅ Use voice input/output
- ✅ Summarize web pages
- ✅ Get explanations
- ✅ Translate content

**Enjoy your AI-powered browsing experience!** 🚀

---

## 📝 Quick Reference Commands

### Ollama Commands:

```powershell
# Start Ollama
ollama serve

# List models
ollama list

# Download model
ollama pull llama3.2:1b

# Test model
ollama run llama3.2:1b "Hello"

# Sign in to cloud (optional)
ollama signin

# Download cloud model (optional)
ollama pull gpt-oss:120b-cloud
```

### Windows Commands:

```powershell
# Open PowerShell
Windows Key + X → "Windows PowerShell"

# Check Ollama is running
curl http://127.0.0.1:11434/api/tags
```

---

**Version**: 2.0.0
**Last Updated**: 2025-10-27
**Difficulty**: Beginner-Friendly ✅
