@echo off
REM Enterprise Voice Browser - Unified Installer Builder
REM This script builds a Windows installer that includes Ollama
REM Version 2.0.0

echo ============================================================
echo  Enterprise Voice Browser - Unified Installer Builder
echo ============================================================
echo.
echo This will create a Windows installer that:
echo  - Installs Enterprise Voice Browser
echo  - Downloads and installs Ollama (if not already installed)
echo  - Sets up shortcuts and start menu entries
echo.
echo Expected build time: 5-15 minutes
echo ============================================================
echo.

REM Check if Node.js is installed
echo [1/7] Checking Node.js...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed!
    echo Please download and install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo OK - Node.js found
echo.

REM Check if NSIS is installed
echo [2/7] Checking NSIS (Nullsoft Scriptable Install System)...
where makensis >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: NSIS is not installed!
    echo.
    echo NSIS is required to create Windows installers.
    echo.
    echo Please install NSIS:
    echo   Option 1: Download from https://nsis.sourceforge.io/Download
    echo   Option 2: Install with winget: winget install NSIS.NSIS
    echo   Option 3: Install with Chocolatey: choco install nsis
    echo.
    echo After installing NSIS, run this script again.
    echo.
    pause
    exit /b 1
)
makensis /VERSION
echo OK - NSIS found
echo.

REM Install npm dependencies
echo [3/7] Installing npm dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm install failed!
    pause
    exit /b 1
)
echo OK - Dependencies installed
echo.

REM Create icon if it doesn't exist
echo [4/7] Checking icon...
if not exist "icon.png" (
    echo Creating default icon...
    powershell -ExecutionPolicy Bypass -File create-icon.ps1
) else (
    echo OK - Icon already exists
)
echo.

REM Create LICENSE.txt if it doesn't exist
echo [5/7] Creating LICENSE.txt...
if not exist "LICENSE.txt" (
    echo MIT License > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright (c) 2025 Enterprise Voice Team >> LICENSE.txt
    echo. >> LICENSE.txt
    echo Permission is hereby granted, free of charge, to any person obtaining a copy >> LICENSE.txt
    echo of this software and associated documentation files (the "Software"), to deal >> LICENSE.txt
    echo in the Software without restriction, including without limitation the rights >> LICENSE.txt
    echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell >> LICENSE.txt
    echo copies of the Software, and to permit persons to whom the Software is >> LICENSE.txt
    echo furnished to do so, subject to the following conditions: >> LICENSE.txt
    echo. >> LICENSE.txt
    echo The above copyright notice and this permission notice shall be included in all >> LICENSE.txt
    echo copies or substantial portions of the Software. >> LICENSE.txt
    echo. >> LICENSE.txt
    echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. >> LICENSE.txt
    echo OK - LICENSE.txt created
) else (
    echo OK - LICENSE.txt already exists
)
echo.

REM Build the Electron app
echo [6/7] Building Electron application...
echo This may take 5-10 minutes on first build...
call npm run build:win
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Electron build failed!
    pause
    exit /b 1
)
echo OK - Electron build complete
echo.

REM Build the unified installer with NSIS
echo [7/7] Creating unified installer with NSIS...
echo.
echo Building installer: Enterprise-Voice-Browser-Setup-2.0.0.exe
echo This includes:
echo   - Enterprise Voice Browser
echo   - Ollama downloader/installer
echo   - Setup wizard
echo   - Shortcuts
echo   - Uninstaller
echo.

makensis installer.nsi
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: NSIS build failed!
    echo Check the error messages above for details.
    pause
    exit /b 1
)
echo.
echo ============================================================
echo  BUILD COMPLETE!
echo ============================================================
echo.
echo Your unified installer has been created:
echo.
echo  File: Enterprise-Voice-Browser-Setup-2.0.0.exe
echo  Location: %CD%
echo.
echo This installer will:
echo  [x] Install Enterprise Voice Browser
echo  [x] Download and install Ollama (if needed)
echo  [x] Create desktop shortcut
echo  [x] Create Start Menu entries
echo  [x] Include uninstaller
echo.
echo ============================================================
echo  NEXT STEPS
echo ============================================================
echo.
echo 1. Test the installer:
echo    - Double-click: Enterprise-Voice-Browser-Setup-2.0.0.exe
echo    - Follow the installation wizard
echo    - Test the installed application
echo.
echo 2. Distribute to users:
echo    - Upload to file sharing service
echo    - Share via email or download link
echo    - Users just need to download and run the .exe
echo.
echo 3. For Windows Store:
echo    - Use the MSIX packaging tools
echo    - See WINDOWS_STORE_GUIDE.md (to be created)
echo.
echo ============================================================
echo.
pause
