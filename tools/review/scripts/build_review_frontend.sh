#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${REVIEW_DIR}/../.." && pwd)"

CHAPTERS_DEFAULT="${PROJECT_ROOT}/draft-tex-4-codex/chapters/ch1"
SOURCE_DEFAULT="${CHAPTERS_DEFAULT}/1-Def.v1.tex"
TARGET_DEFAULT="${CHAPTERS_DEFAULT}/1-Def.v1_polished_unified_expanded.tex"

SOURCE_PATH="${SOURCE_PATH:-${1:-${SOURCE_DEFAULT}}}"
TARGET_PATH="${TARGET_PATH:-${2:-${TARGET_DEFAULT}}}"
REVIEW_NAME="${REVIEW_NAME:-${3:-1-Def.v1__plain__polished_unified_expanded}}"
REVIEW_TITLE="${REVIEW_TITLE:-${4:-第1章 定义与智能校对页}}"
OUTPUT_DIR="${OUTPUT_DIR:-${REVIEW_DIR}/outputs}"
TEX_ROOT="${TEX_ROOT:-${PROJECT_ROOT}/draft-tex-4-codex}"

python3 "${REVIEW_DIR}/run_review.py" \
  --source "${SOURCE_PATH}" \
  --target "${TARGET_PATH}" \
  --name "${REVIEW_NAME}" \
  --title "${REVIEW_TITLE}" \
  --output-dir "${OUTPUT_DIR}" \
  --project-root "${PROJECT_ROOT}" \
  --tex-root "${TEX_ROOT}" \
  --pretty \
  --build-pdf-preview

echo
echo "Frontend artifacts generated:"
echo "  ${OUTPUT_DIR}/${REVIEW_NAME}-review.html"
echo "  ${OUTPUT_DIR}/${REVIEW_NAME}-render.html"
