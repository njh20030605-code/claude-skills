#!/bin/bash
# 把 ~/.claude/skills/synced 里的 skill 同步进本仓库。
#
# ⚠️ 重要：下面分成两组。
#   GENERIC  —— 已经在本仓库里通用化过（业务参数抽成占位符 / 示例数据）的 skill。
#               它们的本机版本仍是 KANS 专用的，同步过来会把通用化成果冲掉，
#               所以**不同步**，直接在本仓库维护。本机改了功能想合过来，手工 diff。
#   MIRROR   —— 本身就不含业务数据的 skill，本机是唯一真源，照常同步。
#
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; SK="$HOME/.claude/skills/synced"
X=(--exclude .DS_Store --exclude '._*' --exclude __pycache__)
S() { rsync -a --delete "${X[@]}" "$SK/$2/" "$R/$1/$2/"; }

# ── 不同步：已通用化，仓库版才是真源 ──────────────────────────────
GENERIC=(
  kans-analysis/kans-livestream-charts
  kans-analysis/kans-vn-category-competition
  kans-analysis/kans-vn-weekly-flow
  kans-analysis/kans-vn-high-cost-low-roi-hourly
  kans-analysis/tiktok-vn-kans-live-ops
  kans-analysis/ttms-audience-package-strategy
  tiktok-automation/kans-ttms-cads-report-batch
  live-script/vn-kans-script
)
printf '跳过（已通用化，仓库版为真源）：\n'; printf '  %s\n' "${GENERIC[@]}"

# ── 照常同步：不含业务数据 ────────────────────────────────────────
S kans-analysis tiktok-brand-upper-funnel
for s in tiktok-batch-budget-update tiktok-batch-exclude-creators tiktok-copy-adgroup-swap-creative tiktok-creative-id-to-creator; do
  S tiktok-automation "$s"
done
S data-cleaning tkshop-daren-cleaning
S feishu feishu-docs
S personal touji-zhilu-playbook

bash "$R/scrub.sh"
cd "$R" && git status --short
