@echo off
cls
echo ============================================================
echo   AI VOICE ASSISTANT - FULL VERSION
echo   Speech Recognition + AI + Text-to-Speech
echo ============================================================
echo.

REM Check dependencies
echo 🔍 Checking dependencies...
echo.

python -c "import speech_recognition" 2>nul
if errorlevel 1 (
    echo ❌ speech_recognition not installed
    echo.
    echo Installing speech_recognition...
    pip install SpeechRecognition
    echo.
)

python -c "import aiohttp" 2>nul
if errorlevel 1 (
    echo ❌ aiohttp not installed
    echo.
    echo Installing aiohttp...
    pip install aiohttp
    echo.
)

echo ✅ Dependencies checked
echo.
echo ============================================================
echo   Starting AI Voice Assistant
echo ============================================================
echo.
echo Features:
echo   🎤 Speech-to-Text (Google Speech Recognition)
echo   🤖 AI Responses (Ollama - llama3.2:1b)
echo   🔊 Text-to-Speech (Your TTS System)
echo.
echo Make sure:
echo   ✅ Ollama is running (ollama serve)
echo   ✅ TTS server is running (port 8000)
echo.
echo ============================================================
echo.

python webrtc_voice_ai_full.py

pause
