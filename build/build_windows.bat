@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0\.."

set EXE_NAME=Protocol Bridge

echo Cleaning previous build artifacts...
if exist build\pyinstaller rmdir /s /q build\pyinstaller
if exist dist rmdir /s /q dist
if exist dist-new rmdir /s /q dist-new
if exist "%EXE_NAME%.spec" del /q "%EXE_NAME%.spec"

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
