@echo off
echo ============================================================
echo   ENTERPRISE VOICE TTS PLATFORM
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

echo Starting Ollama Voice TTS Platform...
echo.
echo Make sure Ollama is running:
echo   ollama serve
echo   ollama pull llama3.2:1b
echo.
echo Starting server on http://localhost:8000
echo.

python ollama_api_server.py

pause