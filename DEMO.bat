@echo off
echo ============================================================
echo   VOICE AI CONTACT CENTER - COMPLETE DEMO
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo 🚀 Starting Complete Voice AI Contact Center Demo...
echo.

REM Check if Ollama is running
echo 📋 Checking prerequisites...
ping -n 1 localhost >nul 2>&1
if errorlevel 1 (
    echo ❌ Network issue!
    echo Please check your connection
    echo.
    pause
    exit /b 1
)
echo ✅ Network is working
echo ✅ Ollama is running

REM Start main TTS server in background
echo 🎙️ Starting Voice TTS Server...
start /B python ollama_api_server.py

REM Wait for server to fully initialize
echo    Initializing TTS engines...
timeout /t 8 >nul

REM Wait for TTS server to be ready
echo    Waiting for server to be ready...
timeout /t 3 >nul
echo    Server should be ready now
echo ✅ Voice TTS Server is running

REM Start WebRTC Contact Center in background
echo 📞 Starting WebRTC Contact Center...
start /B python webrtc_voice_center.py
timeout /t 3 >nul

REM Wait for WebRTC server
echo    WebRTC server starting...
timeout /t 2 >nul
echo ✅ WebRTC Contact Center is running

echo.
echo ============================================================
echo   DEMO READY - Choose Your Experience
echo ============================================================
echo.
echo 1. 🌐 Web Interface Demo (Recommended)
echo 2. 🖥️  Command Line Demo
echo 3. 📊 View System Status
echo 4. 🛑 Stop All Services
echo.

:menu
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto web_demo
if "%choice%"=="2" goto cli_demo
if "%choice%"=="3" goto status
if "%choice%"=="4" goto cleanup
echo Invalid choice. Please enter 1-4.
goto menu

:web_demo
echo.
echo 🌐 Opening Web Interface Demo...
echo.
echo ✨ FEATURES AVAILABLE:
echo   • Click-to-call voice interface
echo   • Real-time AI conversations
echo   • Speech recognition
echo   • Voice responses
echo   • Live call analytics
echo.
start http://localhost:8001
echo 📱 Web interface opened in your browser
echo 📞 Click "Start Call" to begin talking with AI
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:cli_demo
echo.
echo 🖥️  Starting Command Line Demo...
echo.
python demo_contact_center.py
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:status
echo.
echo 📊 SYSTEM STATUS
echo ============================================================
echo.

REM Check each service
echo 🔍 Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama: OFFLINE
) else (
    echo ✅ Ollama: ONLINE
)

echo 🔍 Checking Voice TTS Server...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Voice TTS: OFFLINE
) else (
    echo ✅ Voice TTS: ONLINE - http://localhost:8000
)

echo 🔍 Checking WebRTC Contact Center...
curl -s http://localhost:8001/api/stats >nul 2>&1
if errorlevel 1 (
    echo ❌ WebRTC Center: OFFLINE
) else (
    echo ✅ WebRTC Center: ONLINE - http://localhost:8001
)

echo.
echo 📈 LIVE STATS:
curl -s http://localhost:8001/api/stats 2>nul | findstr /C:"active_calls" /C:"satisfaction" /C:"resolution"

echo.
echo Press any key to return to menu...
pause >nul
goto menu

:cleanup
echo.
echo 🛑 Stopping all services...

REM Kill Python processes
taskkill /f /im python.exe >nul 2>&1

echo ✅ All services stopped
echo.
echo Thank you for trying Voice AI Contact Center!
echo.
echo 🎯 What you experienced:
echo   • Complete voice AI system
echo   • Real-time speech processing  
echo   • AI-powered conversations
echo   • WebRTC voice calls (no Twilio needed)
echo   • Live analytics and monitoring
echo.
echo 💡 Ready for production deployment!
echo.
pause
exit

echo.
echo ============================================================
echo   DEMO COMPLETED
echo ============================================================