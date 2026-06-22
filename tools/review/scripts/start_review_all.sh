#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/build_review_frontend.sh" "$@"

echo
echo "Starting local review server..."
exec "${SCRIPT_DIR}/start_review_backend.sh"
