<div align="center">

# Claude Skills 合集 · 自写 Claude 技能

**21 个手写 skill，给 Claude Code / Claude in Chrome / claude.ai 用：周报复盘、品牌广告与人群包、TikTok 后台自动化、短视频素材拆解、飞书表格迁移。**

中文 | [English](README.en.md)

![Claude](https://img.shields.io/badge/Claude-Code%20%7C%20in%20Chrome%20%7C%20claude.ai-D97757?logo=anthropic&logoColor=white)
![Skills](https://img.shields.io/badge/skills-21-blue)
![Domain](https://img.shields.io/badge/%E5%9C%BA%E6%99%AF-TikTok%20Shop%20%E8%B6%8A%E5%8D%97-000000?logo=tiktok&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

</div>

我在 Claude（Claude Code / Claude in Chrome / claude.ai）里用的自定义 skill。每个 skill 一个目录，`SKILL.md` 是入口（frontmatter 的 `name` / `description` 决定何时触发，正文是操作手册），`scripts/` `references/` `examples/` 是配套脚本、口径资料和示例数据。

绝大多数 skill 绑定 **KANS（韩束）越南 TikTok Shop** 运营语境：汇率 ₫3,860 ≈ ¥1，主 KPI 是本土店直播间 GMV + 商品卡 GMV。公开版已脱敏：内部系统、表格 token、同事名、真实商品 / 素材 ID 都换成了占位值。

## 🆕 2026-10 更新

| skill | 一句话 |
|---|---|
| [`video-breakdown-doc`](content/video-breakdown-doc/) | **新增**：把一批带货短视频逐秒拆解成飞书文档，出结构母版、前三秒钩子、逐条话术大表、重点案例，还能一键出数据脱敏的对外版 |
| [`kans-cads-summary-table`](kans-analysis/kans-cads-summary-table/) | **新增**：把 TTMS 种草报告 + GMV Max + 订单 + Campaign 四份导出合成一张按素材的品广投放决策表，不需要浏览器 |
| [`gsheet-to-feishu-base-migration`](feishu/gsheet-to-feishu-base-migration/) | **新增**：Google 表格迁飞书多维表格的通用流程，首次灌数 / 增量补迁 / 回填 / 回滚，附两次真实迁移的口径清单 |
| [`tiktok-brand-ads-analysis`](kans-analysis/tiktok-brand-ads-analysis/) | **更新**：每次分析强制出「实际 vs 美妆行业 Benchmark」对比表，补充平台 C-ads Playbook 要点 |

## 给谁用 · 按角色找 skill

| 你是 | 先看这几个 | 典型一句话 |
|---|---|---|
| **广告投手 / 投放实习生** | [🤖 后台自动化](#-投放监控与-tiktok-后台自动化claude-in-chrome) 全部 | 「按我发的清单批量改预算」「把这些达人加进排除列表」「这些素材 ID 是哪些达人发的」 |
| **品牌广告 / 种草负责人** | [`kans-cads-summary-table`](kans-analysis/kans-cads-summary-table/) · [`tiktok-brand-ads-analysis`](kans-analysis/tiktok-brand-ads-analysis/) · [`ttms-audience-package-strategy`](kans-analysis/ttms-audience-package-strategy/) | 「出这周的品广表」「CPCo 多少算好」「这个目标选什么人群标签」 |
| **写周报 / 月报的运营** | [`kans-vn-weekly-flow`](kans-analysis/kans-vn-weekly-flow/) · [`kans-livestream-charts`](kans-analysis/kans-livestream-charts/) · [`kans-vn-category-competition`](kans-analysis/kans-vn-category-competition/) | 「开始跑 9 月 W2 周报」「这是本周和上周的店铺数据，做竞品对比」 |
| **内容编导 / 素材优化** | [`video-breakdown-doc`](content/video-breakdown-doc/) | 「拆一下这几条爆款视频」「重点拆两个案例」「做个对外脱敏版」 |
| **直播话术 / 主播培训** | [`vn-kans-script`](live-script/vn-kans-script/) | 「写一版美白三件套的越南语循环话术，配手卡」 |
| **达人 BD** | [`tkshop-daren-cleaning`](data-cleaning/tkshop-daren-cleaning/) · [`gsheet-to-feishu-base-migration`](feishu/gsheet-to-feishu-base-migration/) | 「把达人导出表清洗一下按客单价初筛」「把合作表从 Google 迁到飞书」 |
| **任何要读写飞书文档的人** | [`feishu-docs`](feishu/feishu-docs/) | 「把结论写进这个飞书文档」「读一下这个多维表格」 |

做 PPT 或 HTML 页面的，看另一个仓库 [slidor-style-skill](https://github.com/njh20030605-code/slidor-style-skill)（Slidor + Lucile 风格的设计 skill）。

关键词：Claude Skills · Claude in Chrome · TikTok Ads 自动化 · TTMS · C-ads · GMV Max · 素材拆解 · 越南电商 · 周报自动化 · 飞书多维表格

## 目录

| 分类 | 数量 | skill |
|---|---|---|
| [📈 周报与复盘](#-周报与复盘) | 4 | kans-vn-weekly-flow · kans-livestream-charts · kans-vn-category-competition · tiktok-vn-kans-live-ops |
| [🎯 品牌广告 · 种草 · 人群包](#-品牌广告--种草--人群包) | 5 | kans-cads-summary-table · tiktok-brand-ads-analysis · tiktok-brand-upper-funnel · ttms-brand-diagnosis · ttms-audience-package-strategy |
| [🤖 投放监控与后台自动化](#-投放监控与-tiktok-后台自动化claude-in-chrome) | 6 | kans-vn-high-cost-low-roi-hourly · kans-ttms-cads-report-batch · tiktok-batch-budget-update · tiktok-batch-exclude-creators · tiktok-copy-adgroup-swap-creative · tiktok-creative-id-to-creator |
| [🎬 内容：素材拆解与直播话术](#-内容素材拆解与直播话术) | 2 | video-breakdown-doc · vn-kans-script |
| [🗂 数据清洗与飞书](#-数据清洗与飞书) | 3 | tkshop-daren-cleaning · feishu-docs · gsheet-to-feishu-base-migration |
| [🧭 个人](#-个人) | 1 | touji-zhilu-playbook |

### 📈 周报与复盘

把后台导出的数据变成周报结论、图表，写进飞书。

| skill | 用途 | 配套 |
|---|---|---|
| [`kans-vn-weekly-flow`](kans-analysis/kans-vn-weekly-flow/) | 周报 / 月报全流程编排：一句话启动，固定 13 步（大盘→直播间 GMV→相关性→退款→竞品→流量→品广→商品卡→单链接→主播），缺数据时停下来告诉你去哪导，最后写进飞书 | scripts |
| [`kans-livestream-charts`](kans-analysis/kans-livestream-charts/) | 直播周报三张标准图：每日 GMV + ROI 周对比、自家直播 vs 大盘相关性、品类大盘堆叠趋势 | examples, scripts |
| [`kans-vn-category-competition`](kans-analysis/kans-vn-category-competition/) | 类目竞争格局周报：FastMoss / Kalodata 店铺级导出做两周对比，出 6 张图 + 人民币口径 xlsx + 异动品牌结论 | examples, references, scripts |
| [`tiktok-vn-kans-live-ops`](kans-analysis/tiktok-vn-kans-live-ops/) | 直播间复盘分析师：GMV / ROI / 退款 / 流量结构 / 转化漏斗 / 主播排名的环比归因，给出下一步运营动作 | — |

### 🎯 品牌广告 · 种草 · 人群包

C-ads（种草广告）和 TTMS 的分析与决策：看 CPCo 和 Co 人群，不只看 GMV。

| skill | 用途 | 配套 |
|---|---|---|
| [`kans-cads-summary-table`](kans-analysis/kans-cads-summary-table/) 🆕 | 品广素材投放决策汇总表：TTMS 种草报告 + GMV Max Creative + 达人订单 + Campaign Report 合成一张按素材的表（CPCo / 种草效率 / 品广质量分 / 总营销 ROI / 付费流占比），自带校验页 | scripts, templates |
| [`tiktok-brand-ads-analysis`](kans-analysis/tiktok-brand-ads-analysis/) | C-ads 投放诊断：预算 / 定向 / 排期 / 创意 / 大促节奏四维 + 美妆行业 Benchmark 对比表（必出） | — |
| [`tiktok-brand-upper-funnel`](kans-analysis/tiktok-brand-upper-funnel/) | 品牌上漏斗诊断：TTMS 四阶段截图或推广系列消耗导出，定位卡在哪一层 | — |
| [`ttms-brand-diagnosis`](kans-analysis/ttms-brand-diagnosis/) | TTMS Brand Diagnosis 四阶段指标复盘，找瓶颈层 | — |
| [`ttms-audience-package-strategy`](kans-analysis/ttms-audience-package-strategy/) | 人群包策略顾问：选什么标签、估不出规模怎么办、推不到 TTAM、新品包 / 爆品包怎么分，以及 C-ads 承接怎么搭 | — |

### 🤖 投放监控与 TikTok 后台自动化（Claude in Chrome）

在 TikTok 广告平台 / 商家中心 / TTMS 页面上代替人手批量操作。共同点：逐条校验计数、提交前列对照表让人确认。

| skill | 用途 | 配套 |
|---|---|---|
| [`kans-vn-high-cost-low-roi-hourly`](kans-analysis/kans-vn-high-cost-low-roi-hourly/) | 每小时扫 GMV Max 当天高成本低 ROI 素材，10 点 / 14 点加扫近 7 天，命中才出 xlsx | — |
| [`kans-ttms-cads-report-batch`](tiktok-automation/kans-ttms-cads-report-batch/) | 在 TTMS 投后结案页批量建种草广告报告 | — |
| [`tiktok-batch-budget-update`](tiktok-automation/tiktok-batch-budget-update/) | 按「广告组 ID → 新日预算」清单批量改预算 | references |
| [`tiktok-batch-exclude-creators`](tiktok-automation/tiktok-batch-exclude-creators/) | 在「管理创意作品」里把一批达人逐个加进排除列表 | — |
| [`tiktok-copy-adgroup-swap-creative`](tiktok-automation/tiktok-copy-adgroup-swap-creative/) | 复制已有广告组，换成新达人素材（帖子授权码），改名改预算改排期后发布 | — |
| [`tiktok-creative-id-to-creator`](tiktok-automation/tiktok-creative-id-to-creator/) | 一批素材 ID 反查达人用户名，去重导出 CSV | — |

### 🎬 内容：素材拆解与直播话术

| skill | 用途 | 配套 |
|---|---|---|
| [`video-breakdown-doc`](content/video-breakdown-doc/) 🆕 | 短视频素材逐秒拆解成飞书文档：1 秒 1 帧 + 0.5 秒字幕条逐格核对，产出数据 Benchmark、结构母版、前三秒钩子地图、逐条拆解大表（附视频 + 分层完整话术）、重点案例拆解卡，可出数据脱敏的对外版 | references, scripts, assets |
| [`vn-kans-script`](live-script/vn-kans-script/) | 越南直播间循环话术的写作、改写与手卡配牌，可生成带手卡图的话术 xlsx 和可打印手卡 PDF | — |

### 🗂 数据清洗与飞书

| skill | 用途 | 配套 |
|---|---|---|
| [`tkshop-daren-cleaning`](data-cleaning/tkshop-daren-cleaning/) | 清洗 / 合并 TikTok Shop 达人导出：K₫/M₫/万 单位换算、区间取中位、按达人去重，并按成交量 / 客单价 / 护肤占比初筛 | filter_candidates.py |
| [`feishu-docs`](feishu/feishu-docs/) | 读写飞书云文档（sheet / docx / 多维表格） | — |
| [`gsheet-to-feishu-base-migration`](feishu/gsheet-to-feishu-base-migration/) 🆕 | Google 表格迁飞书多维表格：口径确认清单、首次灌数、增量补迁、字段回填、按 record_id 回滚，附踩坑清单和一份真实迁移口径作参照 | references, scripts |

### 🧭 个人

与工作无关的个人知识库。

| skill | 用途 | 配套 |
|---|---|---|
| [`touji-zhilu-playbook`](personal/touji-zhilu-playbook/) | 「投机之路」Telegram 频道的方法论检索（公开版只含方法论摘要，不含帖子全文） | references, scripts |

共 21 个 skill。

## 接入你自己的店铺

这些 skill 的流程是通用的，KANS 特有的只是参数（店铺名、汇率、阈值、计划 ID、表链接）。**[CUSTOMIZE.md](CUSTOMIZE.md)** 逐个 skill 列出了通用程度评级（★1–5）、必改参数、在哪一行改，以及「越南 TikTok 卖家 / 其他国家 TikTok 卖家 / 非 TikTok 电商」三条接入路径。

## 怎么用

- **Claude Code**：把某个 skill 目录复制到 `~/.claude/skills/<name>/`，或整个仓库 clone 后做软链接；对话里 `/<name>` 或自然语言触发。
- **claude.ai / Cowork**：把目录打成 zip（`SKILL.md` 在根）上传到「技能」。
- 每个 `SKILL.md` 开头的 `description` 写清了触发场景，改触发条件只改它。

## 写 skill 的约定

1. `description` 里把**触发短语**写全（用户会怎么说），比写功能更重要。
2. 涉及浏览器自动化的：先确认参数（周期、清单、阈值）再执行；每一步靠页面上的计数校验；提交前列对照表。
3. 涉及数据口径的：把口径写进 `references/`，SKILL.md 只放流程；口径变了改一处。
4. 脚本一律可独立运行（`python3 scripts/x.py --help` 能看到用法），skill 只是编排。

## 联系

- 微信：**Anyway77777777**
- GitHub：[@njh20030605-code](https://github.com/njh20030605-code)

## 许可

MIT，见 [LICENSE](LICENSE)。
