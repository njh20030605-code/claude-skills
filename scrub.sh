#!/bin/bash
# 公开仓库脱敏：第三方频道全文存档不再分发，只保留方法论摘要。
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"
rm -f "$R/personal/touji-zhilu-playbook/references/posts.json" "$R/personal/touji-zhilu-playbook/references/archive.md"
cat > "$R/personal/touji-zhilu-playbook/references/NOTE.md" <<'N'
公开仓库不包含 `posts.json`（频道帖子全文存档）和 `archive.md`（按时间线整理的原帖），它们是第三方内容，只保留在本机。
这里保留的 `methodology.md` 是我自己归纳的方法论摘要。要在本机使用完整检索能力，把本地存档放回本目录即可。
N
echo "✅ scrub ok"
