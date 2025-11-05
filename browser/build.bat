@echo off
echo ====================================
echo Building Enterprise Voice Browser
echo ====================================
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies first...
    call npm install
    echo.
)

echo Building Windows installer...
call npm run build:win

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo Build completed successfully!
    echo ====================================
    echo.
    echo Installer location: dist\
    echo.
    pause
) else (
    echo.
    echo Build failed! Check the errors above.
    echo.
    pause
)
