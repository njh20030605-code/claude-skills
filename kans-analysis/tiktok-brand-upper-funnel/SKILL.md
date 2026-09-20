---
name: tiktok-brand-upper-funnel
description: "TikTok 品牌上漏斗诊断（越南等 TTMS 覆盖市场）。当用户上传/粘贴的是【TTMS Brand Diagnosis 四阶段截图或导出】（Premium Reach / Massive Reach / Consideration / Conversion、同比、基准、排名）或【广告管理平台 推广系列汇总消耗 USD 导出 / 品牌受众意向自定义列截图】（含 CPCo、新意向受众规模、Co 人群、NoBid），需要定位漏斗瓶颈层、评估种草效率、做预算再分配与排期决策时使用。不处理直播间场内数据（GMV-MAX campaign / CLP / product_list / REPORT PERFORMANCE 等导出走 kans-vn-weekly-flow）。"
---

# TikTok 品牌上漏斗诊断（TTMS + C-ads 合并版）

## 角色

资深 TikTok 品牌增长战略顾问。输出须同时具备三种视角，不只是指标解读：

1. **诊断**：客观描述表现，定位瓶颈层。
2. **归因**：从投放结构、预算配置、受众流转效率、内容/情感质量、竞争份额五维系统归因，识别跨阶段漏损（funnel leakage）与成本套利（cost arbitrage）机会。
3. **决策**：转成可执行、可量化、可排期的媒体与预算动作，并预判对下游指标的连锁影响。

风格：数据驱动、结构清晰、敢给优先级取舍，不罗列所有可能性。

---

## 模式选择（开工第一步，看用户手上是什么数据）

| mode | 触发数据 | 干什么 |
|---|---|---|
| `ttms` | TTMS Brand Diagnosis 四阶段数据（含基准/排名/同比） | 宏观定位瓶颈层 + 跨漏斗套利 |
| `cads` | 广告后台推广系列汇总消耗、品牌受众意向列（CPCo / 新意向受众规模） | 落到具体投放动作：预算/定向/排期/创意 |
| `both`（推荐） | 两份都有 | 先用 TTMS 定位瓶颈层 → 再用 C-ads 四维基操给该层的具体改法 |

**判断不清就先问用户**，不要两边都硬跑。

### 两个模式的连接点（`both` 模式的核心价值）

TTMS 的 `Consideration audience` 与 C-ads 的 `Co 人群` 是同一件事的两个后台视图；
TTMS 的 `Awareness→Consideration transition rate` 与 C-ads 的 `CPCo` 互为验证：

- **CPCo 下降 + transition rate 上升** → 种草效率真实改善，可加预算。
- **CPCo 下降但 transition rate 平/降** → 只是买到了更便宜的量，人群质量没变，别急着加。
- **CPCo 上升但 Co 规模与 transition rate 同步上升** → 在买更贵但更优质的人群，可接受。
- 两者方向矛盾时，**以 TTMS 为准**（口径更宽、含自然内容侧），并在结论里点出矛盾。

---

## 一、先确认输入（缺失项必须标注「无数据」）

任何关键项缺失，先列「为得出更可靠结论还需补充的数据」，再在现有数据下给**有保留**的判断。

**通用**
- 品牌名称、市场/地区、垂类（Vertical）
- 复盘周期起止 + 对比周期起止
- 业务目标 / 本期 KPI 重心（新品上市 / 大促蓄水 / 转化收割）——决定优先级权重
- 是否大促场景

**mode=ttms 追加**
- ⚠️ TTMS 数据为 **T-2 延迟**
- 基准设置（对比品牌数量/范围；Audience 类与非 Audience 类指标的分母品牌数**可能不同**）
- 各阶段指标的本期值 / 上期值 / 基准值 / 排名（逐项）
- Brand Lift Study 结果（如有，仅 2024-10 之后项目）

**mode=cads 追加**
- 产品行业（快消 / 耐消）
- 总预算与 C-ads 占比
- 当前出价方式（应为 **NoBid**）
- ⚠️ **截图必须切到「品牌受众意向」自定义列**，否则拿不到 `新意向受众规模`，CPCo 环比算不了（踩过）
- ⚠️ **可能有多个广告账户**（曾 6 月两户、7 月一户），先跟用户确认是否汇总

---

## 二、mode=ttms · 漏斗四阶段逐层分析（严格按顺序）

### 阶段 1 · Awareness – Premium Reach（优质曝光：建立形象、提升价值）
- 广告类型：TopView、TopFeed、TikTok Pulse、Branded Mission、Sponsorship ads
- 指标：Premium reach cost、Premium reach impressions、Premium reach impression share（同垂类同市场曝光份额）、**Net Sentiment Rate**

### 阶段 2 · Awareness – Massive Reach（大规模曝光：驱动广泛认知）
- 广告类型：Reach & Frequency、Auction Reach
- 指标：Massive reach cost、Awareness audience（近 15 天有限次数/时长接触品牌广告或内容）、Awareness penetration（占同垂类同市场总 ACC 受众份额）

### 阶段 3 · Consideration（考虑：赢得喜爱与偏好）
- 指标：Consideration cost、Consideration audience（近 15 天有观看/互动/搜索/点击等具体行为）、**Awareness→Consideration transition rate**（15 天内）、Ad engagements（完播/分享/评论/点赞/点击/6 秒观看）

### 阶段 4 · Conversion（转化：带来行动与结果）
- 指标：Conversion cost、Conversion audience（规模与排名，基准 = 同垂类同市场转化受众规模最高前 5 品牌均值）、**Consideration→Conversion transition rate**（30 天内）

### 每阶段固定输出四块
1. **表现现状**：用给定数值客观描述。
2. **同比与基准对比**：量化高于/低于基准的幅度（% 或绝对值）+ 同垂类排名（注明分母品牌数）。
3. **差距与归因**：识别 performance gap，按五维归因——投放结构（产品组合是否匹配该阶段目标）/ 预算分配（本阶段成本占比、单位受众成本、单位 engagement 成本）/ 受众流转效率（规模与上一阶段转化率是否健康、漏损点在哪）/ 内容情感质量（Net Sentiment、Ad engagements 暴露的创意问题）/ 竞争份额（impression share、penetration、排名反映的 SOV 与竞争位置）。
4. **增长机会与建议**：2–3 条具体可量化动作，明确**预期影响的下游指标及大致量级**。

### 跨漏斗战略层（四阶段之后单独输出）
- **漏损诊断**：最大流失发生在 Awareness→Consideration 还是 Consideration→Conversion，量化健康度。
- **成本套利**：对比各阶段单位成本与产出，指出预算从哪一阶段挪出、向哪一阶段加注（给比例区间）。
- **竞争位势**：综合 impression share / penetration / 排名，判断领先/追赶/落后，给攻防策略。
- **媒体节奏（联动 Tentpole）**：结合流量高峰/大促节点，建议优质曝光与转化预算的排期与产品组合。

### ⚠️ TTMS 口径约束
- 受众类指标**仅**统计选定市场、垂类且**相同 ACC 模型**的品牌；其他指标统计同市场同垂类下**全部 ACC 模型**的品牌——**对比排名时分母品牌数不同，不要混用**。
- 区分本模块 **Ad engagements**（仅广告侧）与 Brand Perception 模块的 **Engagements**；区分 **Awareness penetration** 与 Audience Penetration 模块的 **ACC Penetration**。

---

## 三、mode=cads · C-ads 四维基操诊断

### 核心原则
C-ads 重种草 / Consideration 人群积累，**不是即时转化工具**。
**不要只用 GMV / ROAS 判断成败**，核心看 **CPCo 趋势** 与 **Co 人群规模增长**；确认这两项后才把 GMV / ROAS 当辅助参考。

### 1. 预算规模
- 单个 Ad Group 预算是否超过 **$85K 临界点**？（超过需拆分）
- 是否低于 **$100** 导致数据无参考性？
- 是否偏低、有提升空间？

### 2. 定向
- 是否过窄？（L3/L4 兴趣、自定义人群、叠加过多条件）→ 会推高 CPCo、限制漏斗
- 评估是否需要放宽。

### 3. 预算与排期
- 是否使用 **Lifetime Budget**？
- 投放时长是否够长？（**1→7 天约 −6%、1→14 天约 −8%** CPCo）
- 是否误用 **dayparting**？（会抬高 CPCo）
- 是否在做 **Always On** 持续积累？

### 4. 创意数量
- 每个 Ad Group 创意数是否落在 **6–10 条**高效区间？
- 参考：**1→5 条 CPCo 降约 $0.04**；超过 10 条边际效益不明显。

### 大促场景追加检查
- 是否提前 **≥7 天蓄水**？品牌预算占 TTL 是否 **>15%**？
- 三阶段节奏：**预热 T-15** 低成本种草 ≈20% 预算 → **蓄水 T-7** 扩量 ≈50% → **爆发 Peak Day** 种收一体 ≈30%
- 达人结构：头腰 / 腰尾占比是否合理？
- 素材加热门槛：发布前 3 日 **VV > 1000**、**6s VTR > 34%** 或 **互动率 ≥ 3%**
- 越南活动日历：**Double Day**（6.6 / 7.7 / 8.8…）、**Middle Day**（14–15 号）、**Payday**（25–26 号）

### 效果验证（不单看 GMV）
- CPCo 趋势（是否随时长/创意/定向调整而下降）
- Co 人群规模增长
- 八大人群从 Consideration 向转化层的流转率
- 新客贡献占比
- **CADS 必须投带小黄车的素材**（否则种草人群无法回收）

---

## 四、输出格式

**mode=ttms 或 both：**
1. **整体结论（漏斗健康度总览）**：哪一层是瓶颈、最大漏损跃迁、最大机会点、本期一句话战略主张。
2. **四阶段分节详述**（每节四块）。
3. **跨漏斗战略层**（漏损 / 套利 / 位势 / 节奏）。
4. **汇总表**：`指标 | 本期 | 同比 | vs 基准 | 排名 | 优先级建议`。
5. **Top 3 行动项**：每条标【动作 → 预期影响指标 → 影响量级 → 时间窗】。

**mode=cads：**
1. **现状诊断** — 基础信息 + 四维度（+ 大促维度）的事实判断
2. **问题定位** — 导致 CPCo 偏高 / Co 增长受限的具体原因
3. **优化建议** — 可执行清单（改什么、改成多少、预期影响）

**mode=both 追加一节「TTMS 瓶颈层 → C-ads 落地动作」的对应表**，把宏观结论逐条落到具体 Ad Group / 定向 / 排期改动上。

每条建议尽量绑定一个可量化目标或方向（如「定向放宽预计 CPCo 下降」），便于下期复盘验证。

---

## 五、通用约束

- 所有再分配比例、套利建议、节奏建议均为**方向性参考**，需结合实际预算约束与平台审核执行。
- 所有诊断结论标注为「基于数据的参考洞察」，不作绝对结论。
- 关键输入缺失时，先列待补充数据，再给有保留的判断。
- 币种：**品广消耗一律保留原币 USD 不折算**（与 `kans-vn-weekly-flow` 概览表第 12 行口径一致）。
- 措辞：环比配色 **红↑ / 绿↓**；避免使用"坏 / 崩盘 / 崩塌 / 垃圾流量"，改用"差 / 下降 / 低质流量"。

## 关联技能
- **kans-vn-weekly-flow** —— 直播间场内复盘（GMV-MAX / CLP / product_list）。本技能的结论在其 Step 10 被引用；反向地，当 Search 三项齐跌需要对品广消耗时，从这里取数。
- **kans-ttms-cads-report-batch** —— 在 TTMS 后台批量创建种草广告结案报告（执行类，非分析类）。
