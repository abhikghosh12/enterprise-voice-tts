@echo off
echo ========================================
echo Enterprise Voice Browser - Setup
echo ========================================
echo.

echo [1/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please download and install from: https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js found:
node --version

echo.
echo [2/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama is not running or not installed
    echo.
    echo To install Ollama:
    echo 1. Download from: https://ollama.ai/download
    echo 2. Run: ollama serve
    echo 3. Run: ollama pull llama3.2
    echo.
    echo Continuing anyway...
) else (
    echo Ollama is running!
)

echo.
echo [3/4] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Make sure Ollama is running: ollama serve
echo 2. Pull a model: ollama pull llama3.2
echo 3. Start the browser: npm start
echo.
echo Or simply run: start-browser.bat
echo ========================================
echo.
pause
