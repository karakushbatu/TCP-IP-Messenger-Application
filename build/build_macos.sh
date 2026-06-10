#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Cleaning previous build artifacts..."
rm -rf build/pyinstaller dist "TCP Tactical Messenger.spec"

echo "Building macOS application..."
pyinstaller --noconfirm --clean \
  --onefile --windowed \
  --name "TCP Tactical Messenger" \
  --paths . \
  --collect-all customtkinter \
  --add-data "assets:assets" \
  --hidden-import "src.app" \
  --hidden-import "src.instance" \
  --hidden-import "src.instance_manager" \
  src/main.py

cd dist
APP_NAME="TCP Tactical Messenger.app"
VOLUME_NAME="TCP Tactical Messenger"

if [[ ! -d "$APP_NAME" ]]; then
  echo "ERROR: Expected $APP_NAME not found in dist/"
  ls -la
  exit 1
fi

echo "Creating DMG installer..."
rm -f "TCP-Tactical-Messenger-macOS.dmg" "TCP-Tactical-Messenger-macOS.zip"

# Primary macOS distribution: DMG
hdiutil create \
  -volname "$VOLUME_NAME" \
  -srcfolder "$APP_NAME" \
  -ov \
  -format UDZO \
  "TCP-Tactical-Messenger-macOS.dmg"

# Optional ZIP fallback for automation-restricted environments
zip -r "TCP-Tactical-Messenger-macOS.zip" "$APP_NAME"

echo ""
echo "Build complete:"
ls -lh "TCP-Tactical-Messenger-macOS.dmg" "TCP-Tactical-Messenger-macOS.zip"
