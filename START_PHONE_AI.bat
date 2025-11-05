@echo off
echo Starting Phone AI System...

REM Start main TTS server
start "TTS Server" cmd /k "cd /d c:\git\enterprise-voice-tts && python ollama_api_server.py"

REM Wait 3 seconds
timeout /t 3 /nobreak >nul

REM Start Twilio server
start "Twilio Server" cmd /k "cd /d c:\git\enterprise-voice-tts\voice-ai-agent && python twilio_server.py"

REM Start ngrok tunnel
start "Ngrok" cmd /k "ngrok http 8080"

echo.
echo ========================================
echo Phone AI System Started!
echo ========================================
echo.
echo 1. Copy ngrok URL from ngrok window
echo 2. Update .env file with ngrok URL
echo 3. Configure Twilio webhook
echo 4. Call your Twilio number!
echo.
pause