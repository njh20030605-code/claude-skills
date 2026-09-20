#!/bin/bash
# 把 ~/.claude/skills/synced 里我自己写的 skill 同步进本仓库（分类目录固定在下面的映射里）。
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; SK="$HOME/.claude/skills/synced"
X=(--exclude .DS_Store --exclude '._*' --exclude __pycache__)
S() { rsync -a --delete "${X[@]}" "$SK/$2/" "$R/$1/$2/"; }
for s in kans-livestream-charts kans-vn-category-competition kans-vn-weekly-flow kans-vn-high-cost-low-roi-hourly tiktok-brand-upper-funnel ttms-audience-package-strategy; do S kans-analysis $s; done
for s in kans-ttms-cads-report-batch tiktok-batch-budget-update tiktok-batch-exclude-creators tiktok-copy-adgroup-swap-creative tiktok-creative-id-to-creator; do S tiktok-automation $s; done
S data-cleaning tkshop-daren-cleaning; S live-script vn-kans-script; S feishu feishu-docs; S personal touji-zhilu-playbook
cd "$R" && git status --short
bash "$R/scrub.sh"
