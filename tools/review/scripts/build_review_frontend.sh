#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${REVIEW_DIR}/../.." && pwd)"

CHAPTERS_DEFAULT="${PROJECT_ROOT}/draft-tex-3扩写/chapters-20251105"
SOURCE_DEFAULT="${CHAPTERS_DEFAULT}/12-语言中的智能：Transformer的意外胜利.v3_refined.tex"
TARGET_DEFAULT="${CHAPTERS_DEFAULT}/12-语言中的智能：Transformer的意外胜利.v3.tex"

SOURCE_PATH="${SOURCE_PATH:-${1:-${SOURCE_DEFAULT}}}"
TARGET_PATH="${TARGET_PATH:-${2:-${TARGET_DEFAULT}}}"
REVIEW_NAME="${REVIEW_NAME:-${3:-ch12-clean}}"
REVIEW_TITLE="${REVIEW_TITLE:-${4:-第12章 清洗校对稿}}"
OUTPUT_DIR="${OUTPUT_DIR:-${REVIEW_DIR}/outputs}"
TEX_ROOT="${TEX_ROOT:-${PROJECT_ROOT}/draft-tex-3扩写}"

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
