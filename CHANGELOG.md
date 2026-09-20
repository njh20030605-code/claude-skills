# Changelog

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
