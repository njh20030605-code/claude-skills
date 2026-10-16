#!/bin/bash
# 公开仓库脱敏：sync-from-local.sh 每次同步后自动跑。
#   1. 第三方频道全文存档不再分发，只保留方法论摘要
#   2. 2026-10 新增 skill 里的内部系统、飞书 token、同事名、真实 ID 换成通用写法
#      具体替换规则在本机 scrub.local.py（不提交：规则里本身就含要删的原文）
#   3. 最后整体扫一遍，残留就报错退出，不让它进 commit
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"

# ── 1. touji-zhilu：删全文存档 ───────────────────────────────────
rm -f "$R/personal/touji-zhilu-playbook/references/posts.json" "$R/personal/touji-zhilu-playbook/references/archive.md"
cat > "$R/personal/touji-zhilu-playbook/references/NOTE.md" <<'N'
公开仓库不包含 `posts.json`（频道帖子全文存档）和 `archive.md`（按时间线整理的原帖），它们是第三方内容，只保留在本机。
这里保留的 `methodology.md` 是我自己归纳的方法论摘要。要在本机使用完整检索能力，把本地存档放回本目录即可。
N

# ── 2. 新 skill 的内部信息 ───────────────────────────────────────
# 依赖内部接口的取数脚本不公开：scrub.local.py 里的 DROP 列表

python3 - "$R" <<'PY'
import pathlib, re, sys
R = pathlib.Path(sys.argv[1])

LOCAL = R / 'scrub.local.py'
if not LOCAL.exists():
    sys.exit('❌ 缺少 scrub.local.py（本机脱敏规则，不入库）。没有它不能同步，否则内部信息会原样公开。')
exec(LOCAL.read_text(encoding='utf-8'))   # 定义 DROP / RULES / BAD
for rel in DROP:
    (R / rel).unlink(missing_ok=True)
EXT = {'.md', '.py', '.js', '.svg', '.csv', '.json', '.txt'}
for d, rules in RULES.items():
    for f in (R / d).rglob('*'):
        if not f.is_file() or f.suffix not in EXT:
            continue
        s0 = s = f.read_text(encoding='utf-8-sig' if f.suffix == '.csv' else 'utf-8')
        for pat, rep in rules:
            s = re.sub(pat, rep, s)
        if s != s0:
            f.write_text(s, encoding='utf-8')

# ── 3. 残留扫描（BAD 规则同样在 scrub.local.py）──
NEW = ['content/video-breakdown-doc', 'feishu/gsheet-to-feishu-base-migration',
       'kans-analysis/kans-cads-summary-table', 'kans-analysis/tiktok-brand-ads-analysis']
hits = []
for d in NEW:
    for f in (R / d).rglob('*'):
        if f.is_file() and f.suffix in EXT:
            for i, line in enumerate(f.read_text(encoding='utf-8-sig').splitlines(), 1):
                for pat, why in BAD:
                    if re.search(pat, line):
                        hits.append(f'  {f.relative_to(R)}:{i}  [{why}]  {line.strip()[:90]}')
if hits:
    print('❌ 脱敏后仍有残留：'); print('\n'.join(hits)); sys.exit(1)
PY
echo "✅ scrub ok"
