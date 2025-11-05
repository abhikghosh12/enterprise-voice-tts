# Enterprise Voice Browser

An AI-powered desktop browser with Ollama integration and voice capabilities built with Electron.

## Features

- 🌐 **Full Web Browser** - Browse the web with standard navigation controls
- 🤖 **AI Assistant** - Integrated Ollama LLM support with multiple models
- 🎤 **Voice Input** - Speech-to-text for hands-free interaction
- 🔊 **Text-to-Speech** - AI responses spoken aloud
- 📄 **Quick Actions** - Summarize pages, explain selections, translate content
- 🎨 **Modern UI** - Dark theme with smooth animations
- 💬 **Chat Interface** - Natural conversation with AI while browsing

## Prerequisites

1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/

2. **Ollama** (for local LLM)
   - Download from: https://ollama.ai/
   - After installation, pull a model:
     ```bash
     ollama pull llama3.2
     ```

## Installation

### Option 1: Automatic Setup (Windows PowerShell)

1. Copy the entire project folder to `C:\git\enterprise-voice-tts`
2. Open PowerShell as Administrator
3. Navigate to the project folder:
   ```powershell
   cd C:\git\enterprise-voice-tts
   ```
4. Run the setup script:
   ```powershell
   .\setup.ps1
   ```

### Option 2: Manual Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the application:
   ```bash
   npm start
   ```

## Building the Application

### For Windows:
```bash
npm run build:win
```

This creates an installer in the `dist` folder.

### For Mac:
```bash
npm run build:mac
```

### For Linux:
```bash
npm run build:linux
```

## Usage

### Basic Navigation
- Use the URL bar to navigate to websites
- Use navigation buttons (back, forward, refresh, home)
- Press Enter in the URL bar to navigate

### AI Assistant
1. Click the 🤖 button to open the AI sidebar
2. Type your message or click 🎤 for voice input
3. Press Send or Enter to chat with the AI
4. Select different models from the dropdown

### Voice Features
- **Voice Input**: Click 🎤 to start voice recognition
- **Speech Output**: Click 🔊 to toggle AI voice responses
- The browser will speak AI responses when enabled

### Quick Actions
- **Summarize Page**: Get a summary of the current webpage
- **Explain Selection**: Highlight text and click to get an explanation
- **Translate**: Translate the page content

## Configuration

### Changing Ollama Host
If Ollama is running on a different machine or port, edit `main.js`:

```javascript
// Change this line (around line 35)
const response = await axios.post('http://localhost:11434/api/chat', {
```

### Adding More Models
1. Pull models with Ollama:
   ```bash
   ollama pull mistral
   ollama pull codellama
   ollama pull neural-chat
   ```
2. Models will automatically appear in the dropdown

### Custom Styling
Edit `styles.css` to customize colors and appearance.

## Troubleshooting

### Ollama Not Connected
- Make sure Ollama is running: `ollama serve`
- Check if you can access: http://localhost:11434
- Verify models are installed: `ollama list`

### Voice Input Not Working
- Check browser permissions for microphone
- Voice recognition requires an internet connection (uses browser API)
- Only supported in Chromium-based Electron

### Build Errors
- Clear node_modules and reinstall:
  ```bash
  rm -rf node_modules
  npm install
  ```
- Make sure you have the latest Node.js version

## Development

### Project Structure
```
enterprise-voice-tts/
├── main.js           # Electron main process
├── preload.js        # Secure IPC bridge
├── renderer.js       # UI logic and event handlers
├── index.html        # Main HTML structure
├── styles.css        # Styling
├── package.json      # Dependencies and build config
└── README.md         # This file
```

### Development Mode
```bash
npm start
```

This opens DevTools automatically for debugging.

## Publishing to Stores

### Microsoft Store (Windows)
1. Build the app: `npm run build:win`
2. Create a Microsoft Partner Center account
3. Submit the `.appx` file from `dist/`

### Mac App Store
1. Build the app: `npm run build:mac`
2. Create an Apple Developer account ($99/year)
3. Sign the app with your certificates
4. Submit via App Store Connect

### Google Play Store (Android)
This Electron app is for **desktop only**. For Android, you need to:
1. Rebuild using **React Native** or **Flutter**
2. Use Capacitor to wrap the web version
3. Or use **Cordova** to package as a hybrid app

## License

MIT License - feel free to use and modify!

## Credits

Built with:
- Electron
- Ollama
- Web Speech API

## Support

For issues and questions, please open an issue on the repository.
