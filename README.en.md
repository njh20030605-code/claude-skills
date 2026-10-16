<div align="center">

# Claude Skills · 自写 Claude 技能合集

**21 hand-written skills for Claude Code / Claude in Chrome / claude.ai — weekly reviews, brand ads & audiences, TikTok Ads browser automation, short-video creative breakdowns, Google Sheets → Feishu migration.**

[中文](README.md) | English

![Claude Code](https://img.shields.io/badge/Claude-Code%20%7C%20in%20Chrome%20%7C%20claude.ai-D97757?logo=anthropic&logoColor=white)
![Skills](https://img.shields.io/badge/skills-21-blue)
![Domain](https://img.shields.io/badge/domain-TikTok%20Shop%20Vietnam-000000?logo=tiktok&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

</div>

Each skill is a folder with a `SKILL.md` entry point (the frontmatter `name` / `description` decides when it triggers; the body is the playbook) plus optional `scripts/`, `references/`, `examples/`. Most skills are written for the **KANS (韩束) Vietnam TikTok Shop** context: FX ₫3,860 ≈ ¥1, primary KPI = livestream GMV + product-card GMV of the local shop. Skill bodies are in Chinese. The public copy is scrubbed: internal systems, doc tokens, colleague names and real product / creative IDs are replaced with placeholders.

## 🆕 October 2026

| skill | What it does |
|---|---|
| [`video-breakdown-doc`](content/video-breakdown-doc/) | **New** — second-by-second breakdown of a batch of shoppable short videos into a Feishu doc: structure template, first-3-second hook map, per-video script table, case cards, plus a data-masked external version |
| [`kans-cads-summary-table`](kans-analysis/kans-cads-summary-table/) | **New** — merges four exports (TTMS C-ads reports, GMV Max creatives, affiliate orders, campaign report) into one per-creative brand-ads decision sheet; no browser needed |
| [`gsheet-to-feishu-base-migration`](feishu/gsheet-to-feishu-base-migration/) | **New** — generic Google Sheets → Feishu Bitable migration: first load, incremental top-ups, field backfill, rollback, with a real-world mapping checklist |
| [`tiktok-brand-ads-analysis`](kans-analysis/tiktok-brand-ads-analysis/) | **Updated** — every analysis now ends with an "actual vs. beauty-industry benchmark" table |

## Who is this for

| You are… | Start with | You'd say |
|---|---|---|
| **Media buyer / ads intern** | everything in [`tiktok-automation/`](tiktok-automation/) · [`kans-vn-high-cost-low-roi-hourly`](kans-analysis/kans-vn-high-cost-low-roi-hourly/) | "Update budgets from this list", "Exclude these creators", "Which creators posted these creative IDs?" |
| **Ops writing weekly / monthly reviews** | [`kans-vn-weekly-flow`](kans-analysis/kans-vn-weekly-flow/) · [`kans-livestream-charts`](kans-analysis/kans-livestream-charts/) · [`kans-vn-category-competition`](kans-analysis/kans-vn-category-competition/) | "Run the Sep W2 weekly review", "Here's this week's and last week's store data, compare competitors" |
| **Brand ads / audience owner** | [`kans-cads-summary-table`](kans-analysis/kans-cads-summary-table/) · [`tiktok-brand-ads-analysis`](kans-analysis/tiktok-brand-ads-analysis/) · [`ttms-audience-package-strategy`](kans-analysis/ttms-audience-package-strategy/) · [`kans-ttms-cads-report-batch`](tiktok-automation/kans-ttms-cads-report-batch/) | "Build this week's brand-ads sheet", "What's a good CPCo?", "Which tags for this goal?" |
| **Content director / creative optimizer** | [`video-breakdown-doc`](content/video-breakdown-doc/) | "Break down these winning videos", "Deep-dive two cases", "Make a masked external version" |
| **Creator BD** | [`tkshop-daren-cleaning`](data-cleaning/tkshop-daren-cleaning/) · [`gsheet-to-feishu-base-migration`](feishu/gsheet-to-feishu-base-migration/) | "Clean this creator export and shortlist by AOV", "Move our collab sheet from Google to Feishu" |
| **Livestream script / host training** | [`vn-kans-script`](live-script/vn-kans-script/) | "Write a Vietnamese loop script for the whitening trio, with cue cards" |
| **Anyone who reads/writes Feishu docs** | [`feishu-docs`](feishu/feishu-docs/) | "Write the conclusions into this Feishu doc", "Read this Bitable" |

## Catalogue

| Group | # | Skills |
|---|---|---|
| 📈 Weekly reviews | 4 | [kans-vn-weekly-flow](kans-analysis/kans-vn-weekly-flow/) · [kans-livestream-charts](kans-analysis/kans-livestream-charts/) · [kans-vn-category-competition](kans-analysis/kans-vn-category-competition/) · [tiktok-vn-kans-live-ops](kans-analysis/tiktok-vn-kans-live-ops/) |
| 🎯 Brand ads · consideration · audiences | 5 | [kans-cads-summary-table](kans-analysis/kans-cads-summary-table/) 🆕 · [tiktok-brand-ads-analysis](kans-analysis/tiktok-brand-ads-analysis/) · [tiktok-brand-upper-funnel](kans-analysis/tiktok-brand-upper-funnel/) · [ttms-brand-diagnosis](kans-analysis/ttms-brand-diagnosis/) · [ttms-audience-package-strategy](kans-analysis/ttms-audience-package-strategy/) |
| 🤖 Ad monitoring & TikTok back-office automation (Claude in Chrome) | 6 | [kans-vn-high-cost-low-roi-hourly](kans-analysis/kans-vn-high-cost-low-roi-hourly/) · [kans-ttms-cads-report-batch](tiktok-automation/kans-ttms-cads-report-batch/) · [tiktok-batch-budget-update](tiktok-automation/tiktok-batch-budget-update/) · [tiktok-batch-exclude-creators](tiktok-automation/tiktok-batch-exclude-creators/) · [tiktok-copy-adgroup-swap-creative](tiktok-automation/tiktok-copy-adgroup-swap-creative/) · [tiktok-creative-id-to-creator](tiktok-automation/tiktok-creative-id-to-creator/) |
| 🎬 Content: creative breakdowns & livestream scripts | 2 | [video-breakdown-doc](content/video-breakdown-doc/) 🆕 · [vn-kans-script](live-script/vn-kans-script/) |
| 🗂 Data cleaning & Feishu | 3 | [tkshop-daren-cleaning](data-cleaning/tkshop-daren-cleaning/) · [feishu-docs](feishu/feishu-docs/) · [gsheet-to-feishu-base-migration](feishu/gsheet-to-feishu-base-migration/) 🆕 |
| 🧭 Personal | 1 | [touji-zhilu-playbook](personal/touji-zhilu-playbook/) |

Making slides or HTML pages? See the sibling repo [slidor-style-skill](https://github.com/njh20030605-code/slidor-style-skill).

## Adopt for your own shop

The procedures are generic; only parameters (shop names, FX rate, thresholds, campaign IDs, Feishu links) are KANS-specific. **[CUSTOMIZE.md](CUSTOMIZE.md)** (Chinese) rates every skill for reusability (★1–5), lists the parameters to change with file and line, and gives three adoption paths: Vietnam TikTok Shop sellers, TikTok Shop in other countries, non-TikTok e-commerce.

## Install

- **Claude Code**: copy a skill folder to `~/.claude/skills/<name>/` (or clone and symlink). Trigger with `/<name>` or plain language.
- **claude.ai / Cowork**: zip the folder (`SKILL.md` at the root) and upload it under *Skills*.

## Conventions used when writing skills

1. Put the **trigger phrases** (how a user would actually ask) in `description` — that matters more than listing features.
2. Browser-automation skills confirm parameters first, verify each step against an on-page counter, and show a comparison table before submitting.
3. Metric definitions live in `references/`; `SKILL.md` only holds the procedure.
4. Every script runs standalone (`python3 scripts/x.py --help`); the skill is just orchestration.

## Contact

- WeChat: **Anyway77777777**
- GitHub: [@njh20030605-code](https://github.com/njh20030605-code)

## License

MIT — see [LICENSE](LICENSE).
