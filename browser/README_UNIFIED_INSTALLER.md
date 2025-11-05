# 🎉 Unified Windows Installer

## What's New?

We've created a **unified Windows installer** that installs both the Enterprise Voice Browser AND Ollama in one easy installation process!

## 📦 Two Types of Installers

### 1. Unified Installer (NEW! ⭐)

**File**: `Enterprise-Voice-Browser-Setup-2.0.0.exe`

**Built with**: NSIS (Nullsoft Scriptable Install System)

**What it does**:
- ✅ Installs Enterprise Voice Browser
- ✅ Automatically detects if Ollama is installed
- ✅ Downloads and installs Ollama if needed
- ✅ Creates shortcuts
- ✅ One-stop installation

**Build command**:
```bash
.\build-unified-installer.bat
```

**Requirements**:
- NSIS installed (get with: `winget install NSIS.NSIS`)

### 2. Standard Installer (Original)

**File**: `dist/Enterprise Voice Browser Setup 2.0.0.exe`

**Built with**: electron-builder

**What it does**:
- ✅ Installs Enterprise Voice Browser only
- ❌ Does NOT install Ollama (user must install separately)

**Build command**:
```bash
npm run build:win
```

**Requirements**:
- Just Node.js and npm

## 🚀 Which Should I Use?

### Use Unified Installer When:
- ✅ You want the easiest user experience
- ✅ You're distributing to non-technical users
- ✅ You want one-click installation
- ✅ You don't mind larger file size (~500MB download during install)

### Use Standard Installer When:
- ✅ Users already have Ollama installed
- ✅ You want smaller initial download (~200MB)
- ✅ Users prefer to manage Ollama separately
- ✅ You don't want to install NSIS

## 📚 Quick Start Guides

Choose the guide for your needs:

| Guide | Purpose |
|-------|---------|
| **INSTALLER_QUICK_START.md** | 3-step guide to build unified installer |
| **UNIFIED_INSTALLER_GUIDE.md** | Complete guide for unified installer |
| **WINDOWS_STORE_GUIDE.md** | Publish to Microsoft Store |
| **BUILD_GUIDE.md** | Build standard Electron installer |
| **HOW_TO_CREATE_INSTALLER.md** | Original installer documentation |

## 🔨 Build Commands

```bash
# Unified installer (includes Ollama)
.\build-unified-installer.bat

# Standard installer (Electron only)
npm run build:win

# Windows Store package (MSIX/APPX)
npm run build:win:appx

# Portable version
npm run build:win:portable

# Test without building
npm start
```

## 📂 File Structure

```
browser/
├── build-unified-installer.bat        ← Build unified installer
├── installer.nsi                      ← NSIS installer script
├── setup-installer-build.ps1          ← Prerequisites checker
│
├── INSTALLER_QUICK_START.md           ← Quick start (3 steps)
├── UNIFIED_INSTALLER_GUIDE.md         ← Full unified installer guide
├── WINDOWS_STORE_GUIDE.md             ← Windows Store publishing
│
├── package.json                       ← Electron config (updated)
├── build-installer.bat                ← Original build script
├── BUILD_GUIDE.md                     ← Original build guide
└── ...
```

## 🎯 Recommended Workflow

### For Development:
```bash
npm start  # Test locally
```

### For Distribution:
```bash
.\build-unified-installer.bat  # Create unified installer
```

### For Windows Store:
```bash
npm run build:win:appx  # Create MSIX package
# Then follow WINDOWS_STORE_GUIDE.md
```

## ✅ What You Have Now

- ✅ Unified installer that includes Ollama
- ✅ Standard Electron installer
- ✅ Windows Store (MSIX) support
- ✅ Portable version support
- ✅ Complete documentation
- ✅ Build scripts for all scenarios

## 🆘 Need Help?

1. **Quick start**: See `INSTALLER_QUICK_START.md`
2. **Full guide**: See `UNIFIED_INSTALLER_GUIDE.md`
3. **Windows Store**: See `WINDOWS_STORE_GUIDE.md`
4. **Troubleshooting**: Check the guides above

## 💡 Tips

- **First time building?** Start with `INSTALLER_QUICK_START.md`
- **Need NSIS?** Run: `winget install NSIS.NSIS`
- **Testing?** Use `npm start` to test without building
- **Questions?** Check the comprehensive guides

---

**Ready to build?** 🚀

```bash
# Install NSIS (one time)
winget install NSIS.NSIS

# Build unified installer
.\build-unified-installer.bat
```

**Created**: 2025-11-05
**Version**: 2.0.0
**Status**: Ready to Build ✅
