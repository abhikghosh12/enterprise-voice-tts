@echo off
echo Downloading FFmpeg...
curl -L "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -o ffmpeg.zip

echo Extracting FFmpeg...
powershell -command "Expand-Archive -Path ffmpeg.zip -DestinationPath . -Force"

echo Moving FFmpeg to C:\ffmpeg...
move ffmpeg-master-latest-win64-gpl C:\ffmpeg

echo Adding to PATH...
setx PATH "%PATH%;C:\ffmpeg\bin" /M

echo Cleaning up...
del ffmpeg.zip

echo FFmpeg installed! Restart your terminal.
pause