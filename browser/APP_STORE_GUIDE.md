# Publishing to App Stores

## Important Note About Android

**This is an Electron desktop application and CANNOT be published to Google Play Store directly.**

Electron apps run on:
- ✅ Windows
- ✅ macOS  
- ✅ Linux

For Android, you would need to:
1. Rebuild the app using **React Native** or **Flutter**
2. Use **Capacitor** or **Cordova** to wrap the web version
3. Create a completely separate Android app

## Publishing Options

### 1. Microsoft Store (Windows)

#### Requirements:
- Windows 10/11 PC
- Microsoft Developer account ($19 one-time fee)
- Code signing certificate

#### Steps:

1. **Build the app**
   ```powershell
   npm run build:win
   ```

2. **Get a Microsoft Developer Account**
   - Go to https://partner.microsoft.com/dashboard
   - Register as a developer
   - Pay the $19 registration fee

3. **Create App Package**
   - Install Windows SDK
   - Generate APPX package:
   ```powershell
   npm install --save-dev electron-windows-store
   ```
   
   Update `package.json`:
   ```json
   "build": {
     "win": {
       "target": ["appx"]
     }
   }
   ```

4. **Submit to Store**
   - Go to Partner Center
   - Create new app submission
   - Upload APPX file
   - Fill in app details, screenshots
   - Submit for certification

#### Estimated Timeline: 1-3 days for approval

---

### 2. Mac App Store (macOS)

#### Requirements:
- Mac computer
- Apple Developer account ($99/year)
- Code signing certificates

#### Steps:

1. **Join Apple Developer Program**
   - Go to https://developer.apple.com/
   - Enroll ($99/year)

2. **Get Certificates**
   - Create App ID in Apple Developer portal
   - Generate certificates
   - Download provisioning profile

3. **Build the app**
   ```bash
   npm run build:mac
   ```

4. **Sign the app**
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: YOUR NAME" "dist/Enterprise Voice Browser.app"
   ```

5. **Create DMG**
   ```bash
   npm install --save-dev electron-installer-dmg
   ```

6. **Submit via App Store Connect**
   - Use Xcode or Transporter app
   - Upload the signed app
   - Fill in metadata
   - Submit for review

#### Estimated Timeline: 2-7 days for approval

---

### 3. Direct Distribution (Easiest)

Instead of app stores, you can distribute directly:

#### For Windows:
```powershell
npm run build:win
```
Creates `Enterprise Voice Browser Setup.exe` in `dist/`

Users can download and install directly.

#### For Mac:
```bash
npm run build:mac
```
Creates a `.dmg` file users can download.

#### For Linux:
```bash
npm run build:linux
```
Creates an AppImage that runs on most Linux distros.

---

### 4. Alternative: Snap Store (Linux)

Snap Store is easier than traditional stores:

1. **Install snapcraft**
   ```bash
   sudo snap install snapcraft --classic
   ```

2. **Create snapcraft.yaml**
   ```yaml
   name: enterprise-voice-browser
   version: '1.0.0'
   summary: AI-powered browser with voice
   description: |
     AI-powered desktop browser with Ollama integration
   
   base: core20
   confinement: strict
   grade: stable
   
   apps:
     enterprise-voice-browser:
       command: npm start
       plugs:
         - network
         - audio-playback
         - audio-record
   ```

3. **Build and publish**
   ```bash
   snapcraft
   snapcraft login
   snapcraft upload *.snap --release=stable
   ```

#### Estimated Timeline: 1-2 days for approval

---

## For Android (Separate Project Needed)

To create an Android version, you need to rebuild using:

### Option 1: React Native
1. Create new React Native project
2. Port the UI from HTML/CSS to React Native components
3. Use React Native WebView for browser
4. Integrate with Ollama API (requires CORS setup)
5. Use React Native Voice for speech
6. Build APK and submit to Play Store

### Option 2: Capacitor
1. Create Ionic/Capacitor project
2. Wrap your existing web interface
3. Add Capacitor plugins for native features
4. Build Android app
5. Submit to Play Store

### Option 3: Flutter
1. Rebuild UI in Flutter
2. Use webview_flutter for browser
3. Integrate with Ollama
4. Build APK
5. Submit to Play Store

### Google Play Store Requirements:
- Google Play Developer account ($25 one-time fee)
- Privacy policy
- Content rating questionnaire
- Screenshots and app icon
- APK or AAB file
- Testing phase (internal/closed/open beta)

#### Estimated Timeline: 3-7 days for approval

---

## Recommended Publishing Strategy

For your Electron app:

1. **Start with Direct Distribution** (Easiest)
   - Build installers for Windows/Mac/Linux
   - Host on your website or GitHub Releases
   - No approval process needed
   - Free

2. **Then Try Microsoft Store** (Optional)
   - Reach more Windows users
   - $19 one-time fee
   - Relatively easy process

3. **For Mobile**: Create Separate App
   - If you really need Android/iOS
   - Requires significant additional development
   - Probably 2-4 weeks of work to port

---

## Current Status

✅ **Ready for Direct Distribution**
- Windows installer
- Mac DMG  
- Linux AppImage

❌ **Not Ready for:**
- Google Play Store (need Android app)
- iOS App Store (need iOS app)

⚠️ **Partially Ready for:**
- Microsoft Store (need APPX packaging)
- Mac App Store (need signing certificates)

---

## Quick Start for Distribution

The simplest way to share your app right now:

1. **Build for all platforms**
   ```bash
   npm run build:win    # Windows
   npm run build:mac    # macOS
   npm run build:linux  # Linux
   ```

2. **Upload to GitHub Releases**
   - Create a release on GitHub
   - Upload the installers from `dist/`
   - Users can download for their platform

3. **Or host on your website**
   - Upload installers to your web server
   - Create a download page
   - Users download and install

This way users can start using your app immediately without waiting for store approval!
