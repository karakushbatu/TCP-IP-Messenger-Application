#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APP_NAME="Protocol Bridge"

echo "Cleaning previous build artifacts..."
rm -rf build/pyinstaller dist dist-new "${APP_NAME}.spec"

echo "Building macOS application..."
pyinstaller --noconfirm --clean \
  --onefile --windowed \
  --name "$APP_NAME" \
  --paths . \
  --collect-all customtkinter \
  --add-data "assets:assets" \
  --hidden-import "src.app" \
  --hidden-import "src.app_info" \
  --hidden-import "src.instance" \
  --hidden-import "src.instance_manager" \
  src/main.py

cd dist
APP_BUNDLE="${APP_NAME}.app"

if [[ ! -d "$APP_BUNDLE" ]]; then
  echo "ERROR: Expected $APP_BUNDLE not found in dist/"
  ls -la
  exit 1
fi

echo "Creating DMG installer..."
rm -f "Protocol-Bridge-macOS.dmg" "Protocol-Bridge-macOS.zip"

hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$APP_BUNDLE" \
  -ov \
  -format UDZO \
  "Protocol-Bridge-macOS.dmg"

zip -r "Protocol-Bridge-macOS.zip" "$APP_BUNDLE"

echo ""
echo "Build complete:"
ls -lh "Protocol-Bridge-macOS.dmg" "Protocol-Bridge-macOS.zip"
