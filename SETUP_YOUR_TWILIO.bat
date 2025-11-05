@echo off
echo ========================================
echo Setting up YOUR Twilio Phone AI
echo ========================================
echo.

REM Install Twilio dependencies
echo Installing Twilio dependencies...
pip install twilio python-dotenv

REM Create environment file
echo Creating .env file...
cd voice-ai-agent
if not exist .env (
    echo TWILIO_ACCOUNT_SID=your_account_sid_here > .env
    echo TWILIO_AUTH_TOKEN=your_auth_token_here >> .env
    echo TWILIO_PHONE_NUMBER=+1234567890 >> .env
    echo WEBHOOK_BASE_URL=your-ngrok-url.ngrok.io >> .env
    echo TTS_API_URL=http://localhost:8000 >> .env
)

echo.
echo ========================================
echo SETUP STEPS:
echo ========================================
echo.
echo 1. Go to twilio.com and create account
echo 2. Get Account SID and Auth Token
echo 3. Buy a phone number
echo 4. Edit voice-ai-agent\.env file with your details
echo 5. Run START_PHONE_SYSTEM.bat
echo.
pause