<div align="center">

# Claude Skills · 自写 Claude 技能合集

**18 hand-written skills for Claude Code / Claude in Chrome / claude.ai — TikTok Ads browser automation, e-commerce analytics, data cleaning, livestream scripting, Feishu docs.**

[中文](README.md) | English

![Claude Code](https://img.shields.io/badge/Claude-Code%20%7C%20in%20Chrome%20%7C%20claude.ai-D97757?logo=anthropic&logoColor=white)
![Skills](https://img.shields.io/badge/skills-18-blue)
![Domain](https://img.shields.io/badge/domain-TikTok%20Shop%20Vietnam-000000?logo=tiktok&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

</div>

Each skill is a folder with a `SKILL.md` entry point (the frontmatter `name` / `description` decides when it triggers; the body is the playbook) plus optional `scripts/`, `references/`, `examples/`. Most skills are written for the **KANS (韩束) Vietnam TikTok Shop** context: FX ₫3,860 ≈ ¥1, primary KPI = livestream GMV + product-card GMV of the local shop. Skill bodies are in Chinese.

## Who is this for

| You are… | Start with | You'd say |
|---|---|---|
| **Media buyer / ads intern** | everything in [`tiktok-automation/`](tiktok-automation/) · [`kans-vn-high-cost-low-roi-hourly`](kans-analysis/kans-vn-high-cost-low-roi-hourly/) | "Update budgets from this list", "Exclude these creators", "Which creators posted these creative IDs?" |
| **Ops writing weekly / monthly reviews** | [`kans-vn-weekly-flow`](kans-analysis/kans-vn-weekly-flow/) · [`kans-livestream-charts`](kans-analysis/kans-livestream-charts/) · [`kans-vn-category-competition`](kans-analysis/kans-vn-category-competition/) | "Run the Sep W2 weekly review", "Here's this week's and last week's store data, compare competitors" |
| **Brand ads / audience owner** | [`tiktok-brand-upper-funnel`](kans-analysis/tiktok-brand-upper-funnel/) · [`ttms-audience-package-strategy`](kans-analysis/ttms-audience-package-strategy/) · [`ttms-brand-diagnosis`](kans-analysis/ttms-brand-diagnosis/) · [`kans-ttms-cads-report-batch`](tiktok-automation/kans-ttms-cads-report-batch/) | "Which tags for this goal?", "What's a good CPCo?", "Batch-create the C-ads wrap-up reports" |
| **Creator BD** | [`tkshop-daren-cleaning`](data-cleaning/tkshop-daren-cleaning/) | "Clean this creator export and shortlist by AOV and skincare share" |
| **Livestream script / host training** | [`vn-kans-script`](live-script/vn-kans-script/) | "Write a Vietnamese loop script for the whitening trio, with cue cards" |
| **Anyone who reads/writes Feishu docs** | [`feishu-docs`](feishu/feishu-docs/) | "Write the conclusions into this Feishu doc", "Read this Bitable" |

## Catalogue

| Group | Skills |
|---|---|
| 📊 [`kans-analysis/`](kans-analysis/) — data → charts → decisions | kans-livestream-charts · kans-vn-category-competition · kans-vn-weekly-flow · kans-vn-high-cost-low-roi-hourly · tiktok-brand-upper-funnel · tiktok-brand-ads-analysis · tiktok-vn-kans-live-ops · ttms-audience-package-strategy · ttms-brand-diagnosis |
| 🤖 [`tiktok-automation/`](tiktok-automation/) — Claude in Chrome driving TikTok Ads / Seller Center / TTMS | kans-ttms-cads-report-batch · tiktok-batch-budget-update · tiktok-batch-exclude-creators · tiktok-copy-adgroup-swap-creative · tiktok-creative-id-to-creator |
| 🧹 [`data-cleaning/`](data-cleaning/) | tkshop-daren-cleaning |
| 🎙 [`live-script/`](live-script/) | vn-kans-script |
| 📄 [`feishu/`](feishu/) | feishu-docs |
| 🧭 [`personal/`](personal/) | touji-zhilu-playbook |

## Adopt for your own shop

The procedures are generic; only parameters (shop names, FX rate, thresholds, campaign IDs, Feishu links) are KANS-specific. **[CUSTOMIZE.md](CUSTOMIZE.md)** (Chinese) rates every skill for reusability (★1–5), lists the parameters to change with file and line, and gives three adoption paths: Vietnam TikTok Shop sellers, TikTok Shop in other countries, non-TikTok e-commerce. 5 skills work out of the box, 4 need a one-line change.

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
