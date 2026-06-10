@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0\.."

set EXE_NAME=Protocol Bridge

echo Stopping running instances...
powershell -NoProfile -Command "Get-Process -Name 'Protocol Bridge','TCP Tactical Messenger','Protokol Köprüsü' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"

echo Cleaning all previous build artifacts...
if exist dist rmdir /s /q dist
if exist dist-new rmdir /s /q dist-new
for /d %%D in (build\*) do rmdir /s /q "%%D" 2>nul
del /q "TCP Tactical Messenger.spec" 2>nul
del /q "Protokol Köprüsü.spec" 2>nul
for %%F in (*.spec) do if /I not "%%~nF"=="%EXE_NAME%" del /q "%%F" 2>nul

echo Building Windows executable...
pyinstaller --noconfirm --clean ^
  --onefile --windowed ^
  --name "%EXE_NAME%" ^
  --paths . ^
  --collect-all customtkinter ^
  --add-data "assets;assets" ^
  --hidden-import "src.app" ^
  --hidden-import "src.app_info" ^
  --hidden-import "src.instance" ^
  --hidden-import "src.instance_manager" ^
  src\main.py

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo Creating ZIP archive...
cd dist
if exist "Protocol-Bridge-Windows.zip" del /q "Protocol-Bridge-Windows.zip"
powershell -NoProfile -Command "Compress-Archive -LiteralPath '%EXE_NAME%.exe' -DestinationPath 'Protocol-Bridge-Windows.zip' -Force"

echo.
echo Build complete:
echo   dist\%EXE_NAME%.exe
echo   dist\Protocol-Bridge-Windows.zip
