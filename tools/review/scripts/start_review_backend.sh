#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8766}"
STATIC_ROOT="${STATIC_ROOT:-${REVIEW_DIR}/outputs}"

python3 "${REVIEW_DIR}/synctex_review_server.py" \
  --root "${STATIC_ROOT}" \
  --host "${HOST}" \
  --port "${PORT}"
