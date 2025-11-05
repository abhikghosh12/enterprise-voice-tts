@echo off
echo ============================================================
echo   VOICE AI CONTACT CENTER - WORKING DEMO
echo ============================================================
echo.

echo 1. Starting Ollama...
start "Ollama" cmd /k "ollama serve"
timeout /t 3 >nul

echo 2. Starting Voice TTS Server...
start "Voice TTS" cmd /k "python ollama_api_server.py"
timeout /t 8 >nul

echo 3. Starting WebRTC Contact Center...
start "WebRTC Center" cmd /k "python webrtc_voice_center.py"
timeout /t 5 >nul

echo 4. Opening browsers...
start http://localhost:8000
timeout /t 2 >nul
start http://localhost:8001

echo.
echo ============================================================
echo   DEMO READY!
echo ============================================================
echo.
echo Voice TTS UI:     http://localhost:8000
echo Contact Center:   http://localhost:8001
echo.
echo Test the voice features:
echo - Type messages and get voice responses
echo - Record voice messages (with FFmpeg)
echo - Try voice cloning
echo - Test WebRTC voice calls
echo.
echo To stop: Close all command windows
echo.
pause