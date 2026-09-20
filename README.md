# Claude Skills 合集

我在 Claude（Claude Code / Claude in Chrome / claude.ai）里用的自定义 skill。每个 skill 一个目录，`SKILL.md` 是入口（frontmatter 的 `name` / `description` 决定何时触发，正文是操作手册），`scripts/` `references/` `examples/` 是配套脚本、口径资料和示例数据。

绝大多数 skill 绑定 **KANS（韩束）越南 TikTok Shop** 运营语境：汇率 ₫3,860 ≈ ¥1，主 KPI 是本土店直播间 GMV + 商品卡 GMV。

## 怎么用

- **Claude Code**：把某个 skill 目录复制到 `~/.claude/skills/<name>/`，或整个仓库 clone 后做软链接；对话里 `/<name>` 或自然语言触发。
- **claude.ai / Cowork**：把目录打成 zip（`SKILL.md` 在根）上传到「技能」。
- 每个 `SKILL.md` 开头的 `description` 写清了触发场景，改触发条件只改它。

## 目录

### 📊 KANS 分析类（周报 / 品广 / 人群包 / 预警口径）

把后台导出的数据变成周报结论、图表和决策。大多是「给数据 → 出图 + 结论」的分析型 skill。

| skill | 用途 | 配套 |
|---|---|---|
| [`kans-livestream-charts`](kans-analysis/kans-livestream-charts/) | 生成 KANS 越南直播运营周报/月报的三类标准图表。当用户提供直播间日度数据（KANS Campaign 导出）和/或大盘品类数据（TTMS Serums & Essences 导出），并要求做 (1) 每日 GMV+ROI 周对比柱线图、(2) KANS 直播 vs 大盘直播 GMV 相关性验证双面板图、(3) 品类大盘堆叠 GM… | examples, scripts |
| [`kans-vn-category-competition`](kans-analysis/kans-vn-category-competition/) | 越南美妆个护类目【竞争格局周报】——从 FastMoss/Kalodata 店铺级导出（Store Name / GMV / Affiliate Video / Self-Account Video / Self-Account Live / Affiliate Live / Shop Tab GMV）做两周对比，输出 6 张标准图 … | examples, references, scripts |
| [`kans-vn-high-cost-low-roi-hourly`](kans-analysis/kans-vn-high-cost-low-roi-hourly/) | 每小时扫描KANS越南GMV Max(商品+直播)当天高成本低ROI素材；每天10点/14点额外扫近7天，输出一个xlsx按当天/近7天分sheet。当用户要求跑"KANS 高成本低ROI素材预警 / GMV Max 低效高耗素材扫描"或将其设为定时任务时使用。 | — |
| [`kans-vn-weekly-flow`](kans-analysis/kans-vn-weekly-flow/) | KANS 越南 SKINCARE 直播间【周报 / 月报复盘全流程】半自动编排器。当用户用一句话启动复盘（如"开始跑 7月W1 周报 / 这周的复盘 / 把周报写进飞书"）时使用。按固定 13 步走：大盘→直播间GMV→相关性→GMV-ROI→退款率→短视频占比→竞品→流量结构→品广→商品卡→单链接→主播三件套→写入飞书。每步缺数据时… | scripts |
| [`tiktok-brand-ads-analysis`](kans-analysis/tiktok-brand-ads-analysis/) | 分析越南市场 TikTok Brand Consideration Ads (C-ads) 投放数据。当用户提供 C-ads 数据并需诊断预算/定向/排期/创意/大促节奏，或评估种草效果(CPCo、Co人群、人群流转)时使用。核心看 CPCo 与 Co 人群规模，不只看 GMV/ROAS。 | — |
| [`tiktok-brand-upper-funnel`](kans-analysis/tiktok-brand-upper-funnel/) | TikTok 品牌上漏斗诊断（越南等 TTMS 覆盖市场）。当用户上传/粘贴的是【TTMS Brand Diagnosis 四阶段截图或导出】（Premium Reach / Massive Reach / Consideration / Conversion、同比、基准、排名）或【广告管理平台 推广系列汇总消耗 USD 导出 / 品… | — |
| [`tiktok-vn-kans-live-ops`](kans-analysis/tiktok-vn-kans-live-ops/) | TikTok 越南韩束(KANS)SKINCARE 直播间运营复盘分析师。当用户提供某周/某月直播间数据（GMV/NMV、ROI、退款率、流量结构、转化漏斗、变现效率、互动、付费自然结构、主力链接SKU、主播排名、背景视觉、同行视觉、GMV-MAX商品卡等）并需要写周报/月报、做环比复盘、归因诊断、给出下一步运营动作时使用。核心：不只… | — |
| [`ttms-audience-package-strategy`](kans-analysis/ttms-audience-package-strategy/) | TTMS（TikTok Market Scope）人群包策略顾问 + 种草广告（C-ads）承接。当用户要「打人群包/建受众包/这个目标选什么标签/ACC 和 TikTok Shop 标签怎么选/视频受众估算不出规模/人群包推不到 TTAM/开 R&F 要多久/人群包过期/新品包爆品包怎么分/种草广告怎么搭计划/CPCo 多少算好」时… | — |
| [`ttms-brand-diagnosis`](kans-analysis/ttms-brand-diagnosis/) | 用 TikTok Market Scope (TTMS) Brand Diagnosis 模块做品牌增长漏斗复盘（TTMS分析师）。当用户提供 TTMS 品牌诊断数据（Premium Reach / Massive Reach / Consideration / Conversion 四阶段指标、同比、基准、排名）并需要定位瓶颈层、系… | — |

### 🤖 TikTok 后台浏览器自动化（Claude in Chrome）

在 TikTok 广告平台 / 商家中心 / TTMS 页面上代替人手批量操作。共同点：逐条校验计数、提交前列对照表让人确认。

| skill | 用途 | 配套 |
|---|---|---|
| [`kans-ttms-cads-report-batch`](tiktok-automation/kans-ttms-cads-report-batch/) | 在 TikTok Market Scope (TTMS) 投后结案页面用 Claude in Chrome 批量创建 KANS 越南「种草广告报告」结案。当用户给出一批待建报告（或给出 Campaign Report + GMV Max Creative 导出表让你自己筛）并要求"批量建种草广告报告 / 跑 C-ads 结案 / 建投… | — |
| [`tiktok-batch-budget-update`](tiktok-automation/tiktok-batch-budget-update/) | 在 TikTok 广告管理平台（ads.tiktok.com/i18n/manage/adgroup）用 Claude in Chrome 按「广告组ID → 新日预算」清单批量改预算。当用户粘贴一份 ID+数字的清单并说「调一下预算 / 按我发的改预算 / 批量改日预算 / 把新预算加进去 / 改总预算」时使用。核心：广告组ID是广… | references |
| [`tiktok-batch-exclude-creators`](tiktok-automation/tiktok-batch-exclude-creators/) | 在 TikTok 商家中心「修改广告计划 › 管理创意作品」页面，用 Claude in Chrome 把一批达人用户名逐个加入「排除」联盟列表并保存。当用户给出一份待排除达人清单并要求"批量排除达人 / 把这些达人加到排除列表 / 逐个勾选排除用户名 / 在排除下拉里按用户名批量勾选"时使用。也适用于任何"带搜索框的勾选下拉列表里… | — |
| [`tiktok-copy-adgroup-swap-creative`](tiktok-automation/tiktok-copy-adgroup-swap-creative/) | 在 TikTok 广告管理平台用 Claude in Chrome 复制已有广告组、批量换成新达人素材（帖子授权码）、改名改预算改排期后发布。用户说「复制这个广告组投新素材 / 建品牌广告 / 这几个达人的视频拿去投」时使用。 | — |
| [`tiktok-creative-id-to-creator`](tiktok-automation/tiktok-creative-id-to-creator/) | 在 TikTok Shop 卖家后台「创意作品」(ads-creation/manage-analyze) 页面，用 Claude in Chrome 批量把一批已知的素材/作品ID（作品ID / creative_id）反查成对应的达人用户名，并去重、导出本地 CSV。当用户给出一批作品ID/素材ID 并要求"查出这些素材是哪些达人… | — |

### 🧹 数据清洗

导出表的单位换算、去重、初筛。

| skill | 用途 | 配套 |
|---|---|---|
| [`tkshop-daren-cleaning`](data-cleaning/tkshop-daren-cleaning/) | 清洗/合并 TikTok Shop「tkshop达人信息」.xls 导出：K₫/M₫/万 单位换算、客单价区间取中位数、拆出直播视频占比与类目/性别/年龄占比、按达人名称去重合并；并支持按成交量/客单价/男女比/视频占比/护肤占比做达人初筛。 | filter_candidates.py |

### 🎙 直播话术

越南直播间循环话术的写作、改写与手卡配牌。

| skill | 用途 | 配套 |
|---|---|---|
| [`vn-kans-script`](live-script/vn-kans-script/) | VN KANS话术 —— 越南 TikTok 韩束(KANS)直播间循环话术的写作、改写、手卡配牌与物料诊断。当用户要写/改越南直播间话术、调整段落顺序或优先级、把手卡（POSM / INFO BOARD / 主图价格卡）配到话术旁边、判断物料是红系抗老还是白系美白、诊断缺哪些手卡、或生成带手卡图的话术 xlsx 和可打印手卡 PDF… | — |

### 📄 飞书云文档

读写飞书 sheet / docx / 多维表格。

| skill | 用途 | 配套 |
|---|---|---|
| [`feishu-docs`](feishu/feishu-docs/) | 读写飞书云文档（sheet / docx / 多维表格）。当请求里出现飞书链接（*.feishu.cn/wiki|sheets|docx|base）或要求把内容写进飞书文档、回填飞书表格、从飞书文档取数时自动使用。 | — |

### 🧭 个人

与工作无关的个人知识库。

| skill | 用途 | 配套 |
|---|---|---|
| [`touji-zhilu-playbook`](personal/touji-zhilu-playbook/) | 「投机之路」(Telegram @journey_of_someone) 全量帖子存档 + 方法论检索。当用户问「投机之路怎么看X / 他当时是怎么做的 / 他对某个币·某个交易所·某次黑天鹅说过什么」、想用他那套"现金为王+只买急跌+套利吃摩擦+不做无edge的空"的框架给自己的仓位或某笔交易做体检、想查他的原话原帖、或要把频道存档… | references, scripts |

共 18 个 skill。

## 写 skill 的约定

1. `description` 里把**触发短语**写全（用户会怎么说），比写功能更重要。
2. 涉及浏览器自动化的：先确认参数（周期、清单、阈值）再执行；每一步靠页面上的计数校验；提交前列对照表。
3. 涉及数据口径的：把口径写进 `references/`，SKILL.md 只放流程；口径变了改一处。
4. 脚本一律可独立运行（`python3 scripts/x.py --help` 能看到用法），skill 只是编排。
