#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8766}"

"${SCRIPT_DIR}/build_review_frontend.sh" "$@"

echo
echo "Starting local review server..."
"${SCRIPT_DIR}/start_review_backend.sh" &
BACKEND_PID=$!

cleanup() {
  kill "${BACKEND_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 2

TARGET_PAGE="${TARGET_PAGE:-http://${HOST}:${PORT}/ch12-clean-render.html}"
if command -v open >/dev/null 2>&1; then
  open "${TARGET_PAGE}"
else
  echo "${TARGET_PAGE}"
fi

wait "${BACKEND_PID}"
