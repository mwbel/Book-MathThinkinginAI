#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8766}"
STATIC_ROOT="${STATIC_ROOT:-${REVIEW_DIR}/outputs}"
LOG_FILE="${LOG_FILE:-${REVIEW_DIR}/outputs/review-server.log}"
URL="http://${HOST}:${PORT}/ch12-clean-render.html"

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Review server already running: ${URL}"
else
  nohup python3 "${REVIEW_DIR}/synctex_review_server.py" \
    --root "${STATIC_ROOT}" \
    --host "${HOST}" \
    --port "${PORT}" \
    >"${LOG_FILE}" 2>&1 &
  SERVER_PID=$!
  echo "Started review server PID ${SERVER_PID}"
  sleep 1
fi

if ! curl -fsS -I "${URL}" >/dev/null; then
  echo "Review server did not respond. Log: ${LOG_FILE}" >&2
  tail -40 "${LOG_FILE}" >&2 || true
  exit 1
fi

echo "Open: ${URL}"
if command -v open >/dev/null 2>&1; then
  open "${URL}"
fi

