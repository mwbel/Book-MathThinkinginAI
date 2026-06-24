#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REVIEW_DIR}"

usage() {
  cat <<'EOF'
Usage:
  push_review.sh [remote-name-or-url] [branch]

Examples:
  push_review.sh                  # push current branch to preferred remote (polish -> origin)
  push_review.sh polish            # push current branch to remote polish
  push_review.sh polish book-refine
  push_review.sh https://github.com/mwbel/Book-AI-Polish.git
EOF
}

REMOTE_OR_URL="${1:-}"
BRANCH="${2:-$(git rev-parse --abbrev-ref HEAD)}"

resolve_remote_url() {
  local target="$1"
  if [[ -z "${target}" ]]; then
    if git remote | rg -q '^polish$'; then
      echo polish
      return 0
    fi
    if git remote | rg -q '^origin$'; then
      echo origin
      return 0
    fi
    return 1
  fi

  if git remote | rg -q "^${target}$"; then
    echo "${target}"
    return 0
  fi

  if [[ "${target}" == http*://* ]]; then
    echo "${target}"
    return 0
  fi

  return 1
}

REMOTE_OR_URL="$(resolve_remote_url "${REMOTE_OR_URL}")"
if [[ -z "${REMOTE_OR_URL}" ]]; then
  echo "No valid remote specified. Example: push_review.sh <polish|origin|https://...> [branch]" >&2
  usage
  exit 1
fi

if [[ -z "${BRANCH}" ]]; then
  echo "Failed to resolve current branch. Please pass branch explicitly." >&2
  exit 1
fi

echo "Repository : ${REVIEW_DIR}"
echo "Branch    : ${BRANCH}"
echo "Remote    : ${REMOTE_OR_URL}"

attempt_push() {
  local remote_spec="$1"
  git push "${remote_spec}" "HEAD:${BRANCH}"
}

to_https_url() {
  local remote_url="$1"
  if [[ "${remote_url}" =~ ^https:// ]]; then
    echo "${remote_url}"
    return 0
  fi
  if [[ "${remote_url}" =~ ^git@([^:]+):(.+)(\.git)?$ ]]; then
    local host="${BASH_REMATCH[1]}"
    local path="${BASH_REMATCH[2]}"
    if [[ "${path}" != *.git ]]; then
      path="${path}.git"
    fi
    echo "https://${host}/${path}"
    return 0
  fi
  if [[ "${remote_url}" =~ ^ssh://([^/]+)/(.+)(\.git)?$ ]]; then
    local host="${BASH_REMATCH[1]}"
    local path="${BASH_REMATCH[2]}"
    if [[ "${path}" != *.git ]]; then
      path="${path}.git"
    fi
    echo "https://${host}/${path}"
    return 0
  fi
  return 1
}

if [[ "${REMOTE_OR_URL}" == http*://* ]]; then
  echo "Try push via HTTPS URL..."
  attempt_push "${REMOTE_OR_URL}" && exit 0
else
  SSH_URL="$(git remote get-url "${REMOTE_OR_URL}")"
  echo "Try push via SSH remote: ${REMOTE_OR_URL} (${SSH_URL})"
  if attempt_push "${REMOTE_OR_URL}"; then
    exit 0
  fi
fi

echo "SSH push failed, fallback to HTTPS..."

HTTPS_URL="$(to_https_url "${SSH_URL:-${REMOTE_OR_URL}}")" || {
  echo "Unable to convert remote to HTTPS, skipping fallback." >&2
  exit 1
}

if [[ -n "${GITHUB_TOKEN:-${GH_TOKEN:-}}" ]]; then
  TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
  HTTPS_URL_AUTH="$(sed "s#https://#https://${TOKEN}@#;s#https://##" <<< "${HTTPS_URL}")"
  HTTPS_URL_AUTH="https://${TOKEN}@${HTTPS_URL#https://}"
else
  HTTPS_URL_AUTH="${HTTPS_URL}"
  if command -v zsh >/dev/null 2>&1 && [[ -t 0 ]]; then
    printf "GitHub token not set (GITHUB_TOKEN/GH_TOKEN). Enter token for HTTPS fallback (optional): "
    read -r -s HTTPS_TOKEN_INPUT
    echo
    if [[ -n "${HTTPS_TOKEN_INPUT}" ]]; then
      HTTPS_URL_AUTH="https://${HTTPS_TOKEN_INPUT}@${HTTPS_URL#https://}"
    fi
  fi
fi

if attempt_push "${HTTPS_URL_AUTH}"; then
  exit 0
fi

echo "HTTPS fallback also failed. Suggest set one token and retry:"
echo "  export GITHUB_TOKEN=your_personal_access_token"
echo "  ./tools/review/scripts/push_review.sh polish ${BRANCH}"
echo "or run manual token-less interactive fallback via:"
echo "  git push https://github.com/mwbel/Book-AI-Polish.git HEAD:${BRANCH}"
exit 1
