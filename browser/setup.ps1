# Enterprise Voice Browser Setup Script
# Run this in PowerShell as Administrator

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Enterprise Voice Browser Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "Checking for Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Write-Host "Press any key to open the Node.js website..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Start-Process "https://nodejs.org/"
    exit 1
}

# Check if Ollama is installed
Write-Host "Checking for Ollama..." -ForegroundColor Yellow
$ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaPath) {
    Write-Host "✓ Ollama found" -ForegroundColor Green
    
    # Check if Ollama service is running
    $ollamaRunning = Test-NetConnection -ComputerName localhost -Port 11434 -InformationLevel Quiet 2>$null
    if ($ollamaRunning) {
        Write-Host "✓ Ollama service is running" -ForegroundColor Green
    } else {
        Write-Host "! Ollama is installed but not running" -ForegroundColor Yellow
        Write-Host "Starting Ollama service..." -ForegroundColor Yellow
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }
    
    # Check for models
    Write-Host "Checking for installed models..." -ForegroundColor Yellow
    $models = ollama list 2>$null
    if ($models -match "llama3.2") {
        Write-Host "✓ llama3.2 model found" -ForegroundColor Green
    } else {
        Write-Host "! No models found. Pulling llama3.2..." -ForegroundColor Yellow
        ollama pull llama3.2
    }
} else {
    Write-Host "✗ Ollama not found!" -ForegroundColor Red
    Write-Host "Please install Ollama from https://ollama.ai/" -ForegroundColor Red
    Write-Host "Press any key to open the Ollama website..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Start-Process "https://ollama.ai/"
    exit 1
}

Write-Host ""
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application, run:" -ForegroundColor Yellow
Write-Host "  npm start" -ForegroundColor White
Write-Host ""
Write-Host "To build the application, run:" -ForegroundColor Yellow
Write-Host "  npm run build:win" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to start the application now..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

npm start
