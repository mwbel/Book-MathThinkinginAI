#!/usr/bin/env bash
set -euo pipefail

cd "/Users/Min369/Desktop/书/书稿打磨"

if lsof -nP -iTCP:8766 -sTCP:LISTEN >/dev/null 2>&1; then
  lsof -tiTCP:8766 -sTCP:LISTEN | xargs kill -9
  sleep 1
fi

python3 tools/review/synctex_review_server.py \
  --root tools/review/outputs \
  --host 127.0.0.1 \
  --port 8766
