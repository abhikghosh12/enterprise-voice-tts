# Quick Start Guide - Ollama-Powered Browser

Get up and running with the Enterprise Voice Browser in 5 minutes!

## Prerequisites

1. **Node.js** (v16+): [Download](https://nodejs.org/)
2. **Ollama**: [Download](https://ollama.ai/)

## Installation

### Step 1: Install Ollama

**Windows**:
```powershell
# Download from https://ollama.ai/download
# Run the installer
```

**macOS**:
```bash
brew install ollama
```

**Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Start Ollama & Pull a Model

```bash
# Start Ollama service
ollama serve

# In a new terminal, pull a fast model
ollama pull llama3.2

# Or pull other models
ollama pull mistral
ollama pull codellama
ollama pull llama3.2:1b  # Smallest/fastest
```

### Step 3: Install Browser Dependencies

```bash
cd C:\git\enterprise-voice-tts\browser
npm install
```

### Step 4: Start the Browser

```bash
npm start
```

## First Use

1. **The browser will open** with Google as the homepage
2. **Click the 🤖 button** in the top-right to open the AI assistant
3. **Check the status bar** at the bottom:
   - 🟢 Ollama = Connected
   - ⚫ Ollama = Not connected
4. **Try a message**: "Hello! Tell me about yourself"
5. **Watch the AI respond** with streaming text

## Features to Try

### 1. Web Browsing with AI
- Navigate to any website
- Click **📄 Summarize Page** to get a summary
- Select text and click **💡 Explain Selection**

### 2. Voice Input
- Click the **🎤** microphone button
- Speak your message
- The AI will respond (and speak back if 🔊 is enabled)

### 3. Settings Configuration
- Click the **⚙️** settings button
- Change the Ollama endpoint if needed
- Test connection
- Clear chat history

### 4. Conversation Context
The AI now remembers your entire conversation! Try:
```
You: "My favorite color is blue"
AI: "That's nice! Blue is a calming color..."
You: "What's my favorite color?"
AI: "Your favorite color is blue!"
```

## Troubleshooting

### "⚫ Ollama (Not connected)"

**Check if Ollama is running**:
```bash
ollama serve
```

**Check if models are installed**:
```bash
ollama list
```

**Test the API**:
```bash
curl http://localhost:11434/api/tags
```

### "No models found"

Pull at least one model:
```bash
ollama pull llama3.2
```

Refresh the browser or click Settings → Test Connection.

### Browser won't start

```bash
# Clear node_modules and reinstall
cd C:\git\enterprise-voice-tts\browser
rm -rf node_modules
npm install
npm start
```

### Voice input not working

- Voice input requires an internet connection (uses browser's Web Speech API)
- Check microphone permissions
- Only works in Chromium-based browsers (Electron uses Chromium)

### Slow responses

Try a smaller/faster model:
```bash
ollama pull llama3.2:1b  # 1 billion parameters = much faster
```

Then select it from the dropdown in the AI sidebar.

## Remote Ollama Setup

If Ollama is running on another machine:

1. Start Ollama on the remote machine with network access:
   ```bash
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```

2. In the browser, click **⚙️ Settings**
3. Enter: `http://192.168.1.100:11434` (replace with your server IP)
4. Click **Test Connection**
5. Click **Save Settings**

## Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| llama3.2:1b | 1.3GB | ⚡⚡⚡ | ⭐⭐ | Fast responses, simple tasks |
| llama3.2 | 2GB | ⚡⚡ | ⭐⭐⭐ | Balanced (recommended) |
| mistral | 4GB | ⚡ | ⭐⭐⭐⭐ | High quality, slower |
| codellama | 7GB | ⚡ | ⭐⭐⭐⭐ | Code-focused |

Pull with:
```bash
ollama pull <model-name>
```

## Usage Tips

### 1. Context Window
The browser sends your full conversation history to Ollama. Long conversations may:
- Take longer to process
- Use more memory
- Hit model context limits

**Solution**: Click Settings → Clear Chat History to start fresh.

### 2. Quick Actions

**Summarize Page**:
- Navigate to any article
- Click "📄 Summarize Page"
- Get a quick summary

**Explain Selection**:
- Highlight any text on a webpage
- Click "💡 Explain Selection"
- AI explains the selected text

**Translate**:
- Navigate to foreign language page
- Click "🌐 Translate"
- AI translates to English

### 3. Voice Chat

Best practices:
- Speak clearly and pause after finishing
- The AI will automatically respond when you stop speaking
- Toggle 🔊 to enable/disable AI voice responses

## Building for Distribution

### Windows:
```bash
npm run build:win
```
Creates installer in `dist/` folder.

### macOS:
```bash
npm run build:mac
```

### Linux:
```bash
npm run build:linux
```

## What's New in v2.0

✅ **Fixed critical security vulnerability** (sandbox enabled)
✅ **Conversation context now works** (AI remembers chat history)
✅ **Configurable Ollama endpoint** (connect to remote servers)
✅ **Improved performance** (batched streaming updates)
✅ **Settings UI** (configure endpoint, test connection, clear history)
✅ **Input validation** (sanitized inputs for security)
✅ **Better error handling** (detailed error messages)

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for full details.

## Support & Documentation

- **Full README**: [README.md](README.md)
- **Improvements**: [IMPROVEMENTS.md](IMPROVEMENTS.md)
- **Windows Install**: [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)
- **App Store Guide**: [APP_STORE_GUIDE.md](APP_STORE_GUIDE.md)

## Next Steps

1. ✅ Browse the web with AI assistance
2. ✅ Try voice input and output
3. ✅ Experiment with different Ollama models
4. ✅ Configure settings for your use case
5. ✅ Build and distribute your customized browser

Enjoy your AI-powered browsing experience! 🚀
