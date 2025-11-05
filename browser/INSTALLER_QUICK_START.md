# ⚡ Quick Start - Unified Windows Installer

## 🎯 What This Does

Creates a single Windows installer (`.exe`) that installs:
- ✅ Enterprise Voice Browser
- ✅ Ollama AI Engine (automatically)

## 🚀 Build in 3 Steps

### Step 1: Install NSIS (One Time Only)

**Option 1 - winget** (Recommended):
```powershell
winget install NSIS.NSIS
```

**Option 2 - Chocolatey**:
```powershell
choco install nsis
```

**Option 3 - Manual**:
- Download from: https://nsis.sourceforge.io/Download
- Install

### Step 2: Build the Installer

```powershell
cd C:\path\to\enterprise-voice-tts\browser
.\build-unified-installer.bat
```

Wait 5-15 minutes (first build takes longer)

### Step 3: Distribute

Your installer is ready:
```
Enterprise-Voice-Browser-Setup-2.0.0.exe
```

Share this file with users!

## 📦 What Users Get

When users run the installer:

1. ✅ Installation wizard opens
2. ✅ Checks if Ollama is installed
3. ✅ Downloads/installs Ollama if needed
4. ✅ Installs Enterprise Voice Browser
5. ✅ Creates desktop shortcut
6. ✅ Creates Start Menu entry
7. ✅ Ready to use!

## 📋 User Instructions

After installation, users need to:

```powershell
# Download AI model (one time)
ollama pull llama3.2:1b

# Launch browser
# (Use desktop shortcut or Start Menu)
```

## 🔧 Files Created

This guide created these new files:

```
browser/
├── installer.nsi                      ← NSIS installer script
├── build-unified-installer.bat        ← Build script
├── setup-installer-build.ps1          ← Setup/prerequisites checker
├── UNIFIED_INSTALLER_GUIDE.md         ← Full guide
├── WINDOWS_STORE_GUIDE.md             ← Store publishing guide
└── INSTALLER_QUICK_START.md           ← This file
```

## 🐛 Troubleshooting

### Build fails with "NSIS not found"
```powershell
winget install NSIS.NSIS
# Restart terminal
.\build-unified-installer.bat
```

### Build fails with "Node not found"
- Install Node.js: https://nodejs.org/
- Restart terminal
- Try again

### "dist/win-unpacked not found"
```powershell
npm run build:win
# Wait for build to complete
.\build-unified-installer.bat
```

## 📚 Full Documentation

- **UNIFIED_INSTALLER_GUIDE.md** - Complete guide
- **WINDOWS_STORE_GUIDE.md** - Publishing to Windows Store
- **BUILD_GUIDE.md** - Electron build details
- **HOW_TO_CREATE_INSTALLER.md** - Original installer guide

## 💡 Quick Commands

```powershell
# Setup prerequisites
.\setup-installer-build.ps1

# Build unified installer
.\build-unified-installer.bat

# Build just Electron app
npm run build:win

# Test app (no build)
npm start
```

## ✅ Ready to Go!

You now have everything needed to create a professional Windows installer!

**Next**: Run `.\build-unified-installer.bat` 🚀

---

**For Windows Store**: See `WINDOWS_STORE_GUIDE.md`
