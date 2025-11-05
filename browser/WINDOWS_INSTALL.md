# Windows Installation Instructions

## Quick Start

1. **Copy all files to Windows**
   - Copy the entire `enterprise-voice-tts` folder to `C:\git\enterprise-voice-tts`
   - Or any location you prefer

2. **Install Prerequisites**
   - Install Node.js from https://nodejs.org/ (v16 or higher)
   - Install Ollama from https://ollama.ai/
   - Pull a model: Open Command Prompt and run `ollama pull llama3.2`

3. **Run the Setup**
   
   **Option A: PowerShell (Recommended)**
   - Right-click on `setup.ps1`
   - Select "Run with PowerShell"
   - If you get an execution policy error, run PowerShell as Administrator and execute:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

   **Option B: Manual Setup**
   - Double-click `start.bat` to install dependencies and run the app

4. **Building the App**
   - Double-click `build.bat` to create a Windows installer
   - The installer will be in the `dist` folder

## Copying Files from Linux to Windows

If you're copying from a Linux machine or WSL:

### Using WSL:
```bash
cp -r /home/claude/enterprise-voice-tts /mnt/c/git/
```

### Using SCP (from Linux to Windows):
```bash
scp -r /home/claude/enterprise-voice-tts username@windows-pc:/c/git/
```

### Using Shared Folder:
- Share the folder from Linux
- Access it from Windows and copy to `C:\git\`

### Using GitHub:
1. On Linux:
   ```bash
   cd /home/claude/enterprise-voice-tts
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/enterprise-voice-tts.git
   git push -u origin main
   ```

2. On Windows:
   ```powershell
   cd C:\git
   git clone https://github.com/yourusername/enterprise-voice-tts.git
   ```

## Troubleshooting

### PowerShell Scripts Won't Run
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Node Not Found
- Restart your terminal after installing Node.js
- Or add Node.js to your PATH manually

### Ollama Connection Issues
- Make sure Ollama is running: `ollama serve`
- Check http://localhost:11434 in your browser
- Try restarting Ollama

### Build Errors
- Delete `node_modules` folder
- Delete `package-lock.json`
- Run `npm install` again

## What Each File Does

- `package.json` - Project configuration and dependencies
- `main.js` - Electron main process (backend)
- `preload.js` - Secure bridge between frontend and backend
- `renderer.js` - Frontend JavaScript logic
- `index.html` - Main HTML structure
- `styles.css` - All styling
- `setup.ps1` - Automated setup script for PowerShell
- `start.bat` - Quick start script
- `build.bat` - Build the Windows installer
- `README.md` - Full documentation

## Next Steps

After installation:
1. Start the app with `npm start` or `start.bat`
2. Click the 🤖 button to open AI assistant
3. Try voice input with the 🎤 button
4. Browse and chat with AI simultaneously!

## Building for Distribution

To create an installer for others:
```powershell
npm run build:win
```

The installer will be in `dist/Enterprise Voice Browser Setup.exe`

You can distribute this to other users who won't need Node.js or npm installed.
