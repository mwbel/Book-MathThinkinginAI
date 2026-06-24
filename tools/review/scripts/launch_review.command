#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
URL="http://127.0.0.1:8766/ch12-clean-render.html"

echo "Starting review server..."
"${SCRIPT_DIR}/start_review_backend.sh" &
SERVER_PID=$!

sleep 1
open "${URL}"

echo
echo "Review page:"
echo "${URL}"
echo
echo "Keep this Terminal window open while using the review page."
echo "Press Control-C here to stop the server."

wait "${SERVER_PID}"

