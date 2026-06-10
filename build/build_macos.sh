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

if [[ -d "TCP Tactical Messenger.app" ]]; then
  rm -f "TCP-Tactical-Messenger-macOS.zip"
  zip -r "TCP-Tactical-Messenger-macOS.zip" "TCP Tactical Messenger.app"
elif [[ -f "TCP Tactical Messenger" ]]; then
  rm -f "TCP-Tactical-Messenger-macOS.zip"
  zip -j "TCP-Tactical-Messenger-macOS.zip" "TCP Tactical Messenger"
else
  echo "ERROR: Expected app bundle or binary not found in dist/"
  ls -la
  exit 1
fi

echo ""
echo "Build complete:"
ls -lh "TCP-Tactical-Messenger-macOS.zip"
