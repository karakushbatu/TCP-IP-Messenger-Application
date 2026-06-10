@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0\.."

echo Cleaning previous build artifacts...
if exist build\pyinstaller rmdir /s /q build\pyinstaller
if exist dist rmdir /s /q dist
if exist "TCP Tactical Messenger.spec" del /q "TCP Tactical Messenger.spec"

echo Building Windows executable...
pyinstaller --noconfirm --clean ^
  --onefile --windowed ^
  --name "TCP Tactical Messenger" ^
  --paths . ^
  --collect-all customtkinter ^
  --add-data "assets;assets" ^
  --hidden-import "src.app" ^
  --hidden-import "src.instance" ^
  --hidden-import "src.instance_manager" ^
  src\main.py

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo Creating ZIP archive...
cd dist
if exist "TCP-Tactical-Messenger-Windows.zip" del /q "TCP-Tactical-Messenger-Windows.zip"
powershell -NoProfile -Command "Compress-Archive -Path 'TCP Tactical Messenger.exe' -DestinationPath 'TCP-Tactical-Messenger-Windows.zip' -Force"

echo.
echo Build complete:
echo   dist\TCP Tactical Messenger.exe
echo   dist\TCP-Tactical-Messenger-Windows.zip
