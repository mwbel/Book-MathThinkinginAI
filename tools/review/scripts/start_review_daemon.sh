#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8766}"
STATIC_ROOT="${STATIC_ROOT:-${REVIEW_DIR}/outputs}"
LOG_FILE="${LOG_FILE:-${REVIEW_DIR}/outputs/review-server.log}"
RESTART_EXISTING="${RESTART_EXISTING:-1}"
DEFAULT_RENDER="${STATIC_ROOT}/1-Def.v1__plain__polished_unified_expanded-render.html"
LATEST_RENDER="$(find "${STATIC_ROOT}" -maxdepth 1 -name '*-render.html' -type f -print0 | xargs -0 ls -t 2>/dev/null | head -n 1 || true)"
if [[ -f "${DEFAULT_RENDER}" ]]; then
  PAGE_NAME="$(basename "${DEFAULT_RENDER}")"
elif [[ -n "${LATEST_RENDER}" ]]; then
  PAGE_NAME="$(basename "${LATEST_RENDER}")"
else
  PAGE_NAME="1-Def.v1__plain__polished_unified_expanded-render.html"
fi
URL="http://${HOST}:${PORT}/${PAGE_NAME}"

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  if [[ "${RESTART_EXISTING}" == "1" ]]; then
    lsof -tiTCP:"${PORT}" -sTCP:LISTEN | xargs kill -9
    sleep 1
  else
    echo "Review server already running: ${URL}"
    if command -v open >/dev/null 2>&1; then
      open "${URL}"
    fi
    exit 0
  fi
fi

nohup python3 "${REVIEW_DIR}/synctex_review_server.py" \
  --root "${STATIC_ROOT}" \
  --host "${HOST}" \
  --port "${PORT}" \
  >"${LOG_FILE}" 2>&1 &
SERVER_PID=$!
disown "${SERVER_PID}" 2>/dev/null || true
echo "Started review server PID ${SERVER_PID}"
sleep 1

if ! curl -fsS -I "${URL}" >/dev/null; then
  echo "Review server did not respond. Log: ${LOG_FILE}" >&2
  tail -40 "${LOG_FILE}" >&2 || true
  exit 1
fi

echo "Open: ${URL}"
if command -v open >/dev/null 2>&1; then
  open "${URL}"
fi
