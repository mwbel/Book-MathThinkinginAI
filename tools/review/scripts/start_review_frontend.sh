#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

TARGET_PAGE="${TARGET_PAGE:-${1:-${REVIEW_DIR}/outputs/ch12-clean-render.html}}"

if [[ ! -f "${TARGET_PAGE}" ]]; then
  echo "target page not found: ${TARGET_PAGE}" >&2
  exit 1
fi

if command -v open >/dev/null 2>&1; then
  open "${TARGET_PAGE}"
else
  echo "${TARGET_PAGE}"
fi

