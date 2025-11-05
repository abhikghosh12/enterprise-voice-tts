@echo off
echo ============================================================
echo   VOICE AI CONTACT CENTER - SIMPLE START
echo ============================================================
echo.

echo Starting servers...

REM Start TTS server
echo 1. Starting Voice TTS Server...
start "Voice TTS" cmd /k "python ollama_api_server.py"
timeout /t 3 >nul

REM Start WebRTC server  
echo 2. Starting WebRTC Contact Center...
start "WebRTC Center" cmd /k "python webrtc_voice_center.py"
timeout /t 2 >nul

echo.
echo ============================================================
echo   SERVERS STARTED
echo ============================================================
echo.
echo Voice TTS:        http://localhost:8000
echo Contact Center:   http://localhost:8001
echo.
echo Opening browsers...

REM Open browsers
start http://localhost:8000
timeout /t 2 >nul
start http://localhost:8001

echo.
echo Both interfaces are now open!
echo.
echo To stop servers: Close the command windows
echo.
pause