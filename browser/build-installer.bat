@echo off
echo ========================================
echo Enterprise Voice Browser - Build Installer
echo ========================================
echo.

REM Check Node.js
echo [1/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js found:
node --version

echo.
echo [2/5] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/5] Creating icon...
if not exist icon.png (
    echo Creating icon from SVG or placeholder...
    powershell -ExecutionPolicy Bypass -File create-icon.ps1
    if errorlevel 1 (
        echo WARNING: Icon creation failed, using default
    )
)

echo.
echo [4/5] Building Windows installer...
echo This may take several minutes...
call npm run build:win
if errorlevel 1 (
    echo ERROR: Build failed!
    echo.
    echo Common issues:
    echo - Make sure all dependencies are installed
    echo - Check that icon.png exists
    echo - Try: npm install --save-dev electron-builder
    pause
    exit /b 1
)

echo.
echo [5/5] Build complete!
echo.
echo ========================================
echo Installation Files Created:
echo ========================================
echo.
dir dist\*.exe /b 2>nul
echo.
echo Location: %CD%\dist\
echo.
echo Files created:
echo - Enterprise Voice Browser Setup X.X.X.exe (Installer)
echo - Enterprise Voice Browser X.X.X.exe (Portable)
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Find installer in: dist\ folder
echo 2. Double-click the Setup.exe to install
echo 3. Or use the portable .exe (no installation needed)
echo 4. Share with others!
echo.
echo ========================================
pause
