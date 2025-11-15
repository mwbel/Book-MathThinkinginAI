#!/usr/bin/env bash
set -euo pipefail
mkdir -p diffs

for newf in chapters/*.refined_unified.tex; do
  [ -e "$newf" ] || continue
  base="$(basename "$newf" .refined_unified.tex)"
  oldf="chapters/${base}.refined.tex"
  patch="diffs/${base}.patch"

  if [ -f "$oldf" ]; then
    git diff --no-index -- "$oldf" "$newf" > "$patch" || true
    echo "✅ 生成差异：$patch   （$oldf ⇄ $newf）"
  else
    echo "⚠️ 缺少原稿：$oldf"
  fi
done
