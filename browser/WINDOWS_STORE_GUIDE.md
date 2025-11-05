# 📱 Windows Store App Publishing Guide

## Overview

This guide shows you how to publish **Enterprise Voice Browser** to the **Microsoft Store** (formerly Windows Store).

## 🎯 Benefits of Windows Store

### For Users:
- ✅ Trusted installation source
- ✅ Automatic updates
- ✅ Easy installation (one click)
- ✅ No SmartScreen warnings
- ✅ Sandboxed security
- ✅ Easy uninstallation

### For Developers:
- ✅ Wider distribution
- ✅ Professional credibility
- ✅ Update management
- ✅ Analytics and insights
- ✅ Monetization options (if desired)
- ✅ Trusted by enterprises

## 📋 Prerequisites

### 1. Windows Developer Account

**Cost**: $19 USD (one-time fee)

**Sign up**:
1. Go to: https://developer.microsoft.com/
2. Click "Join Now"
3. Create Microsoft account (or use existing)
4. Pay $19 registration fee
5. Complete profile
6. Wait for approval (~1-3 days)

### 2. Software Requirements

Install these tools:

1. **Windows 10/11**
   - Build 1809 or later
   - Required for MSIX packaging

2. **MSIX Packaging Tool**
   - Install from Microsoft Store
   - Or download: https://aka.ms/msixpackagingtool

3. **Windows SDK**
   - Download: https://developer.microsoft.com/windows/downloads/windows-sdk/
   - Or install with Visual Studio

4. **Your Electron App**
   - Already built with `npm run build:win`

### 3. Certificates

For testing:
- Create self-signed certificate (for local testing)

For production:
- Microsoft Store handles signing automatically

## 🚀 Quick Start - Publishing to Windows Store

### Step 1: Prepare Your App

1. **Build your app**:
   ```powershell
   cd C:\path\to\enterprise-voice-tts\browser
   npm run build:win
   ```

2. **Verify build**:
   - Check `dist/win-unpacked/` exists
   - Test the app works

### Step 2: Create MSIX Package

#### Option A: Using electron-builder (Recommended)

1. **Update package.json**:

```json
{
  "build": {
    "appId": "com.enterprise.voicebrowser",
    "productName": "Enterprise Voice Browser",
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        },
        {
          "target": "appx",
          "arch": ["x64"]
        }
      ],
      "publisherName": "CN=YourPublisherName",
      "identityName": "YourCompany.EnterpriseVoiceBrowser"
    },
    "appx": {
      "applicationId": "EnterpriseVoiceBrowser",
      "backgroundColor": "#ffffff",
      "displayName": "Enterprise Voice Browser",
      "identityName": "YourCompany.EnterpriseVoiceBrowser",
      "publisher": "CN=YourPublisherName",
      "publisherDisplayName": "Your Company"
    }
  }
}
```

2. **Build MSIX**:
   ```powershell
   npm install --save-dev electron-builder
   npx electron-builder --win appx
   ```

3. **Output**:
   - File: `dist/Enterprise Voice Browser 2.0.0.appx`

#### Option B: Using MSIX Packaging Tool (Manual)

1. **Launch MSIX Packaging Tool**

2. **Choose "Application package"**

3. **Select "Create package on this computer"**

4. **Choose signing certificate**:
   - Create new (for testing)
   - Or use existing

5. **Package information**:
   - **Package name**: Enterprise Voice Browser
   - **Publisher**: Your name/company
   - **Version**: 2.0.0.0
   - **Install location**: C:\Program Files\Enterprise Voice Browser

6. **Prepare computer**:
   - Tool will disable Windows Search, etc.
   - Click "Next"

7. **Installation**:
   - Browse to your installer: `Enterprise Voice Browser Setup 2.0.0.exe`
   - Run the installer
   - Complete installation
   - Click "Next"

8. **First launch**:
   - Launch the app
   - Test functionality
   - Click "Next" when done

9. **Create package**:
   - Review and click "Create"
   - Wait for packaging to complete

10. **Output**:
    - MSIX file created
    - Location shown in tool

### Step 3: Test Your MSIX Package

1. **Install certificate** (for testing only):
   ```powershell
   # Right-click .appx file → Properties → Digital Signatures
   # Select signature → Details → View Certificate → Install Certificate
   # Choose "Local Machine" → "Place all certificates in the following store"
   # Browse → "Trusted Root Certification Authorities"
   ```

2. **Install app**:
   ```powershell
   # Double-click .appx file
   # Or use PowerShell:
   Add-AppxPackage -Path ".\Enterprise Voice Browser 2.0.0.appx"
   ```

3. **Test app**:
   - Launch from Start Menu
   - Test all features
   - Verify Ollama integration works

4. **Uninstall** (if needed):
   ```powershell
   Get-AppxPackage *EnterpriseVoiceBrowser* | Remove-AppxPackage
   ```

### Step 4: Create Store Listing

1. **Go to Partner Center**:
   - https://partner.microsoft.com/dashboard

2. **Create new app**:
   - Click "New product" → "App"
   - Enter app name: "Enterprise Voice Browser"
   - Reserve name

3. **Fill out app information**:

   **Properties**:
   - Category: Productivity
   - Subcategory: Tools
   - Privacy policy URL (required)
   - Support contact info

   **Age ratings**:
   - Complete questionnaire
   - Likely rating: PEGI 3 / ESRB E

   **Packages**:
   - Upload your `.appx` or `.msix` file
   - Must be signed by Microsoft Store

   **Store listings**:
   - **Description** (10-10,000 characters):
     ```
     Enterprise Voice Browser is an AI-powered browser with integrated voice capabilities.

     Features:
     • AI chat powered by Ollama
     • Text-to-speech
     • Voice recognition
     • Web browsing with AI assistance
     • Local AI processing (privacy-focused)
     • Fast and responsive

     Requirements:
     • Windows 10/11
     • Ollama (free download from ollama.com)
     • 4GB RAM recommended
     • Internet connection
     ```

   - **Screenshots** (at least 1, up to 10):
     - Take screenshots of your app
     - Minimum 1366 x 768
     - Recommended: 1920 x 1080
     - Show key features

   - **Store logos**:
     - 300 x 300 (required)
     - Use your icon.png

   - **Keywords** (up to 7):
     - AI browser
     - Voice browser
     - Ollama
     - TTS
     - AI assistant
     - Chat browser

   **Pricing**:
   - Free (recommended)
   - Or set price

   **Availability**:
   - Markets: All markets (or specific ones)
   - Release date: As soon as approved

4. **Submit for certification**:
   - Review all sections (must be green checkmarks)
   - Click "Submit to Store"
   - Wait for certification

### Step 5: Certification Process

**Timeline**: 24-48 hours (usually)

**What Microsoft checks**:
- App functionality
- Content policy compliance
- Technical requirements
- Security
- Metadata accuracy

**Possible outcomes**:
1. **Approved** ✅
   - App goes live in Store
   - Users can download

2. **Failed** ❌
   - Review failure reasons
   - Fix issues
   - Resubmit

**Common rejection reasons**:
- Missing privacy policy
- App crashes
- Incomplete metadata
- Security issues
- Misleading description

## 🔧 Important Considerations

### Ollama Dependency

**Issue**: Your app requires Ollama to be installed separately.

**Solutions**:

1. **Clearly state in description**:
   ```
   REQUIREMENTS:
   • This app requires Ollama to be installed separately
   • Download Ollama free from: https://ollama.com/
   • After installing this app, install Ollama and run:
     ollama pull llama3.2:1b
   ```

2. **First-run experience**:
   - Your app already checks for Ollama
   - Shows helpful dialogs
   - Links to download

3. **Alternative - Host Ollama** (advanced):
   - Host Ollama on your own server
   - App connects to your server
   - Users don't need to install Ollama
   - But you pay hosting costs

### Privacy Policy

**Required by Microsoft Store**

**What to include**:
- What data you collect (if any)
- How you use data
- Third-party services (Ollama)
- User rights
- Contact information

**Example privacy policy**:
```
Privacy Policy for Enterprise Voice Browser

Data Collection:
• This app does not collect any personal data
• All AI processing is done locally on your computer
• No data is sent to our servers

Third-Party Services:
• This app uses Ollama, a local AI engine
• Ollama runs on your computer and does not send data externally
• See Ollama's privacy policy: https://ollama.com/privacy

Contact:
• Email: privacy@yourcompany.com
```

**Where to host**:
- Your website
- GitHub Pages
- Or use a privacy policy generator

### Update Strategy

**Manual updates**:
1. Build new version
2. Increment version number (2.0.0 → 2.0.1)
3. Create new MSIX
4. Upload to Partner Center
5. Submit for certification
6. Users get auto-update

**Automatic updates**:
- Microsoft Store handles updates automatically
- Users get updates when you publish new version
- Can set gradual rollout (10%, 25%, 50%, 100%)

## 📊 Post-Publication

### Analytics

**Partner Center provides**:
- Download numbers
- Active users
- Crashes and errors
- User reviews
- Demographics

**Access analytics**:
1. Go to Partner Center
2. Select your app
3. Click "Analytics"

### User Reviews

**Monitor reviews**:
- Users can rate (1-5 stars)
- Users can write reviews
- Respond to reviews (recommended)

**Responding to reviews**:
- Thank users for positive reviews
- Address concerns in negative reviews
- Provide support for issues

### Updates

**When to update**:
- Bug fixes
- New features
- Security patches
- Ollama compatibility updates

**How to update**:
1. Build new version
2. Update version number
3. Create MSIX
4. Upload to Partner Center
5. Submit

## 🐛 Troubleshooting

### Build Issues

#### "Publisher name mismatch"

**Solution**:
- Make sure publisher in package.json matches your Partner Center publisher identity
- Get publisher identity from Partner Center → App identity

#### "Package validation failed"

**Solution**:
- Run Windows App Certification Kit (WACK):
  ```powershell
  "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\appcert.exe"
  ```
- Fix reported issues
- Rebuild

### Certification Issues

#### "Missing privacy policy"

**Solution**:
- Create privacy policy
- Host online
- Add URL to Store listing

#### "App crashes on startup"

**Solution**:
- Test on clean Windows VM
- Check dependencies
- Verify all files are included in MSIX
- Check app logs

#### "Misleading description"

**Solution**:
- Clearly state Ollama requirement
- Don't make false claims
- Accurately describe features

## 🎯 Best Practices

1. **Clear Requirements**:
   - State Ollama is required
   - Provide installation instructions
   - Link to Ollama download

2. **Good Screenshots**:
   - Show actual app interface
   - Highlight key features
   - Use high resolution
   - No text-heavy images

3. **Detailed Description**:
   - What the app does
   - Key features
   - Requirements
   - How to get started

4. **Responsive Support**:
   - Monitor reviews
   - Respond to user questions
   - Fix reported bugs quickly

5. **Regular Updates**:
   - Fix bugs promptly
   - Add requested features
   - Keep compatible with latest Windows

6. **Professional Presentation**:
   - Good icon
   - Clear branding
   - Professional screenshots
   - Well-written description

## 📚 Resources

- **Partner Center**: https://partner.microsoft.com/dashboard
- **Store Policies**: https://docs.microsoft.com/windows/uwp/publish/store-policies
- **MSIX Documentation**: https://docs.microsoft.com/windows/msix/
- **Electron MSIX**: https://www.electron.build/configuration/appx
- **Windows App Certification Kit**: Included in Windows SDK

## ✅ Checklist

Before submitting:
- [ ] Windows Developer account created ($19)
- [ ] App built and tested
- [ ] MSIX package created
- [ ] MSIX tested on clean Windows VM
- [ ] Privacy policy created and hosted
- [ ] Screenshots prepared (high quality)
- [ ] Store listing completed
  - [ ] Description
  - [ ] Screenshots
  - [ ] Icon
  - [ ] Keywords
  - [ ] Privacy policy URL
  - [ ] Support email
- [ ] Age rating completed
- [ ] Pricing set
- [ ] Markets selected
- [ ] All sections show green checkmark
- [ ] Ready to submit!

## 🎉 After Approval

Once your app is approved:

1. **Share the Store link**:
   ```
   https://www.microsoft.com/store/apps/[your-app-id]
   ```

2. **Promote your app**:
   - Share on social media
   - Blog post
   - Email newsletter
   - GitHub README

3. **Monitor analytics**:
   - Track downloads
   - Read reviews
   - Check crash reports

4. **Maintain your app**:
   - Regular updates
   - Bug fixes
   - New features
   - Respond to reviews

## 💡 Alternative - Sideload Distribution

If you don't want to publish to Store:

**Sideload option**:
1. Create MSIX package
2. Sign with your certificate
3. Distribute MSIX + certificate
4. Users install certificate
5. Users install MSIX

**Pros**:
- No $19 fee
- No certification wait
- Full control

**Cons**:
- Users must install certificate
- No automatic updates
- Less trusted
- Manual distribution

## 🌟 Enterprise Distribution

For enterprise customers:

**Microsoft Store for Business**:
1. Publish to public Store
2. Make available for business
3. Enterprises can deploy via their Store
4. Managed updates

**Private Store**:
1. Create private line-of-business app
2. Only available to your organization
3. No public Store listing

---

**Created**: 2025-11-05
**Version**: 1.0.0
**Status**: Ready for Store Submission ✅

**Next Steps**: Create Windows Developer account and start the submission process! 🚀
