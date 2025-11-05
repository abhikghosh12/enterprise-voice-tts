@echo off
echo ========================================
echo Ollama Connection Diagnostics
echo ========================================
echo.

echo [1] Checking Ollama Service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama is NOT running on localhost:11434
    echo.
    echo Please run: ollama serve
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Ollama is running on localhost:11434
)

echo.
echo [2] Checking for models...
curl -s http://localhost:11434/api/tags 2>nul | findstr "name"
if errorlevel 1 (
    echo ❌ No models found
    echo.
    echo Please run: ollama pull llama3.2:1b
) else (
    echo.
    echo ✅ Models found!
)

echo.
echo [3] Testing Ollama chat API...
curl -X POST http://localhost:11434/api/generate -d "{\"model\": \"llama3.2:1b\", \"prompt\": \"Say hi\", \"stream\": false}" 2>nul >nul
if errorlevel 1 (
    echo ❌ Chat API test failed
) else (
    echo ✅ Chat API working
)

echo.
echo [4] Checking if browser can access Ollama...
echo This requires the browser to be running.
echo If you see "⚫ Ollama" in the browser status bar:
echo   - Click the ⚙️ Settings button
echo   - Make sure endpoint is: http://localhost:11434
echo   - Click "Test Connection"
echo   - Click "Save Settings"

echo.
echo ========================================
echo Summary:
echo ========================================
echo If Ollama is running but browser shows ⚫:
echo.
echo 1. Open the browser
echo 2. Click ⚙️ Settings in top-right
echo 3. Verify endpoint: http://localhost:11434
echo 4. Click "Test Connection"
echo 5. Click "Save Settings"
echo 6. Refresh the browser (F5)
echo.
echo ========================================
pause
