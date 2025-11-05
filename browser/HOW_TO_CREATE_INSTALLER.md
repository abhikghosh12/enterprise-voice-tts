# 📦 How to Create Windows Installer - Complete Guide

## ✅ Everything is Ready!

I've set up everything you need to create a professional Windows installer (.exe) for your Enterprise Voice Browser.

---

## 🎯 What You'll Create

### 1. Professional Installer
**File**: `Enterprise Voice Browser Setup 2.0.0.exe`

Features:
- ✅ Installation wizard
- ✅ Desktop shortcut
- ✅ Start Menu entry
- ✅ Uninstaller included
- ✅ Auto-launch after install
- ✅ Custom install location

### 2. Portable Version
**File**: `Enterprise Voice Browser 2.0.0.exe`

Features:
- ✅ No installation needed
- ✅ Run from anywhere
- ✅ USB-friendly
- ✅ No registry changes
- ✅ Standalone

---

## 🚀 How to Build (3 Easy Steps)

### Method 1: Double-Click (Easiest!)

1. **Navigate** to: `C:\git\enterprise-voice-tts\browser\`
2. **Double-click**: `build-installer.bat`
3. **Wait** 5-10 minutes
4. **Done!** Find installers in `dist\` folder

### Method 2: PowerShell

```powershell
cd C:\git\enterprise-voice-tts\browser
.\build-installer.bat
```

### Method 3: npm Command

```powershell
cd C:\git\enterprise-voice-tts\browser
npm run build:win
```

---

## 📁 Files Created for You

I've set up these files to make building easy:

### Build Scripts
1. **`build-installer.bat`** - One-click build script
   - Checks Node.js
   - Installs dependencies
   - Creates icon
   - Builds installer
   - Shows completion message

2. **`create-icon.ps1`** - Icon creation script
   - Creates PNG from SVG
   - Or generates placeholder
   - 256x256 size

### Configuration
3. **`package.json`** - Updated with:
   - Version 2.0.0
   - Build scripts
   - Windows installer config
   - NSIS settings

### Documentation
4. **`BUILD_GUIDE.md`** - Complete technical guide
5. **`README_BUILD.md`** - Quick reference
6. **`HOW_TO_CREATE_INSTALLER.md`** - This file!

### Assets
7. **`icon.png`** - Application icon (created)

---

## ⚙️ What Happens During Build

```
[1/5] Checking Node.js ✅
[2/5] Installing dependencies ✅
[3/5] Creating icon ✅
[4/5] Building Windows installer ⏱️ (5-10 min)
[5/5] Build complete! ✅
```

The build process:
1. Validates environment
2. Installs electron-builder
3. Packages your app
4. Creates installer
5. Creates portable version
6. Saves to `dist\` folder

---

## 📦 Build Output

After successful build, you'll find in `dist\` folder:

```
C:\git\enterprise-voice-tts\browser\dist\
│
├── Enterprise Voice Browser Setup 2.0.0.exe
│   └── Full installer (~200 MB)
│
├── Enterprise Voice Browser 2.0.0.exe
│   └── Portable version (~200 MB)
│
└── win-unpacked\
    └── Unpacked application files
```

---

## 🎮 Testing Your Installer

### Test the Installer

1. **Locate**: `dist\Enterprise Voice Browser Setup 2.0.0.exe`
2. **Double-click** (or right-click → Run as administrator)
3. **Follow wizard**:
   - Choose installation directory
   - Select shortcuts
   - Click Install
4. **App launches** automatically!
5. **Check**:
   - Desktop shortcut created
   - Start Menu entry created
   - App works correctly

### Test the Portable

1. **Locate**: `dist\Enterprise Voice Browser 2.0.0.exe`
2. **Copy** to any folder (or USB drive)
3. **Double-click** to run
4. **No installation** needed!

---

## 🌐 Distributing Your App

### For Friends/Colleagues

**Option 1: Email/Chat**
- Compress `.exe` to `.zip`
- Share via email or chat
- Recipient extracts and runs

**Option 2: Cloud Storage**
1. Upload to Google Drive / OneDrive / Dropbox
2. Get shareable link
3. Share link
4. Others download and install

**Option 3: USB Drive**
- Copy portable `.exe` to USB
- Others can run directly from USB
- Or copy to their computer

### For Public Distribution

**GitHub Releases** (Recommended):
1. Create new release on GitHub
2. Upload both `.exe` files
3. Write release notes
4. Publish
5. Users download from Releases page

**Your Own Website**:
1. Upload `.exe` to web hosting
2. Create download page
3. Link to `.exe` files
4. Add installation instructions

---

## 🔧 Customization Options

### Change App Name

Edit `package.json`:
```json
{
  "productName": "My Awesome Browser"
}
```
Rebuild to apply.

### Change Version Number

Edit `package.json`:
```json
{
  "version": "2.1.0"
}
```
Rebuilds will use new version.

### Change Icon

1. **Create** new `icon.png` (256x256 or 512x512)
2. **Replace** existing `icon.png`
3. **Rebuild**: `npm run build:win`

### Change Publisher Name

Edit `package.json`:
```json
{
  "build": {
    "win": {
      "publisherName": "Your Company Name"
    }
  }
}
```

---

## 🐛 Troubleshooting

### Build Fails Immediately

**Check Node.js**:
```powershell
node --version  # Should be v16 or higher
```

**Reinstall dependencies**:
```powershell
Remove-Item -Recurse -Force node_modules
npm install
```

### "electron-builder not found"

```powershell
npm install --save-dev electron-builder
npm run build:win
```

### Icon Missing

```powershell
powershell -ExecutionPolicy Bypass -File create-icon.ps1
```

### Build Succeeds but .exe Won't Run

**Windows Defender SmartScreen**:
1. Double-click `.exe`
2. Click **"More info"**
3. Click **"Run anyway"**

This is normal for unsigned apps. For production:
- Get a code signing certificate
- Sign your `.exe` files

### "Out of Memory" Error

```powershell
set NODE_OPTIONS=--max-old-space-size=4096
npm run build:win
```

### Build Takes Forever

First build downloads Electron runtime (~200MB).
- First build: 5-10 minutes
- Later builds: 2-3 minutes

---

## 💡 Tips & Best Practices

1. **Test on clean Windows** - VM or different PC
2. **Increment version** - 2.0.0 → 2.0.1 → 2.1.0
3. **Document changes** - Update CHANGELOG.md
4. **Keep builds organized** - Use version folders
5. **Scan for viruses** - Before distributing
6. **Provide instructions** - Include README with download

---

## 📊 What Users Need

### To Install (Installer Version)

**Requirements**:
- Windows 10 or 11
- ~400MB disk space
- Administrator rights (for installation)

**Prerequisites**:
- Ollama installed ([Download](https://ollama.com/download))
- At least one Ollama model pulled

**Installation**:
1. Download installer `.exe`
2. Double-click
3. Follow wizard
4. Launch app
5. Configure Ollama endpoint (Settings)

### To Run (Portable Version)

**Requirements**:
- Windows 10 or 11
- ~400MB disk space
- No admin rights needed

**Usage**:
1. Download portable `.exe`
2. Place in any folder
3. Double-click to run
4. Configure Ollama (Settings)

---

## 🎯 Build Commands Quick Reference

```powershell
# === Build Both (Installer + Portable) ===
npm run build:win

# === Build Specific ===
npm run build              # Installer + Portable
npm run build:win:portable # Portable only

# === Test Without Building ===
npm start                  # Run in dev mode

# === Clean Build ===
Remove-Item -Recurse -Force dist
npm run build:win

# === Rebuild Everything ===
Remove-Item -Recurse -Force dist, node_modules
npm install
npm run build:win
```

---

## ✅ Success Checklist

Before building:
- [ ] Node.js installed (v16+)
- [ ] In correct folder (`browser\`)
- [ ] `icon.png` exists
- [ ] `package.json` configured

During build:
- [ ] No error messages
- [ ] Build completes successfully
- [ ] `dist\` folder created

After build:
- [ ] Installer `.exe` exists (~200MB)
- [ ] Portable `.exe` exists (~200MB)
- [ ] Test both versions
- [ ] Verify app launches
- [ ] Test with Ollama connection

---

## 🎉 You're Ready!

Everything is set up. Just run:

```powershell
cd C:\git\enterprise-voice-tts\browser
.\build-installer.bat
```

Or double-click: **`build-installer.bat`**

Wait 5-10 minutes, and you'll have professional Windows installers! 🚀

---

## 📚 Additional Resources

- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Complete technical reference
- **[README_BUILD.md](README_BUILD.md)** - Quick build reference
- **[package.json](package.json)** - Build configuration
- **[Electron Builder Docs](https://www.electron.build/)** - Official docs

---

## 🆘 Need Help?

1. **Check troubleshooting** section above
2. **Read** [BUILD_GUIDE.md](BUILD_GUIDE.md)
3. **Enable debug logging**:
   ```powershell
   set DEBUG=electron-builder
   npm run build:win
   ```

---

**Created**: 2025-10-27
**Version**: 2.0.0
**Status**: Ready to Build ✅

**Start building**: `.\build-installer.bat` 🚀
