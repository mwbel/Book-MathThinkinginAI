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

LATEST_RENDER="$(find "${REVIEW_DIR}/outputs" -maxdepth 1 -name '*-render.html' -type f -print0 | xargs -0 ls -t 2>/dev/null | head -n 1 || true)"
if [[ -n "${LATEST_RENDER}" ]]; then
  TARGET_PAGE="${TARGET_PAGE:-http://${HOST}:${PORT}/$(basename "${LATEST_RENDER}")}"
else
  TARGET_PAGE="${TARGET_PAGE:-http://${HOST}:${PORT}/1-Def.v1__plain__polished_unified_expanded-render.html}"
fi
if command -v open >/dev/null 2>&1; then
  open "${TARGET_PAGE}"
else
  echo "${TARGET_PAGE}"
fi

wait "${BACKEND_PID}"
