# Enterprise Voice Browser - Installer Build Setup
# PowerShell script to prepare the build environment
# Version 2.0.0

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Enterprise Voice Browser - Installer Build Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[1/5] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "OK - Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js from: https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check NSIS
Write-Host "[2/5] Checking NSIS..." -ForegroundColor Yellow
try {
    $nsisVersion = makensis /VERSION 2>&1
    Write-Host "OK - NSIS found: $nsisVersion" -ForegroundColor Green
} catch {
    Write-Host "WARNING: NSIS not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "NSIS is required to build Windows installers." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Install NSIS with one of these methods:" -ForegroundColor Cyan
    Write-Host "  1. winget install NSIS.NSIS" -ForegroundColor White
    Write-Host "  2. choco install nsis" -ForegroundColor White
    Write-Host "  3. Download from: https://nsis.sourceforge.io/Download" -ForegroundColor White
    Write-Host ""
    $response = Read-Host "Do you want to install NSIS with winget now? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Installing NSIS..." -ForegroundColor Yellow
        winget install NSIS.NSIS
        Write-Host "Please restart this script after NSIS installation completes." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Please install NSIS and run this script again." -ForegroundColor Yellow
        exit 1
    }
}
Write-Host ""

# Check npm dependencies
Write-Host "[3/5] Checking npm dependencies..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "OK - node_modules exists" -ForegroundColor Green
} else {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: npm install failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "OK - Dependencies installed" -ForegroundColor Green
}
Write-Host ""

# Check/Create icon
Write-Host "[4/5] Checking icon..." -ForegroundColor Yellow
if (Test-Path "icon.png") {
    Write-Host "OK - icon.png exists" -ForegroundColor Green
} else {
    Write-Host "Creating default icon..." -ForegroundColor Yellow
    & .\create-icon.ps1
    if (Test-Path "icon.png") {
        Write-Host "OK - Icon created" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Could not create icon" -ForegroundColor Yellow
    }
}
Write-Host ""

# Check/Create LICENSE.txt
Write-Host "[5/5] Checking LICENSE.txt..." -ForegroundColor Yellow
if (Test-Path "LICENSE.txt") {
    Write-Host "OK - LICENSE.txt exists" -ForegroundColor Green
} else {
    Write-Host "Creating LICENSE.txt..." -ForegroundColor Yellow
    @"
MIT License

Copyright (c) 2025 Enterprise Voice Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Out-File -FilePath "LICENSE.txt" -Encoding UTF8
    Write-Host "OK - LICENSE.txt created" -ForegroundColor Green
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your build environment is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: .\build-unified-installer.bat" -ForegroundColor White
Write-Host "  2. Wait 5-15 minutes for build to complete" -ForegroundColor White
Write-Host "  3. Test the installer: Enterprise-Voice-Browser-Setup-2.0.0.exe" -ForegroundColor White
Write-Host ""
Write-Host "For help, see: UNIFIED_INSTALLER_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
