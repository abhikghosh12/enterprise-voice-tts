# 🚀 Quick Build Instructions

## TL;DR - Create Windows Installer

### Super Quick (One Command):

Open **PowerShell** (NOT Git Bash):

```powershell
cd C:\git\enterprise-voice-tts\browser
.\build-installer.bat
```

**Or just double-click**: `build-installer.bat`

Wait 5-10 minutes ⏱️

Find your installer in `dist\` folder! 🎉

---

## What You Get

After building:

### 1. Full Installer
```
dist\Enterprise Voice Browser Setup 2.0.0.exe
```
- Professional installation wizard
- Creates Start Menu shortcut
- Creates Desktop shortcut
- Includes uninstaller
- Size: ~200MB

### 2. Portable Version
```
dist\Enterprise Voice Browser 2.0.0.exe
```
- No installation needed
- Run from anywhere
- Perfect for USB drives
- Size: ~200MB

---

## Requirements

Before building:
- ✅ **Node.js** (v16+) - [Download](https://nodejs.org/)
- ✅ **npm** (comes with Node.js)
- ✅ **Windows 10/11**

---

## Build Commands

```powershell
# === Method 1: Automated Script (Easiest) ===
.\build-installer.bat


# === Method 2: Manual Commands ===
npm install              # Install dependencies (first time)
npm run build:win        # Build both installer + portable


# === Method 3: Specific Builds ===
npm run build:win        # Both installer and portable
npm run build            # Same as above
npm run build:win:portable  # Portable only
```

---

## After Building

### Test the Installer

1. Go to `dist\` folder
2. Find `Enterprise Voice Browser Setup 2.0.0.exe`
3. **Right-click** → **Run as administrator** (recommended)
4. Follow installation wizard
5. App launches automatically!

### Test the Portable

1. Go to `dist\` folder
2. Find `Enterprise Voice Browser 2.0.0.exe`
3. **Double-click** to run
4. No installation needed!

---

## Troubleshooting

### "Build failed"

```powershell
# Clean and retry
Remove-Item -Recurse -Force node_modules, dist
npm install
npm run build:win
```

### "Icon not found"

```powershell
# Create icon
powershell -ExecutionPolicy Bypass -File create-icon.ps1
npm run build:win
```

### "electron-builder not found"

```powershell
npm install --save-dev electron-builder
npm run build:win
```

### Windows Defender Blocks .exe

This is normal for unsigned apps:
1. Click **"More info"**
2. Click **"Run anyway"**

For production, get a code signing certificate.

---

## Distribution

### For Personal Use
Just run the portable `.exe` - no installation needed!

### For Sharing with Others

**Option 1: Upload to GitHub**
1. Create a release on GitHub
2. Attach both `.exe` files
3. Share the release link

**Option 2: Cloud Storage**
1. Upload to Google Drive / OneDrive / Dropbox
2. Share the link
3. Others download and install

**Option 3: Local Network**
1. Copy to shared network drive
2. Others can access and install

---

## Customization

### Change App Name

Edit `package.json`:
```json
"productName": "Your Custom Name Here"
```

### Change Version

Edit `package.json`:
```json
"version": "2.1.0"
```

### Change Icon

1. Replace `icon.png` with your 256x256 image
2. Rebuild: `npm run build:win`

---

## Build Time

- **First build**: 5-10 minutes (downloads Electron runtime)
- **Subsequent builds**: 2-3 minutes

---

## File Sizes

| File | Size |
|------|------|
| Installer | ~200 MB |
| Portable | ~200 MB |
| Installed app | ~400 MB on disk |

---

## Advanced

For detailed build options, see:
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Complete build documentation
- **[package.json](package.json)** - Build configuration

---

## Quick Reference

```powershell
# Build
npm run build:win

# Test (without building)
npm start

# Clean
Remove-Item -Recurse -Force dist

# Rebuild
npm run build:win
```

---

## Success Checklist

After build completes:

- [ ] `dist\` folder exists
- [ ] `Enterprise Voice Browser Setup 2.0.0.exe` exists (Installer)
- [ ] `Enterprise Voice Browser 2.0.0.exe` exists (Portable)
- [ ] Both files are ~200MB
- [ ] Test installer on Windows
- [ ] Test portable version
- [ ] Both launch successfully

---

**Ready to build?** Run: `.\build-installer.bat`

**Need help?** See: [BUILD_GUIDE.md](BUILD_GUIDE.md)

**Version**: 2.0.0
**Updated**: 2025-10-27
