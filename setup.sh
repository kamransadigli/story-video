#!/usr/bin/env bash
# One-time setup: Python packages + the free Kokoro voice model (~350 MB).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
mkdir -p models
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -f "models/$f" ] || curl -L -o "models/$f" "$base/$f"
done
command -v ffmpeg >/dev/null || echo "WARNING: ffmpeg not found - install it (brew install ffmpeg / apt install ffmpeg)"
node -e "require('playwright')" 2>/dev/null || echo "NOTE: run 'npm install' then 'npx playwright install chromium' to draw SVG scenes"
echo "Setup done. Try: python3 -m storyvideo stories/phantom-of-heilbronn"
