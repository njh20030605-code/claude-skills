# Changelog

## v1.2.0 · 2026-10-16

**新增 3 个 skill，目录按用途重新分组，共 21 个。**

- **新增 `content/video-breakdown-doc`**：短视频素材逐秒拆解成飞书文档。1 秒 1 帧总览图 + 0.5 秒字幕条逐格核对，
  产出数据 Benchmark、结构母版、前三秒钩子地图、逐条拆解大表（附视频 + 分层完整话术）、重点案例拆解卡，
  可整篇复制出数据换成指数的对外版。配套 `prep` / `transcribe_zh` / `parse_review` / `build_table` / `quotes` / `svg_bench` / `scan_sensitive` 七个脚本
- **新增 `kans-analysis/kans-cads-summary-table`**：TTMS 种草报告 + GMV Max Creative + 达人订单 + Campaign Report
  合成按素材的品广投放决策表，按内容自动识别文件，自带校验页；普通对话开代码执行即可，不需要浏览器
- **新增 `feishu/gsheet-to-feishu-base-migration`**：Google 表格迁飞书多维表格的通用流程（口径确认 → 灌数 → 增量补迁 → 回填 → 回滚），
  附踩坑清单和一次真实迁移的口径对照
- **更新 `tiktok-brand-ads-analysis`**：新增第零节「行业 Benchmark」，每次分析强制出「实际 vs 美妆行业 Benchmark」对比表；补充平台 C-ads Playbook 要点
- **README 重新分组**：周报与复盘 / 品牌广告·种草·人群包 / 投放监控与后台自动化 / 内容 / 数据清洗与飞书 / 个人；
  新增「2026-10 更新」和「内容编导」角色入口；`CUSTOMIZE.md` 补 19–21 节
- **脱敏**：`scrub.sh` 新增规则（内部素材后台与取数脚本、飞书 token、同事名、真实商品 / 素材 ID），同步后自动扫残留，命中即中止

## v1.1.0 · 2026-09-20

**从「KANS 专用」变成「填参数就能用的框架」。**

- **脚本里的真实业务数据全部换成示例**：商品 ID、计划 ID、两期 GMV / 成本数字、店铺名、经营结论，
  现在是 `1000000000000000001` / `计划A-主推品` / `Your Shop` 这类一眼可辨的占位值，附 `# 示例数据：换成你自己的导出`
- **参数抽成占位符**：`kans-vn-weekly-flow`、`kans-vn-high-cost-low-roi-hourly`、`kans-ttms-cads-report-batch`、
  `tiktok-vn-kans-live-ops`、`kans-livestream-charts`、`kans-vn-category-competition` 的 SKILL.md 顶部新增「参数」小节，
  逐项列出 `{{店铺名}}` `{{市场}}` `{{汇率}}` `{{盈亏线}}` 等，并给 KANS 的值作为例子
- **接入指南 CUSTOMIZE.md**：新增东南亚六国市场参数表（货币、符号、汇率、时区、后台域名、数字写法），
  通用度评级同步更新，六个 skill 从 ★1–3 升到 ★4
- **修掉两处历史问题**：`kans-ttms-cads-report-batch` 重复的 frontmatter；周报与直播复盘两个 skill 之间
  汇率 / 月目标 / 班次数对不上，现在统一读占位符
- **可移植性**：沙盒专用路径（`/mnt/user-data/outputs`）改成相对路径；自己的店铺名支持环境变量 `MY_SHOP` 覆盖
- **`sync-from-local.sh` 分组**：已通用化的 skill 不再从本机 KANS 版同步，避免成果被覆盖

## v1.0.0 · 2026-09-20

首个公开版本：18 个 skill 按 6 类归档（KANS 分析 / TikTok 后台自动化 / 数据清洗 / 直播话术 / 飞书 / 个人）。中英双语 README、按角色导航、`CUSTOMIZE.md` 接入指南。MIT 许可。
