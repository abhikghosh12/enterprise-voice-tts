@echo off
echo Starting Ollama...
start "Ollama" cmd /k "ollama serve"
timeout /t 3 >nul

echo Starting Voice TTS...
start "Voice TTS" cmd /k "python ollama_api_server.py"
timeout /t 5 >nul

echo Starting WebRTC Center...
start "WebRTC" cmd /k "python webrtc_voice_center.py"
timeout /t 3 >nul

echo Opening browsers...
start http://localhost:8000
start http://localhost:8001

echo All services started!
pause