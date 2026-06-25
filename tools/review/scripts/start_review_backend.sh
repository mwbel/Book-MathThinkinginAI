#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8766}"
STATIC_ROOT="${STATIC_ROOT:-${REVIEW_DIR}/outputs}"
RESTART_EXISTING="${RESTART_EXISTING:-1}"

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  if [[ "${RESTART_EXISTING}" == "1" ]]; then
    lsof -tiTCP:"${PORT}" -sTCP:LISTEN | xargs kill -9
    sleep 1
  else
    echo "Review server already running on ${HOST}:${PORT}. Set RESTART_EXISTING=1 to restart it." >&2
    exit 1
  fi
fi

python3 "${REVIEW_DIR}/synctex_review_server.py" \
  --root "${STATIC_ROOT}" \
  --host "${HOST}" \
  --port "${PORT}"
