@echo off
echo ========================================
echo Starting Enterprise Voice Browser
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo node_modules not found. Running setup...
    call setup-browser.bat
    if errorlevel 1 exit /b 1
)

REM Check Ollama
echo Checking Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Ollama is not running!
    echo Please run: ollama serve
    echo.
    echo Starting browser anyway...
    echo (You can configure Ollama endpoint in Settings)
    echo.
    timeout /t 3
)

echo Starting browser...
npm start
