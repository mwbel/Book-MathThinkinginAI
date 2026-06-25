#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

DEFAULT_RENDER="${REVIEW_DIR}/outputs/1-Def.v1__plain__polished_unified_expanded-render.html"
LATEST_RENDER="$(find "${REVIEW_DIR}/outputs" -maxdepth 1 -name '*-render.html' -type f -print0 | xargs -0 ls -t 2>/dev/null | head -n 1 || true)"
if [[ -f "${DEFAULT_RENDER}" ]]; then
  DEFAULT_PAGE="${DEFAULT_RENDER}"
else
  DEFAULT_PAGE="${LATEST_RENDER:-${DEFAULT_RENDER}}"
fi
TARGET_PAGE="${TARGET_PAGE:-${1:-${DEFAULT_PAGE}}}"

if [[ ! -f "${TARGET_PAGE}" ]]; then
  echo "target page not found: ${TARGET_PAGE}" >&2
  exit 1
fi

if command -v open >/dev/null 2>&1; then
  open "${TARGET_PAGE}"
else
  echo "${TARGET_PAGE}"
fi
