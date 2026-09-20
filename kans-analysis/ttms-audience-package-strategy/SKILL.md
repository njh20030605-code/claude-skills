---
name: ttms-audience-package-strategy
description: "TTMS（TikTok Market Scope）人群包策略顾问 + 种草广告（C-ads）承接。当用户要「打人群包/建受众包/这个目标选什么标签/ACC 和 TikTok Shop 标签怎么选/视频受众估算不出规模/人群包推不到 TTAM/开 R&F 要多久/人群包过期/新品包爆品包怎么分/种草广告怎么搭计划/CPCo 多少算好」时使用。绑定 KANS 越南 SKINCARE 语境，不做浏览器自动化。"
---

# TTMS 人群包策略手册（KANS 越南）

来源：
- TTMS | Audience Creation Playbook（飞书 docx BhRpdo244ou9i1xLtvOlDARngie）
- 「投放实操场景复现 for 种草长效转化」官方页（计划搭建 / 计划优化 / 行业 Benchmark）

【官方口径】= 原文。【策略建议】= 基于机制的经验推导，可推翻。

## 0. 回答姿势

用户抛来一个业务目标（拉新 / 承接 / 复购 / 召回 / 竞品截流 / 种草 / R&F 铺量），按这个顺序回：

1. **先定漏斗位置**：这个包是要「找没见过我的人」还是「捞已经动过手的人」。
2. **再选标签大类**（§1 决策树），不要一上来就堆条件。
3. **给可直接照抄的参数**（数据范围 / 动作 / 回溯天数 / 规模预期）。
4. **接上消费端**（§8）：这个包放进哪种计划、include 还是 exclude。
5. **报排期提前量**（§4），尤其要上 R&F 的包。
6. **过一遍避坑清单**（§6）。

默认语境 KANS 越南 SKINCARE。目标模糊（"帮我打个人群包"）先问一句：这个包是给**种草广告（C-ads）**、**直播 GMV Max**、**商品卡 GMV Max**还是**品牌 R&F** 用的 —— 投放目的不同，标签完全不同。

## 1. 标签大类决策树【官方口径】

```
按漏斗阶段圈人，不自定义规则        → Brand audience › ACC audience
捞我某条广告/某个账户触达过的人      → Brand audience › Ad audience
按商品互动圈人（价格带/类目/直播场景） → Vertical audience › TikTok Shop audience
按视频内容互动圈人（种草/达人内容）   → Content & intent audience › Video audience
任一 + 收窄                              → Demographics / Device / Interests & behaviors
```

### 1.1 Brand audience

**ACC audience** — 按 Awareness / Consideration / Conversion 划人，规则固定不可改。
- 应用：把上漏斗互动人群往下漏斗推。
- 官方示例：建 Consideration 包 → 投 Shop Ads 收高意向转化。

**Ad audience** — Touchpoint（Topview / Reach & Frequency / TikTok Pulse / Brand auction-Reach，分 Upper/Middle/Lower funnel 三级）、Advertiser ID、Campaign ID、Ad Group ID。
- 应用：分析广告受众；对特定 campaign 触达过的人再营销；把 A 账户的人群拿到 B 账户激活。

### 1.2 Vertical audience › TikTok Shop audience（New）

可用性：开通 TikTok Shop 的市场（越南在内）全部广告主，**以 E-commerce vertical 接入 TTMS 的品牌除外**。

| 参数 | 口径 |
|---|---|
| Data range | **Brand**：与本品 TTS 商品互动过的本国用户，**必须绑定 ≥1 个 TikTok Shop ID**；**Market**：本国全品牌全类目 TTS 互动用户，非 TTS 广告主也能用 |
| Product category | TTS 一/二/三级类目 |
| Price | 双滑块或手输，默认 0–2000 USD，可填更大。逻辑=与该价格带内**单个商品**发生过点击/加购/购买/搜索 |
| Item keyword | 按**商品标题**匹配，Include/Exclude、多值、可存词组。**只准用品牌名** |
| Action scenarios | All / LIVE / Video / Product card（TT Mall、Showcase） |
| Action | Impression / Click / Add to cart / Purchase / Search。**Search 仅 All 场景可选** |
| Frequency | Any / Specific |
| Date range | **单条件最长 30 天**；要更长周期就加多条不同日期条件合并进同一个包 |

### 1.3 Content & intent audience › Video audience（New）

**全地区全垂类可用，但仅 TTMS 标准版**。

**Step 1 视频选择**
- **Video source**：`Brand` = 被归类为"品牌相关"的视频（品牌关键词命中，或经 TTAM ID / 企业号 ID 识别）；`Market` = 本国所有已接入 TTMS 品牌相关的视频。
- **Vertical**：本国全部一级垂类，**建议全选**扩大视频池。**仅 Market 源可用**。
- **Content type**：IGC（TikTok One / Affiliate 委托、发布或引发；泰国、美国额外包含 potential collaborated videos）/ BGC（企业号）/ UGC。
- **Video IDs**：指定视频 ID 做画像或重定向。**仅 Brand 源可用**。
- **Upload period**：**最长 180 天**。
- **Keyword / Hashtag**：Include 命中标题与画面文字，Exclude 排除；**部分匹配 + 不区分大小写**；hashtag **必须带 #**；可存词表；**只准用品牌名**。

**Step 2 受众设置**
- **Action**：Impression / Video views at 100% / Share / Comment / Like / Click / 6-second video views。多选是 **OR**。**Click 与 6-second video views 只对付费内容可用**。
- **Frequency**：Any / Specific。
- **Date range**：**最长 60 天**。官方建议先用 **15 或 30 天**，不要一上来 60/90/180（短窗口意向新鲜、稀释少）。

### 1.4 收窄类标签

**Demographics**
- Location / Gender / Age：同步 TTAM Demographic Targeting。
- **Spending power**：US & METAP 用 TTAM tagging；**SEA & AU（含越南）按手机价格档位** —— 本国机价排名前约 **30–45%** 判为高消费力。
- **Audience personas**：预置 8 个（Midlife / Young Adult / Gen Z / Seniors × High / Low Spenders，另有 Moms 等）。

**Device**
- **Device price（New）**：按当前手机上市时官方零售价。
- **Device TikTok Usage（New）**：按在当前设备首次登录 TikTok 至今时长。**仅手机与电信垂类可用**；仅含 30 天未换机用户；不等于真实持机时长。**KANS 用不了，不要推荐**。
- OS version / Device model / Connection type：同步 TTAM Device Targeting。

**Interests & behaviors**（均同步 TTAM）：Interests（付费+自然）、Video / Creator interactions（自然）、Purchase intention（站内外信号）。

## 2. 操作三步【官方口径】

1. **Create**：① TTMS 内选标签组合建新包；② **TTAM Synchronization** 把已上传到 TTAM 的人群同步进来管理/激活。（TTMS 不支持直接上传一方人群；走 TTAM 上传再同步。）
2. **Add Condition**：从标签库选，或以已有受众为底；AND / OR 组合。
3. **Review & Manage**：Audience List 里 `… > Details` / `Delete`；处理中 = **Calculating**；变 **Available** 后才能看 Profile 或 Push。

## 3. 受众画像与 TGI【官方口径】

Profile 可看：personas、年龄分布、性别占比、Top 10 地区、设备类型、OS 版本、Top 10 兴趣。

**TGI = 属性在你人群中的占比 ÷ 在大盘中的占比 × 100**，>100 = 更集中。

【策略建议】TGI 是判断"圈对人没"最快的指标：若 25–34 女性 TGI 只有 105、Gen Z 男性 TGI 到 130，说明素材/关键词跑偏，回去改 Video source 或 hashtag，别直接推去投。

## 4. 排期与提前量【官方口径】

| 动作 | 时长 | 在哪看 |
|---|---|---|
| 建新人群包 | 最长 3h | Availability |
| 推送到 TTAM | 最长 3h（Pushing 状态 ≤2h） | Push record |
| 开启 R&F | **最长 12h** | 悬停 Push record 下的小字 |

**Availability**：`Available` 可推可画像；`Unavailable` 三因 —— <1000 人 / >该国 TikTok MAU 的 80% / 已过期。
**Push record**：`Not pushed` / `Pushed` / `Pushing`（≤2h）/ `Failed`（可重试）。
**R&F 小字**：`Enabled for Reach & Frequency` / `R&F enablement in progress`（≤12h）/ 无小字（尚未开启）。

【策略建议】普通包提前半天；**要上 R&F 的包至少提前 1 个自然日**（3h+3h+12h≈18h，且 R&F 处理必须在推送到 ≥1 个广告账户后才计时）；大促前统一提前 2 天。

## 5. 激活【官方口径】

**推送到 TTAM**：搜到广告主账户 → Push → 同步完成后在广告计划里用。

**R&F 两种场景**
- **新包**：状态 Available → Push → 选 TTAM ID 并打开 R&F 开关 → `Push to [x] accounts` → Confirm。**一旦开启不可撤销**。
- **已推送的包**：Push → 在 **Pushed** 列表选中已推送账户 → 打开 R&F 开关。

**推送注意**
- 只有规模 **>1000** 才能计算和展示。
- **18 岁以下不可选取、不可画像**（合规）。
- TTAM 同步的人群**每日刷新**；TTAM 删除后 TTMS 显示 Unavailable，有延时。
- TTAM 与 TTMS 的规模/画像估算有细微差异。

## 6. 避坑清单（提交前逐条过）

**建包**
- [ ] 关键词只用品牌名（Item keyword 与 Video Keyword/Hashtag 都有此限）。
- [ ] hashtag 带了 `#`。
- [ ] Vertical 筛选仅 **Market** 源可用；Video IDs 仅 **Brand** 源可用 —— 别配反。
- [ ] Video audience 的 Action 多选是 **OR** 不是 AND；"既点赞又评论"做不到。
- [ ] Click / 6-second video views **仅付费内容有效**，纯自然种草人群别选。
- [ ] TikTok Shop 选 Brand 数据范围前先绑 ≥1 个 TikTok Shop ID。
- [ ] TikTok Shop 单条件 ≤30 天；要 90 天就配 3 条合并。
- [ ] Video audience 回溯 ≤60 天、上传周期 ≤180 天。

**规模**
- [ ] 规模在 1000 ~ 该国 MAU 的 80% 之间。
- [ ] **Video audience 估不出规模是常态**。要能实时估算必须同时满足：①关键词 ≤50 个；②日期 ≤30 天；③**Market 数据范围下只选 1 个 Action**（Brand 不限）；④受众设置里只有 **1 张 Video Audience 卡片**。估不出就按这四条降配重试。

**维护**
- [ ] 有效期：**2026 年 8 月起延长到 365 天**（旧文案里 Unavailable 原因仍写"创建超过 6 个月"，**以 365 天为准**）。
- [ ] **Auto-update 默认不开**（改为 opt-in，减系统负载）。Available 后可 `Update Now`，或开 **7 / 15 天**自动更新。
- [ ] **Auto-update 满 60 天自动暂停**，需手动重启；暂停**不影响有效期**。
- [ ] 【策略建议】核心包**每季度重建一次**吃新数据。

## 7. KANS 越南常用配方【策略建议】

越南 = SEA，消费力按机价档位；越南已开通 TTS，TikTok Shop audience 可用。

| 场景 | 配方 |
|---|---|
| **种草拉新（泛护肤）** | Video audience：source=Market，Vertical 全选，Content type=IGC+UGC，Upload 90 天，hashtag 用护肤/抗老词；Action=Video views at 100%+Like+Comment，Date 30 天。叠女性+高消费力+18–44 |
| **类目截流（竞品加购未买）** | TikTok Shop：Market，Category=Beauty & Personal Care › Skincare › Serums & Essences，Price 对准本品客单带，Action=Add to cart，30 天×3 条覆盖 90 天 |
| **直播场景高意向** | TikTok Shop：Market，场景=**LIVE**，Action=Click+Add to cart，30 天。越南直播间最贴合的包 |
| **本品复购/召回** | TikTok Shop：**Brand**，Action=Purchase，30 天/条叠到 90–180 天；召回时在 TTAM 侧排除近 30 天已购 |
| **看过直播未下单** | 两包做差：A=Brand+LIVE+Impression/Click（30天）；B=Brand+Purchase（30天）。**TTMS 不做减法，在 TTAM 定向里把 B 设为 exclude** |
| **上漏斗承接** | ACC 取 Consideration 包 → Shop Ads / 商品卡 GMV Max |
| **广告再营销** | Ad audience 按 Campaign ID / Ad Group ID 取近期高消耗计划触达人群，或按 Touchpoint 取 Topview / Pulse 人群二次收口 |
| **达人素材反哺** | Video audience：source=**Brand** + Video IDs 填爆量作品 ID → 先看 Profile 摸画像，再决定要不要建重定向包 |

配套：素材 ID → 达人用户名反查走 `tiktok-creative-id-to-creator`；周报里人群包表现归因走 `kans-vn-weekly-flow`；批量改预算走 `tiktok-batch-budget-update`。

## 8. 人群包怎么花出去：种草广告（C-ads）实操【官方口径】

人群包本身不产生价值，装进计划才产生。种草长效转化的标准打法：

### 8.1 计划搭建：单品单 Campaign、单计划单素材

**Key Action 1 定向人群**
- **性别年龄**：建议定向**购买人群**的年龄和性别（不是内容受众的）。
- **消费力 Spending power**：**高客单价商品建议定向 High spending power**。
- **自定义人群包**（include / exclude 两栏）—— 按商品阶段分两套：

| | 新品人群包 | 爆品人群包 |
|---|---|---|
| 目的 | **精准拦截**转化意向购买用户 | **破圈扩量**潜力兴趣用户 |
| 用什么包 | 类目购买包 ｜ 品类功效卖点词 × 搜索包 | 关联行业兴趣人群包 ｜ 竞品种草互动人群包 |

【映射到 §1 标签】类目购买包 = TikTok Shop audience（Market + Category + Purchase）；功效卖点词×搜索包 = TikTok Shop（All 场景 + Search + Item keyword）；行业兴趣包 = Interests & behaviors；竞品种草互动包 = Video audience（Market 源）。

**Key Action 2 预算管理**：**Ad Group 粒度日预算**（如 Daily 20.00 USD），设置起止时间（注意时区），需要时配 Dayparting。

**Key Action 3 素材设置**：**一个 ad group 对应一条素材**，做素材赛马测试。

### 8.2 计划优化：素材赛马，放大深度种草素材

- **Key Action 1 素材赛马**：看 **Cost per consideration（CPCo）** 与 Paid likes / Paid shares / Paid comments / Paid follows。
- **Key Action 2 预算加码**：选取**高互动 + 低种草成本**的素材加预算（Change Budget），差的 ad group 置 Paused，好的 Enabled。

### 8.3 行业 Benchmark【官方口径】

| 行业 | CPCo | 互动率 | 互动成本 | 点赞成本 | 评论成本 |
|---|---|---|---|---|---|
| **Beauty and Care（KANS 对应）** | **0.03** | **1.4%** | **0.03** | **0.1** | **28.7** |
| Food and Beverage | 0.02 | 1.4% | 0.03 | 0.1 | 15.5 |
| Health Products | 0.04 | 1.7% | 0.04 | 0.2 | 37.2 |
| Apparel and Accessories | 0.03 | 2.2% | 0.02 | 0.2 | 31.0 |
| Consumer Electronics & Electrical Appliances | 0.02 | 1.4% | 0.03 | 0.1 | 21.7 |
| Lifestyle and Home | 0.03 | 2.3% | 0.02 | 0.1 | 20.7 |
| **TTL（大盘）** | 0.03 | 1.5% | 0.03 | 0.1 | 25.8 |

【用法】KANS 看 **Beauty and Care** 那行：CPCo > 0.03 或互动率 < 1.4% 就是低于行业，先怀疑两件事 —— ①人群包圈偏了（回 §3 看 TGI）；②素材不行（赛马换掉）。先排人群再排素材，因为定向错了素材再好也无法救。

【策略建议】新包上线后先跑 3–5 天再下结论；判死看 CPCo 与互动率两个指标、不看单日波动。每个人群包至少配 2–3 条素材赛马，否则分不清是人群问题还是素材问题。素材预算加码建议每次 +30~50%，别一次翻倍。

## 9. 高频 FAQ 速答【官方口径】

**Q：TTMS 和 TTAM 预估规模为什么不一样？**
① TTAM 在估算值接近/超过总 DAU 时套 **0.6–0.9 乘数**封顶；② TTMS 只算 **L30D MAU** + **同运营国家** + **>18 岁**的可变现人群。

**Q：看广告受众时 TTMS 规模和 TTAM 触达对不上？**
- **活动层级：TTMS < TTAM**（TTMS 按 MAU / >18 岁 / 行为 / 国家筛得更严）。
- **汇总所有广告触点：TTMS > TTAM**（**TTAM 触达报告不含 GMV Max**，此时 TTMS 更全面）。

**Q：创建 Ad Audience 时 Waiting / Not open？**
`Waiting` = 广告主 ID 已关联且已在 Account Setting 开启；`Not open` = 已关联但未开启，去 Account Setting 打开。

**Q：ACC 的 Conversion 和 TikTok Shop 标签区别？（TTS 品牌常问）**

| 维度 | ACC Audience Tag | TikTok Shop Audience Tag |
|---|---|---|
| 核心差异 | 按固定 ACC 规则算出 | 可自定义 |
| 方法论 | 基于与品牌相关**视频内容**（BGC/UGC/Creator）**及** TTS 资产（商品/商品卡）的互动分类 | 仅基于与 **TikTok Shop 商品卡**的互动（视频、直播、TT Mall、Showcase） |
| 用户行为 | 按 ACC TikTok Shop Purchase Model 固定规则（如 L180D 内在你店成交 → Conversion） | 建包时**自选一种**互动：曝光/点击/加购/购买/搜索 |
| 数据范围 | 仅品牌受众 | Brand（仅本品）或 Market（全市场 TTS 活跃互动用户） |

一句话：要"标准漏斗、与 TTAM 口径对齐"用 ACC；要"按价格带/类目/直播场景精细捞人"用 TikTok Shop。