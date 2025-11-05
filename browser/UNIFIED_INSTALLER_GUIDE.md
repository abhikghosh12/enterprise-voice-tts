# 🚀 Unified Windows Installer Guide

## Overview

This guide shows you how to create a **unified Windows installer** that installs both:
1. **Enterprise Voice Browser** - Your Electron-based AI browser
2. **Ollama** - The AI engine required for the browser to work

## 🎯 What You'll Get

After building, you'll have a single installer:

**File**: `Enterprise-Voice-Browser-Setup-2.0.0.exe`

### Features:
- ✅ Installs Enterprise Voice Browser
- ✅ Automatically downloads and installs Ollama (if not already installed)
- ✅ Creates desktop shortcut
- ✅ Creates Start Menu entries
- ✅ Includes proper uninstaller
- ✅ Professional installation wizard
- ✅ Smart detection of existing Ollama installation

### User Experience:
1. User downloads one `.exe` file
2. User runs installer
3. Installer checks for Ollama
4. If Ollama is missing, installer downloads and installs it
5. Browser is installed
6. Shortcuts are created
7. Done! User just needs to download a model

## 📋 Prerequisites

### Required Software:

1. **Node.js** (v16 or higher)
   - Download: https://nodejs.org/
   - Check: `node --version`

2. **NSIS** (Nullsoft Scriptable Install System)
   - **Option 1** (Recommended): `winget install NSIS.NSIS`
   - **Option 2**: `choco install nsis`
   - **Option 3**: Download from https://nsis.sourceforge.io/Download
   - Check: `makensis /VERSION`

3. **npm** (comes with Node.js)
   - Check: `npm --version`

### Optional:
- **PowerShell** (for setup script)
- **Git** (if you want to commit changes)

## 🚀 Quick Start

### Method 1: Automated Setup + Build (Easiest!)

1. **Open PowerShell** in the browser directory:
   ```powershell
   cd C:\path\to\enterprise-voice-tts\browser
   ```

2. **Run setup script**:
   ```powershell
   .\setup-installer-build.ps1
   ```
   This will check prerequisites and install NSIS if needed.

3. **Build the installer**:
   ```powershell
   .\build-unified-installer.bat
   ```

4. **Wait** 5-15 minutes (first build downloads Electron runtime)

5. **Done!** Your installer is ready: `Enterprise-Voice-Browser-Setup-2.0.0.exe`

### Method 2: Manual Build

1. **Install prerequisites** (Node.js, NSIS)

2. **Navigate to browser directory**:
   ```powershell
   cd C:\path\to\enterprise-voice-tts\browser
   ```

3. **Install npm dependencies**:
   ```powershell
   npm install
   ```

4. **Build Electron app**:
   ```powershell
   npm run build:win
   ```

5. **Create LICENSE.txt** (if it doesn't exist):
   ```powershell
   echo MIT License > LICENSE.txt
   ```

6. **Build installer with NSIS**:
   ```powershell
   makensis installer.nsi
   ```

7. **Done!** Your installer is created.

## 📦 What Gets Built

### Build Process:

```
[1/7] Check Node.js          ✓
[2/7] Check NSIS             ✓
[3/7] Install dependencies   ✓ (npm install)
[4/7] Create icon            ✓
[5/7] Create LICENSE         ✓
[6/7] Build Electron app     ✓ (5-10 min)
[7/7] Build NSIS installer   ✓ (1-2 min)
```

### Output Files:

```
browser/
├── Enterprise-Voice-Browser-Setup-2.0.0.exe  ← Main installer (~200-250MB)
├── dist/
│   ├── win-unpacked/                         ← Electron build output
│   ├── Enterprise Voice Browser Setup 2.0.0.exe  ← Electron's installer
│   └── ...
└── ...
```

The **unified installer** is: `Enterprise-Voice-Browser-Setup-2.0.0.exe` (in root of browser folder)

## 🎮 How the Installer Works

### Installation Flow:

1. **Welcome Screen**
   - Shows welcome message
   - Explains that both browser and Ollama will be installed

2. **License Agreement**
   - Shows MIT license

3. **Choose Install Location**
   - Default: `C:\Program Files\Enterprise Voice Browser`
   - User can change if desired

4. **Ollama Check**
   - Installer checks if Ollama is already installed
   - **If found**: Skips Ollama installation
   - **If not found**: Prompts user to download/install Ollama

5. **Ollama Installation** (if needed)
   - Downloads Ollama installer (~500MB)
   - Runs Ollama installation wizard
   - User follows Ollama wizard
   - Returns to browser installation

6. **Browser Installation**
   - Copies browser files
   - Creates shortcuts
   - Creates Start Menu entries
   - Registers uninstaller

7. **Finish**
   - Shows completion message
   - Option to launch browser
   - Shows README with next steps

### User Instructions (Included in README):

After installation, users need to:
1. Make sure Ollama is running
2. Download an AI model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Launch Enterprise Voice Browser

## 🔧 Customization

### Change Product Name

Edit `installer.nsi`:
```nsis
!define PRODUCT_NAME "Your Custom Name"
```

### Change Version

Edit `installer.nsi`:
```nsis
!define PRODUCT_VERSION "2.1.0"
```

And `package.json`:
```json
{
  "version": "2.1.0"
}
```

### Change Publisher Name

Edit `installer.nsi`:
```nsis
!define PRODUCT_PUBLISHER "Your Company Name"
```

### Change Icon

1. Replace `icon.png` with your icon (256x256 or 512x512)
2. Rebuild

### Change Website URL

Edit `installer.nsi`:
```nsis
!define PRODUCT_WEB_SITE "https://yourwebsite.com"
```

## 📊 File Sizes

| Component | Size | Notes |
|-----------|------|-------|
| **Unified Installer** | ~200-250MB | Everything needed for installation |
| **Installed Browser** | ~400MB | After installation |
| **Ollama Download** | ~500MB | Only if not already installed |
| **AI Models** | 1-400GB | User downloads separately |

## 🌐 Distribution

### For End Users:

1. **Upload to cloud storage**:
   - Google Drive, OneDrive, Dropbox
   - Share download link

2. **GitHub Releases**:
   - Create new release
   - Upload `Enterprise-Voice-Browser-Setup-2.0.0.exe`
   - Add release notes

3. **Your website**:
   - Upload to your web hosting
   - Create download page
   - Link to installer

4. **File sharing**:
   - Send via email (if size permits)
   - Share via messaging apps
   - Use file transfer services

### Installation Instructions for Users:

```
Quick Start Guide for Users:
1. Download Enterprise-Voice-Browser-Setup-2.0.0.exe
2. Double-click to run installer
3. Follow installation wizard
4. If prompted, allow Ollama installation
5. After installation, open PowerShell and run:
   ollama pull llama3.2:1b
6. Launch Enterprise Voice Browser from desktop or Start Menu
7. Enjoy!
```

## 🐛 Troubleshooting

### Build Issues

#### "NSIS not found"

**Solution**:
```powershell
# Install with winget
winget install NSIS.NSIS

# Or with Chocolatey
choco install nsis

# Then restart terminal and try again
```

#### "Node not found"

**Solution**:
1. Install Node.js from https://nodejs.org/
2. Restart terminal
3. Verify: `node --version`

#### "npm install failed"

**Solution**:
```powershell
# Clean and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

#### "Electron build failed"

**Solution**:
```powershell
# Clean build
Remove-Item -Recurse -Force dist
npm run build:win
```

#### "NSIS build failed"

**Solutions**:
1. Make sure `dist/win-unpacked` exists (run `npm run build:win` first)
2. Make sure `LICENSE.txt` exists
3. Make sure `icon.png` exists
4. Check NSIS error messages for specific issues

### Runtime Issues

#### "Installer won't run"

**Solution**:
- Windows SmartScreen may block unsigned installers
- Right-click → Properties → Unblock → OK
- Or click "More info" → "Run anyway"

#### "Ollama download fails"

**Solution**:
- Check internet connection
- User can manually download Ollama from https://ollama.com/download
- Install manually, then run browser installer again

#### "Installer says Ollama installed but it's not working"

**Solution**:
1. Verify Ollama is in PATH: `where ollama`
2. Start Ollama service: `ollama serve`
3. Verify Ollama works: `ollama list`

## 🎯 Advanced Topics

### Code Signing

For production distribution, you should sign your installer:

1. **Get a code signing certificate**
   - From: DigiCert, Sectigo, etc.
   - Cost: ~$100-400/year

2. **Sign the installer**:
   ```powershell
   signtool sign /f your-certificate.pfx /p password /t http://timestamp.digicert.com Enterprise-Voice-Browser-Setup-2.0.0.exe
   ```

3. **Benefits**:
   - No SmartScreen warnings
   - Builds trust
   - Professional appearance

### Auto-Updates

To add auto-update capability:

1. Set up update server
2. Configure `autoUpdater` in `main.js`
3. Implement update checking logic
4. Rebuild installer

See Electron documentation: https://www.electronjs.org/docs/latest/api/auto-updater

### Silent Installation

Users can run installer silently:

```powershell
# Silent install
Enterprise-Voice-Browser-Setup-2.0.0.exe /S

# Silent install to custom location
Enterprise-Voice-Browser-Setup-2.0.0.exe /S /D=C:\CustomPath
```

### Bundling Ollama Installer

To bundle Ollama installer (instead of downloading):

1. Download OllamaSetup.exe
2. Place in browser folder
3. Edit `installer.nsi` to use local file instead of downloading
4. Rebuild

**Note**: This will increase installer size to ~700MB

## 📚 Additional Resources

- **NSIS Documentation**: https://nsis.sourceforge.io/Docs/
- **Electron Builder**: https://www.electron.build/
- **Ollama**: https://ollama.com/
- **Node.js**: https://nodejs.org/

## 🆘 Getting Help

If you encounter issues:

1. **Check this guide** for troubleshooting steps
2. **Check NSIS errors** - they usually explain the problem
3. **Clean build**:
   ```powershell
   Remove-Item -Recurse -Force dist, node_modules
   npm install
   .\build-unified-installer.bat
   ```
4. **Enable NSIS verbose logging**: Edit `installer.nsi` and add at top:
   ```nsis
   !verbose 4
   ```

## ✅ Build Checklist

Before building:
- [ ] Node.js installed (v16+)
- [ ] NSIS installed
- [ ] In correct folder (`browser/`)
- [ ] `icon.png` exists
- [ ] `LICENSE.txt` exists (created automatically)
- [ ] `package.json` configured
- [ ] Version numbers updated

During build:
- [ ] No error messages
- [ ] Electron build completes (~5-10 min)
- [ ] NSIS build completes (~1-2 min)
- [ ] Installer `.exe` created

After build:
- [ ] Installer `.exe` exists
- [ ] File size is ~200-250MB
- [ ] Test installer on clean Windows VM
- [ ] Verify browser launches
- [ ] Verify Ollama integration works
- [ ] Test uninstaller

## 🎉 Success!

After successful build, you'll see:

```
============================================================
 BUILD COMPLETE!
============================================================

Your unified installer has been created:

 File: Enterprise-Voice-Browser-Setup-2.0.0.exe
 Location: C:\path\to\browser\

This installer will:
 [x] Install Enterprise Voice Browser
 [x] Download and install Ollama (if needed)
 [x] Create desktop shortcut
 [x] Create Start Menu entries
 [x] Include uninstaller

============================================================
```

Now you can distribute this single `.exe` file to users!

---

## 📱 Next Steps: Windows Store

After creating the installer, you can also publish to Windows Store:

1. **Convert to MSIX**:
   - Use MSIX Packaging Tool
   - Or use electron-builder with MSIX target

2. **Create Windows Store listing**:
   - Register as Windows developer ($19 one-time fee)
   - Create app listing
   - Upload MSIX package
   - Submit for review

3. **Benefits**:
   - Automatic updates
   - Trusted by Windows
   - Easy installation
   - Better distribution

See: **WINDOWS_STORE_GUIDE.md** (to be created)

---

**Created**: 2025-11-05
**Version**: 2.0.0
**Status**: Ready to Build ✅

**Quick Start**: Run `.\build-unified-installer.bat` 🚀
