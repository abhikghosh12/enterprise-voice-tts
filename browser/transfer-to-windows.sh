#!/bin/bash
# Transfer Script - Copy project to Windows
# This script helps you copy the project to Windows from Linux/WSL

echo "==========================================="
echo "Enterprise Voice Browser - Transfer Script"
echo "==========================================="
echo ""

# Check if we're in WSL
if grep -qi microsoft /proc/version; then
    echo "✓ WSL detected"
    echo ""
    
    # Default Windows path
    WIN_PATH="/mnt/c/git/enterprise-voice-tts"
    
    echo "Target directory: C:\\git\\enterprise-voice-tts"
    echo "This will be mounted as: $WIN_PATH"
    echo ""
    
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    # Create directory if it doesn't exist
    echo "Creating target directory..."
    mkdir -p "$WIN_PATH"
    
    # Copy files
    echo "Copying files..."
    cp -r /home/claude/enterprise-voice-tts/* "$WIN_PATH/"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Files copied successfully!"
        echo ""
        echo "Next steps:"
        echo "1. Open Windows Terminal or PowerShell"
        echo "2. Run: cd C:\\git\\enterprise-voice-tts"
        echo "3. Run: .\\setup.ps1"
        echo ""
        echo "Or double-click 'start.bat' to run the app"
    else
        echo "✗ Copy failed!"
        exit 1
    fi
else
    echo "Not running in WSL."
    echo ""
    echo "Manual transfer options:"
    echo ""
    echo "1. Using SCP:"
    echo "   scp -r /home/claude/enterprise-voice-tts username@windows-pc:C:/git/"
    echo ""
    echo "2. Using rsync:"
    echo "   rsync -av /home/claude/enterprise-voice-tts username@windows-pc:/c/git/"
    echo ""
    echo "3. Using ZIP:"
    echo "   cd /home/claude"
    echo "   zip -r enterprise-voice-tts.zip enterprise-voice-tts/"
    echo "   # Then transfer the ZIP to Windows and extract"
    echo ""
    echo "4. Using Git:"
    echo "   cd /home/claude/enterprise-voice-tts"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    echo "   git remote add origin YOUR_GITHUB_URL"
    echo "   git push -u origin main"
    echo "   # Then clone on Windows"
fi
