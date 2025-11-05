@echo off
cls
echo ============================================================
echo   AI VOICE ASSISTANT - FIXED VERSION
echo   Proper Endpoints + Audio Format Handling
echo ============================================================
echo.

REM Check dependencies
echo 🔍 Checking dependencies...
echo.

python -c "import aiohttp" 2>nul
if errorlevel 1 (
    echo ❌ aiohttp not installed
    echo Installing aiohttp...
    pip install aiohttp
    echo.
)

python -c "import pydub" 2>nul
if errorlevel 1 (
    echo ❌ pydub not installed  
    echo Installing pydub...
    pip install pydub
    echo.
)

echo ✅ Dependencies checked
echo.

REM Check if FFmpeg is installed (needed for WebM audio)
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WARNING: FFmpeg not found!
    echo.
    echo FFmpeg is required to process WebM audio from the browser.
    echo.
    echo Install options:
    echo   1. Run: install_ffmpeg.bat (if available)
    echo   2. Install with chocolatey: choco install ffmpeg
    echo   3. Download from: https://ffmpeg.org/download.html
    echo.
    echo Press any key to continue anyway (may have audio issues)...
    pause >nul
) else (
    echo ✅ FFmpeg is installed
)

echo.
echo ============================================================
echo   🚀 Starting Fixed AI Voice Assistant
echo ============================================================
echo.
echo This version:
echo   ✅ Uses correct TTS server endpoints
echo   ✅ Uploads audio files for STT
echo   ✅ Proper audio format handling
echo   ✅ Better error messages
echo.

REM Check if TTS server is running
echo 🔍 Checking if TTS server is running...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  TTS Server not detected on port 8000
    echo.
    echo Starting TTS Server...
    start "TTS Server" /MIN python ollama_api_server.py
    echo Waiting for TTS server to start...
    timeout /t 5 >nul
    echo ✅ TTS Server started
) else (
    echo ✅ TTS Server is already running
)

REM Check Ollama
echo 🔍 Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama is not running!
    echo.
    echo Please start Ollama first:
    echo   ollama serve
    echo.
    echo Then run this script again.
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Ollama is running
)

echo.
echo ============================================================
echo.

python webrtc_voice_ai_fixed.py

pause
