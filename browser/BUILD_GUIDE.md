# 📦 Build Guide - Creating Windows Installer

This guide shows you how to create a Windows installer (.exe) for the Enterprise Voice Browser.

## 🎯 What You'll Get

After building, you'll have:

1. **Setup Installer** (`Enterprise Voice Browser Setup 2.0.0.exe`)
   - Full installation wizard
   - Creates Start Menu shortcuts
   - Creates Desktop shortcut
   - Proper uninstaller
   - ~200MB file size

2. **Portable Version** (`Enterprise Voice Browser 2.0.0.exe`)
   - No installation needed
   - Run from any folder
   - Perfect for USB drives
   - ~200MB file size

## 🚀 Quick Build (Easiest Method)

### Option 1: Double-Click Build Script

1. **Navigate to browser folder**:
   ```
   C:\git\enterprise-voice-tts\browser\
   ```

2. **Double-click**: `build-installer.bat`

3. **Wait** (5-10 minutes for first build)

4. **Find your installers** in the `dist\` folder!

### Option 2: Command Line

Open **PowerShell** or **CMD**:

```powershell
cd C:\git\enterprise-voice-tts\browser
.\build-installer.bat
```

## 📋 Detailed Build Steps

### Step 1: Prerequisites

**Required**:
- ✅ Node.js (v16+) - [Download](https://nodejs.org/)
- ✅ npm (comes with Node.js)

**Optional** (for better icon):
- ImageMagick - `winget install ImageMagick.ImageMagick`

### Step 2: Install Dependencies

```powershell
cd C:\git\enterprise-voice-tts\browser
npm install
```

This installs:
- electron
- electron-builder
- axios

### Step 3: Create Icon (Optional)

If you want a custom icon:

**Option A: Use SVG converter**
```powershell
# If you have ImageMagick
magick convert -background none -size 256x256 icon.svg icon.png
```

**Option B: Use existing icon**
The build script creates a placeholder icon automatically.

**Option C: Create your own**
- Create `icon.png` (256x256 pixels recommended)
- Place in browser folder
- Builder will use it automatically

### Step 4: Build the Installer

**Build everything (Installer + Portable)**:
```powershell
npm run build:win
```

**Or build just installer**:
```powershell
npm run build
```

**Or build just portable**:
```powershell
npm run build:win:portable
```

### Step 5: Find Your Files

Built files are in: `dist\` folder

```
C:\git\enterprise-voice-tts\browser\dist\
├── Enterprise Voice Browser Setup 2.0.0.exe  (Installer)
├── Enterprise Voice Browser 2.0.0.exe        (Portable)
└── win-unpacked\                             (Unpacked files)
```

## 🎨 Customizing the Build

### Change App Name

Edit `package.json`:
```json
{
  "name": "enterprise-voice-browser",
  "productName": "My Custom Browser Name",  // <-- Change this
  "version": "2.0.0"
}
```

### Change Icon

1. Create your icon: `icon.png` (256x256 or 512x512)
2. Place in browser folder
3. Rebuild: `npm run build:win`

### Change Version

Edit `package.json`:
```json
{
  "version": "2.0.0"  // <-- Change this (e.g., "2.1.0")
}
```

### Change Publisher Name

Edit `package.json`:
```json
{
  "build": {
    "win": {
      "publisherName": "Your Company Name"  // <-- Change this
    }
  }
}
```

## 📊 Build Configuration Details

### What Gets Included

From `package.json`:
```json
"files": [
  "main.js",
  "preload.js",
  "renderer.js",
  "styles.css",
  "index.html",
  "package.json"
]
```

### Installer Options

```json
"nsis": {
  "oneClick": false,                    // User can choose install location
  "allowToChangeInstallationDirectory": true,
  "createDesktopShortcut": true,        // Desktop icon
  "createStartMenuShortcut": true,      // Start menu entry
  "runAfterFinish": true                // Launch after install
}
```

## 🔧 Troubleshooting

### Build Fails: "electron-builder not found"

```powershell
npm install --save-dev electron-builder
npm run build:win
```

### Build Fails: "Icon not found"

```powershell
# Create icon first
powershell -ExecutionPolicy Bypass -File create-icon.ps1

# Then build
npm run build:win
```

### Build Takes Forever

First build takes 5-10 minutes (downloads Electron runtime).
Subsequent builds are much faster (2-3 minutes).

### "Out of Memory" Error

```powershell
# Increase Node.js memory
set NODE_OPTIONS=--max-old-space-size=4096
npm run build:win
```

### Build Succeeds but .exe Won't Run

Check:
1. **Windows Defender** - May block unsigned .exe
2. **Antivirus** - Add exception for dist folder
3. **SmartScreen** - Click "More info" → "Run anyway"

### Need Smaller File Size

Edit `package.json`:
```json
"compression": "maximum",  // Add under "build"
"asar": true
```

Then rebuild.

## 📦 Build Output Explained

### Files in `dist\` folder:

| File | Size | Purpose |
|------|------|---------|
| `Enterprise Voice Browser Setup 2.0.0.exe` | ~200MB | Full installer with wizard |
| `Enterprise Voice Browser 2.0.0.exe` | ~200MB | Portable (no install) |
| `win-unpacked\` | ~400MB | Unpacked application files |
| `builder-effective-config.yaml` | Small | Build configuration used |

### Installer (.exe Setup)

**Pros**:
- Professional installation experience
- Start Menu integration
- Desktop shortcut
- Proper uninstaller
- Updates easier to manage

**Cons**:
- Requires admin rights
- Leaves registry entries

### Portable (.exe)

**Pros**:
- No installation needed
- No admin rights needed
- Run from USB
- No registry changes

**Cons**:
- No Start Menu entry
- No automatic updates
- Manual shortcut creation

## 🌐 Distributing Your App

### For Personal Use

1. Build the portable version
2. Copy `.exe` to desired location
3. Run!

### For Sharing

1. **Upload to GitHub Releases**:
   - Create release on GitHub
   - Attach both `.exe` files
   - Users download and install

2. **Share via Cloud Storage**:
   - Upload to Google Drive / OneDrive
   - Share link
   - Users download

3. **Local Network**:
   - Place on shared drive
   - Users copy and run

### For Production

**Recommended steps**:

1. **Code Signing** (prevents security warnings):
   ```powershell
   # Get code signing certificate
   # Configure in package.json
   ```

2. **Auto-Updates**:
   - Set up update server
   - Configure `autoUpdater` in main.js

3. **Distribution Platforms**:
   - Microsoft Store
   - Chocolatey
   - Winget

## 🎯 Quick Reference Commands

```powershell
# Build installer + portable
npm run build:win

# Build only installer
npm run build

# Build only portable
npm run build:win:portable

# Test build without packaging
npm run pack

# Clean previous builds
rmdir /s /q dist
npm run build:win

# Quick test (no build)
npm start
```

## 📝 Build Checklist

Before building:
- [ ] Updated version in `package.json`
- [ ] Created/updated `icon.png`
- [ ] Tested app with `npm start`
- [ ] Committed code changes
- [ ] Updated CHANGELOG.md
- [ ] Run `npm install` (fresh dependencies)

After building:
- [ ] Test installer on clean Windows machine
- [ ] Test portable version
- [ ] Verify shortcuts work
- [ ] Test uninstaller
- [ ] Check file size is reasonable
- [ ] Virus scan the .exe files

## 🔍 Advanced Options

### Building for Different Architectures

```powershell
# 64-bit only (default)
npm run build:win

# 32-bit
electron-builder --win --ia32

# Both
electron-builder --win --x64 --ia32
```

### Creating Multiple Formats

Edit `package.json`:
```json
"target": [
  "nsis",     // Installer
  "portable", // Portable exe
  "zip",      // Zip archive
  "7z"        // 7z archive
]
```

### Debug Build

```powershell
# Build with debug info
set DEBUG=electron-builder
npm run build:win
```

## 💡 Tips

1. **First build is slow** - Subsequent builds are faster
2. **Test on clean Windows** - VM or different PC
3. **Sign your code** - For production distribution
4. **Use semantic versioning** - 2.0.0 → 2.0.1 → 2.1.0
5. **Keep builds organized** - Use version numbers
6. **Document changes** - Update CHANGELOG.md

## 🆘 Getting Help

If build fails:

1. **Check Node version**:
   ```powershell
   node --version  # Should be 16+
   ```

2. **Clean install**:
   ```powershell
   rmdir /s /q node_modules
   rmdir /s /q dist
   npm install
   npm run build:win
   ```

3. **Enable verbose logging**:
   ```powershell
   set DEBUG=electron-builder
   npm run build:win
   ```

4. **Check electron-builder docs**:
   https://www.electron.build/

## ✅ Success!

After successful build:

```
✓ Built files in: C:\git\enterprise-voice-tts\browser\dist\

📦 Enterprise Voice Browser Setup 2.0.0.exe (Installer)
   Size: ~200 MB
   Type: NSIS Installer

📦 Enterprise Voice Browser 2.0.0.exe (Portable)
   Size: ~200 MB
   Type: Standalone Executable

Ready to distribute! 🎉
```

---

**Created**: 2025-10-27
**Version**: 2.0
**Builder**: electron-builder v24.9.1
