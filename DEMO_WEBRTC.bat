@echo off
cls
echo ============================================================
echo   WEBRTC VOICE AI CONTACT CENTER - FREE DEMO
echo   No Twilio - No Phone Numbers - 100%% Browser-Based
echo ============================================================
echo.
echo   ✅ No costs
echo   ✅ Works in browser
echo   ✅ No phone numbers needed
echo   ✅ Real-time AI voice chat
echo.
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python from https://www.python.org/
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if Ollama is running
echo 📋 Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama not detected
    echo    Starting Ollama is recommended for AI responses
    echo    You can continue without it for TTS-only mode
    echo.
) else (
    echo ✅ Ollama is running
)

echo.
echo 🚀 Starting services...
echo.

REM Start main TTS server in background
echo [1/2] 🎙️  Starting Voice TTS Server on port 8000...
start "Voice TTS Server" /MIN python ollama_api_server.py
timeout /t 5 >nul
echo       ✅ TTS Server started

REM Start WebRTC Contact Center in background
echo [2/2] 📞 Starting WebRTC Contact Center on port 8001...
start "WebRTC Voice Center" /MIN python webrtc_voice_center.py
timeout /t 3 >nul
echo       ✅ WebRTC Server started

echo.
echo ============================================================
echo   🎉 SYSTEM READY!
echo ============================================================
echo.
echo   📱 WebRTC Voice Interface: http://localhost:8001
echo   🎙️  TTS API Server:         http://localhost:8000
echo.
echo ============================================================
echo.

:menu
echo.
echo MAIN MENU:
echo ============================================================
echo.
echo   1. 🌐 Open WebRTC Voice Interface (Browser)
echo   2. 📊 View System Status
echo   3. 🧪 Run CLI Voice Demo
echo   4. 🔧 Configuration Info
echo   5. 🛑 Stop All Services
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto open_web
if "%choice%"=="2" goto status
if "%choice%"=="3" goto cli_demo
if "%choice%"=="4" goto config_info
if "%choice%"=="5" goto cleanup
echo ❌ Invalid choice. Please enter 1-5.
goto menu

:open_web
echo.
echo 🌐 Opening WebRTC Voice Interface...
echo.
echo ============================================================
echo   HOW TO USE:
echo ============================================================
echo.
echo   1. Click the "📞 Start Call" button
echo   2. Allow microphone access when prompted
echo   3. Start speaking - AI will respond with voice
echo   4. Click "📞 End Call" when finished
echo.
echo   Features:
echo   • Real-time voice chat with AI
echo   • Speech-to-text transcription
echo   • AI-generated voice responses
echo   • Live conversation history
echo.
echo ============================================================
echo.
start http://localhost:8001
echo ✅ Browser opened
echo.
pause
goto menu

:status
echo.
echo ============================================================
echo   📊 SYSTEM STATUS
echo ============================================================
echo.

echo 🔍 Checking services...
echo.

REM Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [OLLAMA]           ❌ OFFLINE
) else (
    echo [OLLAMA]           ✅ ONLINE - http://localhost:11434
)

REM Check Voice TTS Server
curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo [TTS SERVER]       ❌ OFFLINE
) else (
    echo [TTS SERVER]       ✅ ONLINE - http://localhost:8000
)

REM Check WebRTC Contact Center
curl -s http://localhost:8001 >nul 2>&1
if errorlevel 1 (
    echo [WEBRTC CENTER]    ❌ OFFLINE
) else (
    echo [WEBRTC CENTER]    ✅ ONLINE - http://localhost:8001
)

echo.
echo ============================================================
echo   📈 LIVE STATISTICS
echo ============================================================
echo.
curl -s http://localhost:8001/api/stats 2>nul

echo.
echo.
pause
goto menu

:cli_demo
echo.
echo 🧪 Running CLI Voice Demo...
echo.
python simple_voice_demo.py
echo.
pause
goto menu

:config_info
echo.
echo ============================================================
echo   🔧 CONFIGURATION INFORMATION
echo ============================================================
echo.
echo PORT CONFIGURATION:
echo   • WebRTC Interface:  http://localhost:8001
echo   • TTS API Server:    http://localhost:8000
echo   • Ollama API:        http://localhost:11434
echo.
echo FEATURES ENABLED:
echo   ✅ WebRTC Voice Calls (Browser-based)
echo   ✅ Speech Recognition (Whisper)
echo   ✅ Text-to-Speech (Multiple Engines)
echo   ✅ AI Chat (Ollama/Claude)
echo   ❌ Twilio Integration (Not needed!)
echo   ❌ Phone Numbers (Not needed!)
echo.
echo TTS ENGINES AVAILABLE:
echo   • Google TTS (gtts)
echo   • Edge TTS (edge-tts)
echo   • Piper TTS (piper)
echo   • System TTS
echo.
echo AI MODELS:
echo   • Recommended: llama3.2:1b (fastest)
echo   • Also supports: llama2, mistral, etc.
echo.
echo ============================================================
echo.
pause
goto menu

:cleanup
echo.
echo ============================================================
echo   🛑 STOPPING ALL SERVICES
echo ============================================================
echo.
echo Stopping Python processes...

REM Kill Python processes
taskkill /f /im python.exe >nul 2>&1

echo.
echo ✅ All services stopped
echo.
echo ============================================================
echo   👋 THANK YOU FOR TRYING WEBRTC VOICE AI!
echo ============================================================
echo.
echo What you just experienced:
echo   • Complete voice AI system - 100%% FREE
echo   • Real-time speech processing
echo   • AI-powered conversations
echo   • Browser-based calls (no Twilio needed!)
echo   • Zero ongoing costs
echo.
echo 💡 This system is production-ready and fully local!
echo.
echo To restart, just run this script again.
echo.
pause
exit
