# 定制指南：把这套 skill 改成你自己的业务

这个仓库里的 18 个 skill 是围绕一家品牌（KANS / 韩束）在越南 TikTok Shop 的运营场景写出来的，但每个 skill 内部都是两层：**上层是通用流程**（先确认什么、按什么顺序算、产出什么、哪些坑别踩），**下层是一组业务参数**（店铺名、汇率、阈值、商品 ID、后台链接、文件路径、命名习惯）。绝大多数「KANS 味」都集中在下层，且往往只在几处：frontmatter 的 `description`（决定何时触发）、正文里的「口径 / 阈值 / 清单」小节、以及 `scripts/` 里顶部的常量和 `references/` 里的映射表。

改参数的原则只有一条：**只改触发词和口径，不动流程。** 流程里的每一步（比如「窗口必须匹配导出」「先读表头再写」「提交前列对照表让人确认」）都是踩坑之后写下来的，跟你卖什么、在哪个国家卖没有关系；把它们删了，skill 就退化成一段普通 prompt。反过来，所有带具体数字、具体名字、具体链接的地方，默认都应该被视为「需要换成你自己的」，哪怕它看起来像通用常识（例如 4.1 这条盈亏线，是按那家店的佣金、退款率、人力成本算出来的，不是行业通用值）。

下面先给一张总表，再逐个 skill 说清「哪一行、原值是什么、换成什么」，最后按你的业务类型给一条接入路径。

---

## 〇、市场参数表（东南亚六国）

所有 skill 里跟「国家」有关的东西就这几项。换市场时先在这张表里查好，再按下面各 skill 的说明填进去。

| 市场 | 货币 | 符号 | 1 人民币 ≈ | 时区 | 卖家后台域名 | 数字写法 |
|---|---|---|---|---|---|---|
| 越南 VN | VND | ₫ đ | 3,891 | UTC+7 | seller-vn.tiktok.com | 点=千分位，逗号=小数（`1.234.567` / `4,13`） |
| 泰国 TH | THB | ฿ | 4.5 | UTC+7 | seller-th.tiktok.com | 逗号=千分位，点=小数（`1,234.50`） |
| 印尼 ID | IDR | Rp | 2,250 | UTC+7 | seller-id.tiktok.com | 点=千分位，逗号=小数；缩写 rb=千 jt=百万 |
| 马来西亚 MY | MYR | RM | 0.6 | UTC+8 | seller-my.tiktok.com | 逗号=千分位，点=小数 |
| 菲律宾 PH | PHP | ₱ | 8.0 | UTC+8 | seller-ph.tiktok.com | 逗号=千分位，点=小数 |
| 新加坡 SG | SGD | S$ | 0.18 | UTC+8 | seller-sg.tiktok.com | 逗号=千分位，点=小数 |

汇率是写文档时的参考值，正式出数务必用当日实时汇率。**数字写法那一列最容易踩坑**：
同一串 `1.234.567` 在越南是一百二十三万，在泰国是 1.234567。脚本里的解析函数会自动判别，
但你手动核对数据时要按这一列看。

盈亏线 ROI、月目标、班次划分这些是各家自己的经营参数，不随国家变，按自己的佣金、退款率、人力成本反算。

## 一、总表

通用程度：★★★★★ = 开箱即用，不改也能跑；★★★★ = 参数已抽成占位符 / 示例数据，填表即可；★ = 还绑着具体业务数字，只能借骨架。

> **2026-09-20 起**：标「已通用化」的 skill，脚本里的真实商品 ID、GMV 数字、店铺名、经营结论
> 已全部换成示例数据，`SKILL.md` 顶部有「参数」小节列出所有 `{{占位符}}`。照着填就能跑，
> 跑出来的数是你自己的。这些 skill 由本仓库直接维护，`sync-from-local.sh` 不会再用本机 KANS 版覆盖它们。

| skill | 通用程度 | 必改参数 | 在哪改 |
|---|---|---|---|
| `feishu/feishu-docs` | ★★★★★ | 无业务参数；只需你自己的飞书自建应用凭据 | 环境变量 / `~/.feishu-app.env`（SKILL.md L35–36） |
| `tiktok-automation/tiktok-batch-budget-update` | ★★★★★ | 无；依赖「广告组名以数字 ID 结尾」这一命名习惯 | SKILL.md L30–31、`references/set_budget.js` L33 |
| `tiktok-automation/tiktok-batch-exclude-creators` | ★★★★★ | 无；坐标是经验值，随屏幕变 | SKILL.md L20、L43 |
| `tiktok-automation/tiktok-creative-id-to-creator` | ★★★★★ | 无 | — |
| `kans-analysis/ttms-brand-diagnosis` | ★★★★★ | 无 | — |
| `tiktok-automation/tiktok-copy-adgroup-swap-creative` | ★★★★ | 广告组 / 广告命名规则、广告账户 ID | SKILL.md L27–37、L45 |
| `kans-analysis/tiktok-brand-ads-analysis` | ★★★★ | 「市场应为越南」一句；其余是平台官方基准 | SKILL.md L3、L6、L24 |
| `kans-analysis/tiktok-brand-upper-funnel` | ★★★★ | 越南活动日历、广告账户数备注、币种口径引用 | SKILL.md L63、L132、L167 |
| `data-cleaning/tkshop-daren-cleaning` | ★★★★（越南）/ ★★★（其他国家） | 货币简写与小数格式、导出列名、初筛阈值、目标类目 | SKILL.md L98–113、L169–175、L383–391；`filter_candidates.py` L24–32、L59–64 |
| `kans-analysis/kans-livestream-charts` | ★★★★（已通用化） | USD→RMB 汇率、盈亏线、大促日、事件标注、图标题、导出表头 | `scripts/common.py`、`1_*.py` L144–145、`2_*.py` L129–130、`3_*.py` L23–31 |
| `kans-analysis/kans-vn-category-competition` | ★★★★（已通用化） | 店铺名、中文简称、多店品牌映射、中国品牌梯队、兜底汇率、导出列名 | `scripts/common.py` L51–57、L60–69、L106–190；`metrics.py` L50 |
| `kans-analysis/ttms-audience-package-strategy` | ★★★ | 默认语境、§7 配方表、行业基准行、飞书文档 token | SKILL.md L3、L9、L25、L87、L156–169、L204、L212 |
| `tiktok-automation/kans-ttms-cads-report-batch` | ★★★★（已通用化） | TTMS accountId、账号名、产品名 / 商品 ID 映射、广告组命名格式、报告命名规则、JS 里用于定位的字符串 | SKILL.md L31–32、L40、L43–47、L54–56、L186–188、L193 |
| `kans-analysis/tiktok-vn-kans-live-ops` | ★★★★（已通用化） | 月目标、目标 ROI、盈亏线、两条汇率、SKU 名、素材 / 手卡阈值、排班时段、长期梯队、竞品名、飞书链接 | SKILL.md L3、L7、L37–38、L53–54、L67、L74、L79–80、L84–85、L89、L114–137 |
| `live-script/vn-kans-script` | ★★（框架 ★★★★） | 全部产品价格、赠品、成分、认证数据、品牌背书、越南语卡面文案 | SKILL.md L86–141、L203–205、L211–240 |
| `kans-analysis/kans-vn-high-cost-low-roi-hourly` | ★★★★（已通用化） | 成本 / ROI 阈值、VND 汇率、计划清单（campaign_id / product_id）、卖家后台域名与账号、扫描时刻 | SKILL.md L6、L10–11、L18–19、L22、L24–34、L39、L45、L68 |
| `kans-analysis/kans-vn-weekly-flow` | ★★★★（已通用化） | 两条汇率、VXP 费率、盈亏线、月目标、campaign ID、5 条商品 ID、品线关键词、主播表 / 飞书文档名、店铺名 / 达人 handle、6 班次、文件夹与文件名 | SKILL.md 全篇（见下）；`scripts/_config.py` 全部；`kol_koc.py` / `s105.py` / `s11.py` / `gmvmax_card.py` / `seg5_chart.py` 顶部数据块 |
| `personal/touji-zhilu-playbook` | 不适用 | 与电商无关的个人阅读存档，无需定制；不需要就整个目录删掉 | — |

一个共性提醒：多个 skill 在结尾「关联技能」处互相点名（如 `kans-vn-weekly-flow` ↔ `kans-livestream-charts` ↔ `tiktok-brand-upper-funnel`）。你若改了目录名或 frontmatter 的 `name`，要把这些引用一起改，否则触发链会断。`README.md` / `README.en.md` 开头也写着 KANS 与 ₫3,860 的说明，一并改掉。

---

## 二、逐个 skill 的参数清单

每一节按「参数 → 位置 → 原值 → 换成什么」列。「换成什么」一律用占位符描述，请替换为你自己的值。

### 1. feishu/feishu-docs（★★★★★）

没有任何品牌或市场相关的写死值。整份 SKILL.md 讲的是飞书开放平台的通用路径选择（沙箱 curl → 浏览器直调 → 剪贴板兜底）、权限与错误码。

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 凭据来源 | SKILL.md L34–37 | 环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`，或 `~/.feishu-app.env` | 你自己的自建应用凭据；变量名可以保留 |
| 权限点 | L46 | `sheets:spreadsheet` / `docx:document` / `bitable:app` / `wiki:wiki:readonly` | 按你用到的文档类型增减 |

如果你的团队不用飞书（用 Google Sheets / Notion / 钉钉），这个 skill 不适用，但它的「写入纪律」一节（L138–146：先读表头、按列名匹配、只写目标列、写完回读校验）值得原样搬去你的文档系统 skill。

### 2. tiktok-automation/tiktok-batch-budget-update（★★★★★）

完全是 TikTok 广告平台「修改预算」弹窗的 DOM 结构和操作纪律，没有品牌参数。唯一隐含的业务假设：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 广告组 ID 取法 | SKILL.md L30–31；`references/set_budget.js` L33；`verify.js` L22 | 正则 `/(\d{15,})\s*$/`，假设广告组名以 15 位以上数字结尾（示例名 `0721-withmayanh-White Essence-BC-护肤人群-7664548737817054485`） | 如果你的广告组名里没有 ID 后缀，要改成按名称匹配，或让用户直接给「名称 → 新预算」清单 |
| 币种说明 | L22 | 「通常 USD」 | 你的广告账户结算币种 |

### 3. tiktok-automation/tiktok-batch-exclude-creators（★★★★★）

纯操作流程。只有两处经验坐标，和你的业务无关，和屏幕分辨率有关：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 第一行复选框坐标 | SKILL.md L20 | `(490, 480)` | 首次运行截图后重新记录 |
| 「保存」按钮坐标 | L43 | `(725, 660)` | 同上 |
| 上限计数 | L12、L38 | `X/200 已选择` | 平台限制，无需改 |

### 4. tiktok-automation/tiktok-creative-id-to-creator（★★★★★）

没有任何业务参数。`38000+ 条` 与 `一次最多 400 个` 都是平台侧的量级与限制。

### 5. kans-analysis/ttms-brand-diagnosis（★★★★★）

没有任何品牌参数。L27 列的是 TTMS 已覆盖市场清单（TH / VN / PH / MY / ID / SG / …），本身就是让你填自己的市场。可以直接用。

### 6. tiktok-automation/tiktok-copy-adgroup-swap-creative（★★★★）

操作流程通用，命名规则一节绑定 KANS 习惯：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 命名规则 | SKILL.md L27–37 | `MMDD-达人用户名-产品-BC-人群-视频ID-`（广告组，结尾带短横线）/ 同上不带短横线（广告） | 你团队的命名规则；如果没有，就保留 L34–37 的推导逻辑（日期 = 建计划当天、达人 = `@` 后面那段、视频 ID = `/video/` 后那串），改掉模板字符串即可 |
| 广告账户 URL | L45 | `ads.tiktok.com/i18n/manage/adgroup?aadvid=<广告账户ID>` | 你的 `aadvid` |
| 典型触发语 | L10 | 「20 美金一天」 | 你的常见日预算 |
| 平台提示文案 | L107 | 「此 TikTok 帖子中的链接将仅面向以下地域显示：越南」 | 你的国家；这只是「属正常、不用处理」的提示举例 |
| 验证示例 | L120 | 「4 条新广告组」 | 只是示例数量 |

### 7. kans-analysis/tiktok-brand-ads-analysis（★★★★）

四维基操（预算规模 / 定向 / 排期 / 创意数量）和大促三阶段节奏都是 TikTok 品牌广告的官方方法论，不绑品牌。要改的只有市场声明：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 市场 | SKILL.md L3、L6、L24 | 「越南市场」「投放市场(应为越南)」 | 你的市场；或者把 L24 改成「投放市场（确认）」 |
| 出价方式 | L29 | 「应为 NoBid」 | 若你的 C-ads 不是 NoBid，改成实际方式 |
| 数值基准 | L36–37、L46、L51–52、L58–65 | `$85K` 拆分临界 / `$100` 下限 / `1→7 天 −6%` / `6–10 条创意` / `VV>1000`、`6s VTR>34%` 等 | 这些来自 TikTok 官方分享；除非你的客户经理给了别的数，否则保留 |

### 8. kans-analysis/tiktok-brand-upper-funnel（★★★★）

是 `ttms-brand-diagnosis` + `tiktok-brand-ads-analysis` 的合并版，主体通用。零散几处：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 市场 | SKILL.md L3 | 「越南等 TTMS 覆盖市场」 | 你的市场 |
| 多账户备注 | L63 | 「曾 6 月两户、7 月一户」 | 删掉或改成你的账户情况 |
| 活动日历 | L132 | Double Day（6.6 / 7.7 / 8.8…）/ Middle Day（14–15 号）/ Payday（25–26 号） | 你所在市场的电商促销节点（如 9.9 / 11.11 / 黑五 / 斋月） |
| 币种口径 | L167 | 「品广消耗一律保留原币 USD 不折算（与 kans-vn-weekly-flow 概览表第 12 行口径一致）」 | 改成你自己的口径；若不用 weekly-flow，把括号删掉 |
| 措辞与配色 | L168 | 环比 红↑ / 绿↓（中国财务习惯） | 若面向英文读者，改成 绿↑ / 红↓ |
| 关联技能 | L171–173 | 点名 `kans-vn-weekly-flow`、`kans-ttms-cads-report-batch` | 按你保留的 skill 改 |

### 9. data-cleaning/tkshop-daren-cleaning（★★★★ 越南 / ★★★ 其他国家）

清洗逻辑（区间取中位数、占位符不当 0、开区间按下界比、中英标签都认）完全通用；绑定的是「中文后台 + 越南盾」这两件事。

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 文件名触发 | SKILL.md L10、L20 | `xxxx-xx-xx_tkshop达人信息.xls` | 你后台导出的实际文件名模式 |
| 原始列名 | L98–99（`WAN_COLS` / `CURRENCY_COLS`）、L101–107（`RENAME_MAP`）、L268–285（派生列的源列名）、L425 | 中文后台的列名：`平均视频播放量`、`客单价`、`每个销售渠道的GMV`、`按商品类目查看GMV占比`、`粉丝性别占比`、`粉丝年龄区间占比` 等 | 若你的后台是英文界面，导出列名会不同，逐个替换 |
| 货币简写 | L169–170 | `(Tr|K|M)?\s*₫`，`Tr` = 越南语「百万」 | 你的货币符号与简写（如 `฿`、`RM`、`Rp`、`$`）；`K/M` 一般通用 |
| 小数格式 | L175、L197 | 越南语逗号是小数点（`1,8Tr ₫` = 1,800,000） | 若你的市场逗号是千分位，把 `replace(',', '.')` 改成 `replace(',', '')` |
| 「万」单位 | L154–166 | 中文后台播放量用「万」 | 英文后台可能是 `K/M`，需要另写分支 |
| 目标类目标签 | L110（`BEAUTY_LABELS`）、`filter_candidates.py` L32 | `{'美妆个护', 'Beauty & Personal Care'}`，派生列名「美妆个护占比」 | 你的主类目（如 `Womenswear`、`Food & Beverage`） |
| 初筛阈值 | SKILL.md L383–391；`filter_candidates.py` L24、L59–64 | 成交 ≥100 / 客单价 ≥131,800 ₫ / 男性占比 ≤60% / 视频占比 ≥50 且 >直播 / 美妆占比 >50% | 你的达人筛选标准；都是命令行参数 |
| 二次分池提示 | L434–436 | 「红精华 / 白精华的分池」 | 改成你自己的产品线名或删掉 |

### 10. kans-analysis/kans-livestream-charts（★★★）

三张图的脚本按「列名契约」读数据，只要你能产出 `date, spend_usd, gmv_usd` 和 `date, short_k, live_k, card_k` 两张 CSV，图就能出。写死的是汇率、盈亏线、事件标注和标题：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 触发词 | SKILL.md L3、L6 | 「KANS 越南」「KANS Campaign 导出」「TTMS Serums & Essences 导出」 | 你的品牌、你的类目名 |
| USD→本币汇率 | SKILL.md L18、L54；`scripts/1_gmv_roi_weekly.py` L26、L144 | `6.8`（USD→RMB） | 你的汇率；或用 `--no-rmb` 保持 USD；若你的结算币不是 RMB，改 `common.py` L85 `fmt_rmb` 的符号 |
| 退款后盈亏线 | SKILL.md L54、L81；`1_gmv_roi_weekly.py` L145 | `4.1` | 用你的佣金 + 物流 + 人力 + 退款率反算出来的 ROI 盈亏点 |
| 大促日 / 拉量日 | `2_livestream_correlation.py` L129–130 | `--promo 06-05 06-06 06-18`、`--ramp 06-17 06-19` | 你的大促日和自播加投日；建议把默认值改为空列表，每次传参 |
| 事件标注 | `3_market_stacked_gmv.py` L23–31（`EVENTS`、`BASELINE_NOTE`） | 「6.5–6.6 大促爆发」「6.18 二次拉量高峰」「≈ $340–460K 区间震荡」 | 换成你当月的事件；文案里 `{peak}/{total}/{live_share}/{dod}` 是自动填数占位符，保留 |
| 图标题 / 图例 | `1_*.py` L131–132；`2_*.py` L75、L92、L103、L111、L115 | 「KANS 越南直播间 …」「KANS 直播GMV」「TTMS · Serums & Essences」 | 你的品牌与数据源名 |
| 原始 xlsx 表头 | `common.py` L97–128（`启动时间` / `成本` / `总收入`）、L130–156（`日期` / `短视频GMV` / `直播GMV` / `商品卡GMV`） | 中文后台导出的表头 | 若后台是英文界面，把这几个表头字符串换掉；或者直接喂 CSV 绕过解析器 |
| 中文字体路径 | `common.py` L21–26 | Linux 下的 Noto Sans CJK / 文泉驿路径 | macOS / Windows 用户加上本机 CJK 字体路径；纯英文图可以忽略 |
| 示例数据 | `examples/*.csv`、`examples/README.md` | 2026-06 的真实快照，README 里写了预期 `r_full=0.430` | 换成你自己的样本后，预期值一起改掉或删掉 |

### 11. kans-analysis/kans-vn-category-competition（★★★）

「两周交集口径」「渠道占比分母 = 五渠道之和」「多店品牌只合并两周全在榜的」这三条口径是脚本的骨架，跟你是谁无关。`common.py` 是唯一真源，业务参数几乎全在这一个文件：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 触发词 | SKILL.md L3、L6 | 「越南美妆个护类目」 | 你的国家 + 类目 |
| 你的店铺名 | `scripts/common.py` L56 | `KANS = "Kans Official Vietnam"` | 你在 FastMoss / Kalodata 榜单里显示的店铺名，**必须与导出完全一致** |
| 你的中文简称 | `common.py` L130（`CN_NAME[KANS]`）；`metrics.py` L50；`chart2_cn_brand_tier.py` L37、L44、L52 | `"韩束"` | 你的品牌简称；`metrics.py` 用 `str.contains("韩束")` 找你自己 |
| 兜底汇率 | `common.py` L57 | `DEFAULT_RATE = 6.75` | 你的 USD→本币汇率；`run_all.py` 强制 `--rate` 必填是对的，别改回默认 |
| 导出列名映射 | `common.py` L60–69（`COLMAP`） | `Store Name` / `GMV (USD)` / `Affiliate Video GMV(USD)` / `Self-Account Live GMV(USD)` / `Shop Tab GMV(USD)` … | 若你的榜单工具列名不同（Kalodata 与 FastMoss 略有差别），改这里 |
| 五渠道名 | `common.py` L51–52 | `达人视频 / 店播短视频 / 店铺自播 / 达人直播 / 商城` | 通用；面向英文读者可改 `NM` |
| 多店品牌映射 | `common.py` L106–125（`MULTI_STORE`） | 珂拉琪 4 店、联合利华 2 店、宝洁 2 店 … 全是越南榜单上的店 | 换成你所在市场的多店品牌；空字典也能跑 |
| 店铺 → 展示名 | `common.py` L129–187（`CN_NAME`） | 越南 Top200 里几十家店的中文名，带 `?` 的是归属待核 | 换成你市场的对手；不认识的先不填，脚本会用原名 |
| 「中国品牌梯队」名单 | `common.py` L189（`CN_TIER`） | `["珂拉琪","卡姿兰","花知晓","韩束","橘朵","菲鹿儿","花西子","兰蓓娜"]` | 这张「图 2」本质是「同阵营对手梯队」，换成你想对标的一组品牌 |
| 涨跌配色 | `common.py` L55 | 涨红跌绿（中文财务习惯） | 英文读者改成涨绿跌红 |
| 大促清单 | SKILL.md L25；`references/pitfalls.md` L68 | 8.8 / 9.9 / 11.11 / 12.12 | 你市场的大促日 |
| 沙箱路径 | SKILL.md L38、L41；`run_all.py` L7、L70 | `/mnt/user-data/outputs`、`/mnt/skills/public/xlsx/scripts/recalc.py` | 本机运行时改成你的输出目录；没有 recalc 脚本就加 `--skip-xlsx` 或改用 LibreOffice 重算 |
| 字体路径 | `common.py` L22–26 | Linux Noto / 文泉驿 | 同 kans-livestream-charts |
| 自检基准值 | SKILL.md L220 | 「大盘 +48.1%、KANS +103.6% 排名 38→23、珂拉琪 4 店 −2.8%」 | 只对 `examples/` 里的越南样本成立；换样本后删掉或重写 |
| references 里的品牌举例 | `pitfalls.md` L34–47、L55、L79；`analysis_playbook.md` L21–28、L72–77；`report_template.md` L32–36 | 用 KANS / 珂拉琪 / 科颜氏 作为口径陷阱的例子 | 方法论保留；例子可换可不换（换了更好读） |

### 12. kans-analysis/ttms-audience-package-strategy（★★★）

§1–§6、§8.1–8.2、§9 是 TTMS 官方 playbook 的口径整理，标了【官方口径】的都可以原样用。绑定 KANS 的是「默认语境」和 §7 配方表：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 触发词 / 默认语境 | SKILL.md L3、L6、L25 | 「绑定 KANS 越南 SKINCARE 语境」「默认语境 KANS 越南 SKINCARE」 | 你的品牌 + 市场 + 类目 |
| 来源文档 | L9 | 飞书 docx `BhRpdo244ou9i1xLtvOlDARngie` | 你拿到的 TTMS Audience Creation Playbook 副本链接，或删掉 |
| 消费力判定 | L82 | 「SEA & AU（含越南）按手机价格档位」 | 若你在 US / METAP 市场，改成 TTAM tagging 那条 |
| Device TikTok Usage | L87 | 「KANS 用不了，不要推荐」 | 若你是手机 / 电信垂类，这条反过来可用 |
| 常用配方表 | L156–169（§7） | 8 个场景全按护肤配：类目 `Beauty & Personal Care › Skincare › Serums & Essences`、hashtag 用护肤 / 抗老词、女性 18–44 | 按你的类目、客单带、人群重写这 8 行；场景框架（拉新 / 截流 / 直播高意向 / 复购 / 看过未买 / 上漏斗承接 / 再营销 / 素材反哺）保留 |
| 行业基准 | L202–212（§8.3） | 高亮 `Beauty and Care` 那行（CPCo 0.03 / 互动率 1.4%），L212 写「KANS 看 Beauty and Care 那行」 | 高亮你所在行业的那一行，改 L212 的指代 |
| 配套 skill 点名 | L171 | `tiktok-creative-id-to-creator` / `kans-vn-weekly-flow` / `tiktok-batch-budget-update` | 按你保留的 skill 改 |

### 13. tiktok-automation/kans-ttms-cads-report-batch（★★）

TTMS 结案页面的表单操作（配额循环、React 受控输入、双月面板选日期、坐标勾选 + 全名校验）是通用的，但**有几段 JS 用业务字符串来定位 DOM**，不改会直接找不到元素。注意这个文件的 frontmatter 出现了两次（L1–4 和 L6–9），改的时候两处都要改。

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 平台 URL | SKILL.md L31 | `marketscope.tiktok.com/brand/report/list?accountId=7501254948374904840` | 你的 TTMS `accountId` |
| 账号名 | L32 | 「KANS Vietnam｜美妆个护」 | 你的 TTMS 账号名 |
| 产品三类 | L40 | `White Essence` / `Red serum` / `素颜霜` | 你的产品短名（写进报告名里的） |
| 导出文件名 | L43 | `Kans--02-Campaign Report-YYYY-MM-DD to YYYY-MM-DD.xlsx` | 你的广告后台导出文件名 |
| 广告组命名格式 | L43、L119、L231 | `MMDD-达人-产品-BC-人群包-素材ID`；校验正则 `^\d{4}-.*-\d{18,19}` | 你的命名格式；正则要跟着改，否则 L119 的水印规避和 L223–237 的勾选校验都失效 |
| 商品 ID → 产品名 | L44–47 | `1731561143212017689 → White Essence` 等三条 | 你的 GMV Max 商品 ID 映射 |
| 报告命名规则 | L24–25、L54、L148 | `素材ID_起投MMDD_截止MMDD_产品名` | 你的规则；L80 / L98 的幂等正则 `\d{15,}_\d{4}_0731` 要同步 |
| 默认分析周期 | L22、L55、L176 | `2026-07-01 ～ 2026-07-31` | 只是举例；第 0 条铁律要求每次都问用户，保留 |
| 归因期限 | L56 | `7 天` | 你的归因窗口 |
| **JS 定位字符串** | L186、L193 | `e.textContent.includes('KANS SKINCARE VIETNAM')`（用来找推广系列列表的滚动容器） | 换成你任意一个推广系列名里一定会出现的子串（如你的品牌名） |
| **JS 过滤正则** | L188 | `/KOL-Brand Consideration\|KANS/` | 换成你推广系列名的共同前缀 |
| 推广系列举例 | L62–71、L205、L216 | 8 个 `KOL-Brand Consideration-…` 系列名、`0629-beebong9909-Red serum-…` | 举例，但 L60 明确要求「每次现场枚举」，逻辑保留 |
| 水印 ID | L119 | `7614060375009969160`、`7642277009700619784` | 你账号的水印数字不同；靠 L119 的正则规避即可，不必手填 |

### 14. kans-analysis/tiktok-vn-kans-live-ops（★★）

这是最早的一版「直播间周报分析师」，几乎所有阈值都是那家店在 2026 年中的目标值。七大板块结构、「人货场流」归因、「不要只看 GMV/ROAS，先看效率 + 漏斗 + 进房质量」这套方法论是通用的；下面每一个数字都要换。

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 触发词 | SKILL.md L3、L6 | 「越南韩束(KANS)SKINCARE」「月目标 NMV160万 / 月底 ROI5」「T3→T2→T1」 | 你的品牌 + 你的月目标 |
| 周报链接 | L7 | 飞书 wiki `EeSlwf4caiAU81k1KoJc1QQUnnh` | 你的周报文档，或删掉 |
| 两条汇率 | L37–38 | `USD × 6.8 = RMB`、`VND ÷ 3700 = RMB` | 你的币种与汇率（注意 `kans-vn-weekly-flow` 后来改成了 3890 / 6.75，两份不一致） |
| 大盘数据源 | L39、L84、L135 | FastMoss（周 GMV 以美元计） | 你用的第三方榜单 |
| 退款率取法 | L40 | 「筛选非合作的 skincare 账号」 | 你的直播间账号 |
| 月目标 / 目标 ROI | L53–54、L114 | NMV 160 万、ROI 4.6（区间 4.5–4.6）、月底 ROI 5 | 你的目标 |
| 盈亏线 | L115 | 退前 5.9 / 退后 4.1 | 你的反算值 |
| 主力 SKU | L67 | 白5 / 白3水+精华+霜 / 白3精+霜+素颜霜 / 白3防晒+精华+面霜 | 你的主力链接与组合 |
| 排班时段 | L74 | 早 08–12 / 中 12–16 / 下 16–20 / 晚 20–00（4 段） | 你的开播时段；`kans-vn-weekly-flow` 用的是 6 班次含凌晨，二者不一致 |
| 视觉结论与目标 | L79–80 | 「专柜卖场型 > 海滩型」、进房率目标 6%（5 月 3.7%） | 你自己 A/B 出来的结论；目标按你现状定 |
| 竞品名 | L84 | COLORKEY / Unilever / Carslan / L'Oréal / Olay | 你的竞品 |
| 相关性基准 | L85 | 「KANS vs 品类大盘 6 月 ≈ 0.9」 | 删掉或换成你算出来的 |
| 商品卡计划层级 | L89 | 账号整体 / 白精华 / 红精华 / 素颜霜 / 防晒 | 你的 GMV-MAX 商品卡计划 |
| 素材分级阈值 | L117–122 | CTR > 1%、转化 > 10%（目标 15%）、KOC 素材 ROI < 1 不投 | 你的素材基准 |
| 承接阈值 | L125–126 | 点击率 ≥ 26%、点击下单率 ≥ 3.5%（中位 3.4–3.7%）、进房率 6% | 你的直播间历史中位 |
| 排班原则 | L129 | 「4–5h/场」 | 你的场次时长 |
| 活动日历 | L56、L103、L130 | Double day / Middle day / Payday | 你市场的促销节点 |
| 长期梯队 | L133–137 | `$30K → $500K`、9 月进 T2（TOP23）、12 月进 T1（TOP6）、月阶梯 7 个数、FastMoss TOP160 四梯队门槛、「KANS ≈ #60/159」 | 全部换成你的市场梯队与目标路径；没有就整段删 |
| 关联技能 | L154–157 | `tiktok-brand-ads-analysis` / `ttms-brand-diagnosis` | 按需改 |

### 15. live-script/vn-kans-script（★★，框架 ★★★★）

这个 skill 要拆开看。**框架层完全可复用**：一轮 6′40″ 十三段（L27–46）、「主播先开口、中控硬广收口」（L47–51）、P0/P1/P2 三种节奏（L53–70）、五种行类型配色（L72–82）、执行红线（L144–153）、手卡工作流四步（L157–207）、xlsx / PDF 输出规范（L245–267）、openpyxl / PIL 技术坑（L270–287）。**产品层全部要换**：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 触发词 | SKILL.md L2–3、L6 | 「VN KANS话术」「越南 TikTok 韩束(KANS)」「1,427K 白系 vs 1,347K 红系」 | 你的品牌 + 市场 + 你最容易混的两个价格 |
| 产品线判别表 | L88–100 | 白系（美白）vs 红系（抗老）的越南语关键词、包装色、原价、核心成分 | 你的产品线；如果只有一条线，整节删掉 |
| 单品与套装价格 | L102–109 | 爽肤水 429K / 精华 499K / 面霜 499K / 原价 1,427,000 / 直播价 8XX K / 优惠 17% | 你的价格与货币 |
| 套装内容提示 | L109 | 「三件套里没有乳液」 | 你的套装边界 |
| 赠品 | L111–117、L205 | 氨基酸洁面 50g 正装 + 5 支次抛（价值 160K） | 你的赠品与价值锚点 |
| 成分讲法 | L119–133 | 「四层抑黑」四个成分及其越南语卡面文案；不讲 `Ticracle Pro` | 你的成分 / 技术点；「只讲卡面上有的」这条规则保留 |
| 证据与背书 | L135–140 | SGS 实测四个百分比、中国官方认证、「抖音第一品牌 / WWD TOP38 / 双研发中心 / 20+ 年 / 200+ 专利」、适用人群 18–60 | 你的检测报告与品牌资质 |
| 越南语固定文案 | L130–131、L203–205 | `14 NGÀY CHO DA SÁNG TRONG TRẺO`、`QUÀ 0 ĐỒNG` 等 | 你目标市场语言的卡面原文；「照抄卡面不另译」这条规则保留 |
| 本地化顾虑 | L217–221 | 越南消费者怕激素 / 怕假货 / 怕不会用 | 你市场的典型顾虑 |
| 翻译列名 | L215、L253–254 | `Tiếng Việt（本地翻译填写）` | 你的目标语言 |
| 字体路径 | L278 | `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`，`index=2` | 本机字体路径；非中文市场换成对应字体 |

### 16. kans-analysis/kans-vn-high-cost-low-roi-hourly（★）

接口重放、拦截器注入、分页停止条件、双维度扫描这些机制是通用的（任何 TikTok Shop 卖家后台的 GMV Max 都是同一个 `post_creative_list` 接口），但 SKILL.md 把一家店的全部计划写死在正文里了：

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 触发词 | SKILL.md L3、L6 | 「KANS 越南 GMV Max」 | 你的品牌 |
| 命中阈值 | L6、L19、L61、L81 | 成本 > ¥70（≈US$10）且 ROI < 2 | 你的「烧钱且没效果」阈值；四处要一起改 |
| VND→本币汇率 | L18、L61、L80、L86 | `mixed_real_cost / 3891` | 你的汇率；接口返回的是店铺本币，若你就想看本币，把除法去掉 |
| 扫描时刻 | L10–11 | 每小时跑当天；本地小时 == 10 或 14 时加跑近 7 天 | 你的时区与节奏 |
| 卖家后台 | L22、L39、L45 | `seller-vn.tiktok.com`、`shop_region=VN`、账号 `Kans Official Vietnam` | 你的国家域名（`seller-th` / `seller-id` / `seller-us` …）、`shop_region`、账号名 |
| 计划清单 | L24–34 | 6 个商品 GMV Max（`campaign_id` / `product_id`）+ 1 个直播 GMV Max（`1000000000000001`） | 你的计划；在后台抽屉 URL 里能直接读到 |
| 抽屉 URL | L39、L45 | 带具体 `campaign_id` / `product_id` | 任选你的一个商品计划和一个直播计划 |
| 输出文件名 | L68 | `KANS_高成本低ROI素材预警_<时间>.xlsx` | 你的命名 |
| 接口字段名 | L16–18 | `onsite_mixed_real_roi2_shopping`、`lod_shop_direct_onsite_mixed_real_shopping_roas`、`order_field='mixed_real_cost'` | 平台字段，保留 |

### 17. kans-analysis/kans-vn-weekly-flow（★）

13 步编排、GMV 五口径对照、交叉核对阈值、UV 三条铁律、转化率只保留三个、82 条已知坑 —— 这些是骨架，跟品牌无关，而且是这个仓库里最值钱的部分。但正文与脚本里塞满了一家店一个月的具体数字。建议分两步：先改 `scripts/_config.py`，再按下表把 SKILL.md 里的清单换掉；脚本里带「本期数据」的那几份当模板看。

**SKILL.md 正文**

| 参数 | 位置 | 原值 | 换成什么 |
|---|---|---|---|
| 触发词 | L3、L6 | 「KANS 越南 SKINCARE 直播间」 | 你的品牌 + 直播间 |
| 交付目录 | L18、坑 50（L488）、坑 82（L523） | `…/VN-TK-复盘/<期次文件夹>/` | 你的复盘文件夹 |
| 月目标 | L21、L36、L367 | 「NMV 160万（旧）」vs「退后 120万（当月）」 | 你的月目标；L36 那条「问清楚是哪个口径」保留 |
| 两条汇率 | L38–42 | `VND ÷ 3890`、`USD × 6.75` | 你的币种与汇率；「每期开工必须确认」保留 |
| 平台服务费 | L46、L96、L105、L167、L213、L361 | 广告消耗 `×1.04`（VXP） | 你的平台附加费率；没有就删掉所有 `×1.04` |
| 盈亏线 | L48、L106、L146、L148、L162、L419 | 退后 ROI `4.1`；退前达标线 `4.1 ÷ (1−退款率)` | 你的反算值；换算公式保留 |
| 大盘数据源 | L119–121、坑 34（L463） | Kalodata「越南美妆个护」（`country: VN`）/ TTMS `Beauty & Personal Care › Serums & Essences` | 你的国家 + 类目 |
| 退款率过滤 | L154、L158 | `Creator Handle=kans.skincare_vn`；状态值中文 `已发货 / 已取消 / 已完成` | 你的直播间 handle；后台语言不同时状态值也不同 |
| 竞品榜 | L172–173 | TikTok 官方 Top200；`TOP30 + KANS 双位置` | 你的榜单来源；「自播 + 达播必须同时看」保留 |
| 直播 campaign ID | L228 | `1000000000000001` | 你的直播 GMV-MAX 计划 |
| 商品卡 15 列 | L223–225 | 固定列名 | 通用，保留 |
| 单链接判定清单 | L245–256 | 5 条商品 ID（`1734360557016744985` 等）+ 简称「白3 / 白 single / 白7 / 白3 / 白2」 | 你的主力链接；「清单固定、其余汇总成一行」这条规则保留 |
| 品线关键词 | L259 | 红系 `collagen\|lão hóa\|nếp nhăn\|black waist\|peptide`；白系 `niacinamide\|trắng\|thâm\|…` | 你的产品线在商品标题里的关键词（目标市场语言） |
| 主播表 | L283、坑 18（L447）、坑 74–75（L515–516） | Google Sheet「REPORT PERFORMANCE … SKINCARE」，`Tháng 0X \| SKINCARE` 分页，中文名列，行尾 `#N/A` 平衡行 | 你的主播排班 / 业绩表结构 |
| 时段划分 | L299 | 6 班次：06–10 / 10–14 / 14–18 / 18–22 / 22–02 / 02–06 | 按你的开播时间切，但「必须覆盖 24h」这条保留 |
| 排班表 | L303 | 不读 `CHICMAX LIVESTREAM INHOUSE LỊCH` | 你的排班表名（或删掉这条） |
| 别的直播间 | L305 | 「KHTH」 | 你的其他直播间简称 |
| 飞书目标文档 | L309 | `直播周会-杨佳林-KANS`（docx） | 你的周会文档 |
| 文件命名 | L354、L358、L423 | `KANS_VN_<期次>_…`、标题 `8.31-9.6日复盘-SKINCARE直播间` | 你的命名法 |
| 店铺名 | 坑 10（L439） | `Kans Official Vietnam` | 你的店铺名 |
| 数字格式 | 坑 11（L440）、坑 31 | 越南「点 = 千分位、逗号 = 小数」 | 你市场的数字格式；欧洲市场同越南，英语市场反过来 |
| 关联技能 | L561 | 四个 skill 名 | 按需改 |

**scripts/**

| 文件 | 位置 | 内容 | 处理方式 |
|---|---|---|---|
| `_config.py` | L4–13 | `PERIOD` / `W1` / `W2` / `VND=3890` / `USD=6.75` / `BREAKEVEN=4.1` / `OUT='/home/claude/w/out'` / `SKILL_CHART='/root/.claude/skills/synced/kans-livestream-charts/scripts'` | 每期只改这里；两条路径改成你本机的输出目录和 `kans-livestream-charts/scripts` 所在位置 |
| `kol_koc.py` | L26–35 | 计划名 → 商品 ID 映射（7 条）、`LINE` 品线分组 | 换成你的 GMV-MAX 商品卡计划与品线 |
| `s105.py` | L15–24、L64–65、L75–76、L109–117 | 7 条计划的两期成本 / 收入、上期 KOL 占比、目标 ROI、预算 | **内嵌了一期真实数据**，当模板：保留结构，把数字换成从导出里读 |
| `s11.py` | L22–28、L37–38、L51、L89 | 5 条链接 + 上期值、红 / 白系正则、上期品线合计、红系两条大链 | 同上 |
| `gmvmax_card.py` | L29–35、L88、L98–100 | 商品卡两期数据元组、品线说明、结论文案 | 同上 |
| `seg5_chart.py` | L28–30、L112 | `A` / `B` 两期 CLP 指标字典、顶部「一句话」 | 同上；README 已注明「每期手改」 |
| `host_periods.py` | L10、L27–28 | Google Sheet 名、`host_raw.txt` 十列约定 | 表名换掉；列约定可以照用 |
| `step12_charts.py` / `host_period_chart.py` / `std_charts.py` | 标题与页脚（`step12` L7–8、L112–121；`host_period_chart` L84、L90；`std_charts` L121、L235、L268） | 「KANS 越南 SKINCARE 直播间」「REPORT PERFORMANCE｜KANS › Tháng 08」「Kalodata 美妆个护」 | 换成你的品牌与数据源名 |
| `style.py` | L68 | 字体 `Noto Sans CJK JP / WenQuanYi` | 本机字体 |

### 18. personal/touji-zhilu-playbook（不适用）

一个人的 Telegram 频道阅读存档与方法论检索，和电商没有关系；公开仓库里也已按 `scrub.sh` 删掉了原帖全文。不需要定制，接入你自己的 skill 库时直接跳过或删除目录。

---

## 三、按业务类型的接入路径

### a) 你也是 TikTok Shop 越南卖家

这是改动最少的情况：汇率、数字格式、卖家后台域名、活动日历、货币简写全都能直接沿用。

- **直接用**：`feishu-docs`（如果你用飞书）、`tiktok-batch-budget-update`、`tiktok-batch-exclude-creators`、`tiktok-creative-id-to-creator`、`ttms-brand-diagnosis`、`tiktok-brand-ads-analysis`、`tiktok-brand-upper-funnel`、`tkshop-daren-cleaning`（只改初筛阈值和目标类目）。
- **改参数即可**：`tiktok-copy-adgroup-swap-creative`（命名规则）、`kans-livestream-charts`（汇率、盈亏线、事件）、`kans-vn-category-competition`（店铺名、对手映射、梯队名单；如果你也是美妆个护，`MULTI_STORE` / `CN_NAME` 大半能直接用）、`ttms-audience-package-strategy`（§7 按你的类目重写）、`kans-vn-high-cost-low-roi-hourly`（计划清单、阈值、账号）、`kans-ttms-cads-report-batch`（accountId、命名格式、JS 定位字串）。
- **先改 `_config.py` 再逐步接**：`kans-vn-weekly-flow` 和 `tiktok-vn-kans-live-ops`。建议先用 `kans-livestream-charts` 单独跑出图 1–3，再按 weekly-flow 的 Step 2 / 4 / 5 / 9 / 12 一步步替换清单，不要试图一次跑全 13 步。两份 skill 的目标值（月目标、盈亏线、排班时段、汇率）互相不一致，以 `kans-vn-weekly-flow` 为准，`tiktok-vn-kans-live-ops` 是早期版本。
- **借框架重写内容**：`vn-kans-script` 的 13 段 / 手卡 / 红线 / xlsx 规范原样留，第三节「产品与数字」整节重写。

### b) TikTok Shop 其他国家（泰国 / 印尼 / 马来 / 菲律宾 / 美国 / 英国 …）

平台一样，后台接口和 DOM 一样，所以自动化类 skill 基本无损；分析类 skill 要换掉所有「越南」和 VND 相关的东西。

- **直接用**：`tiktok-batch-budget-update`、`tiktok-batch-exclude-creators`、`tiktok-creative-id-to-creator`、`tiktok-copy-adgroup-swap-creative`（改命名与 L107 的国家提示）、`ttms-brand-diagnosis`、`tiktok-brand-ads-analysis`（改 L24 市场）、`tiktok-brand-upper-funnel`（改 L132 活动日历）、`feishu-docs`。
- **改参数**：
  - `kans-vn-high-cost-low-roi-hourly`：L22 域名换成你的国家（`seller-th.tiktok.com` 等）、L39 / L45 的 `shop_region`、L18 汇率换成你的本币；其余照用。
  - `kans-ttms-cads-report-batch`：TTMS 是跨市场产品，只改 accountId、命名、JS 字串。
  - `ttms-audience-package-strategy`：L82 消费力判定按你所在区域（SEA/AU 按机价，US/METAP 按 TTAM tagging），§7 重写。
  - `kans-livestream-charts`、`kans-vn-category-competition`：汇率和币种符号；`COLMAP` 在 FastMoss / Kalodata 各国导出里一致，通常不用改；`CN_NAME` / `MULTI_STORE` / `CN_TIER` 要从零填你市场的对手。
  - `tkshop-daren-cleaning`：L169–175 的货币简写与小数格式是主要改动点；英语市场（US / UK）后台导出可能是英文列名，L98–107、L268–285 也要改；`Tr` 这个越南语百万单位删掉。
- **只借骨架**：`kans-vn-weekly-flow`（Kalodata 的 `country` header、越南数字格式、越南语品线关键词、Tháng 分页名全都要换）、`tiktok-vn-kans-live-ops`、`vn-kans-script`（越南语文案与本地顾虑整节重写，目标语言列名改掉）。

### c) 非 TikTok 电商（Shopee / Lazada / 抖音电商 / 亚马逊 / 独立站）

浏览器自动化类 skill 对着的是 TikTok 后台的 DOM，换平台等于重写，**不适用**：`tiktok-batch-budget-update`、`tiktok-batch-exclude-creators`、`tiktok-creative-id-to-creator`、`tiktok-copy-adgroup-swap-creative`、`kans-ttms-cads-report-batch`、`kans-vn-high-cost-low-roi-hourly`。它们值得学的是纪律而不是代码：只读一次再写、写完另起一次调用回读、提交前列对照表让人确认、绝不自动点不可逆按钮。

TTMS 三件（`ttms-brand-diagnosis`、`ttms-audience-package-strategy`、`tiktok-brand-upper-funnel` 的 ttms 模式）和 `tiktok-brand-ads-analysis` 依赖 TikTok 的品牌广告产品与人群体系，**不适用**；不过「上漏斗看 CPCo 与 Co 人群、不看 GMV」这个判断框架可以平移到任何平台的品牌广告。

能跨平台的是数据处理与复盘方法：

- `feishu-docs`：完全无关平台，直接用。
- `tkshop-daren-cleaning`：换成你平台的达人导出后，清洗规则（区间取中位、占位符不当 0、中英标签双认、单条件命中数打印）都能复用，改列名和货币即可。
- `kans-livestream-charts`：只要你能给出「日期 / 花费 / GMV」和「日期 / 各渠道 GMV」两张表，三张图不认平台。抖音电商用户把 USD 相关参数换成 `--no-rmb` 直接看人民币。
- `kans-vn-category-competition`：需要一个类目级店铺榜单（抖音有蝉妈妈 / 达多多，Shopee 有第三方榜单），把 `COLMAP` 映射到你的榜单列名、渠道名 `NM` 改成你平台的渠道划分（如「自播 / 达播 / 商城 / 短视频」）；两周交集口径、多店合并、加权 vs 中位数校验这三条方法论完全平台无关。
- `kans-vn-weekly-flow` 与 `tiktok-vn-kans-live-ops`：把它们当「直播电商周报方法论」读，而不是当脚本跑。GMV 多口径对照、退款率与盈亏线反推、UV 三铁律、主播 × 时段格子表、上期建议反向验证 —— 这些在抖音直播间里同样成立；Step 13 写飞书那段如果你用飞书也能直接用。
- `vn-kans-script`：直播话术框架是平台无关的，越南部分整节替换即可。

---

最后一句实操建议：改任何一个 skill 之前，先把它的 `description` 改成你自己的触发词并在对话里试一次，确认能被正确触发；再改正文口径；脚本放最后。触发词错了，后面改得再对也不会被用到。
