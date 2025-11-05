@echo off
cls
echo ============================================================
echo   COMPLETE AI VOICE SYSTEM LAUNCHER
echo   Starts TTS Server + AI Voice Assistant
echo ============================================================
echo.

REM Check if Ollama is running
echo 🔍 Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama is not running!
    echo.
    echo Please start Ollama first:
    echo   1. Open a new terminal
    echo   2. Run: ollama serve
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Ollama is running
)

echo.
echo 🚀 Starting services...
echo.

REM Start TTS Server in background
echo [1/2] 🎙️  Starting TTS Server (port 8000)...
start "TTS Server" /MIN python ollama_api_server.py
timeout /t 5 >nul
echo       ✅ TTS Server started

REM Start AI Voice Assistant in new window
echo [2/2] 🤖 Starting AI Voice Assistant (port 8001)...
start "AI Voice Assistant" python webrtc_voice_ai_full.py
timeout /t 3 >nul

echo.
echo ============================================================
echo   ✅ SYSTEM READY!
echo ============================================================
echo.
echo   🌐 Open: http://localhost:8001
echo.
echo   What it does:
echo   1. 🎤 Listens to your voice
echo   2. 📝 Converts speech to text
echo   3. 🤖 Generates AI response (Ollama)
echo   4. 🔊 Speaks response back to you
echo.
echo ============================================================
echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:8001

echo.
echo 💡 TIP: Check the Debug Console in the web interface
echo          to see what's happening in real-time!
echo.
pause
