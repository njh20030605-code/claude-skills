# 参照样例：KANS 越南 KOL / KOC 迁移口径（2026-09）

> 新品牌迁移时拿来对照「要问哪些问题、口径写到多细」。具体映射值是 KANS 的，**不要直接套到别的品牌**。

## 表结构：三表串联
审核表（KOL Lists，报价/审核唯一入口）→ 推进表（Video Tracking，寄样→脚本→返稿→发布→投流码）→ 投放表（ADS TRACKING）

链路：审核表 `Progress=DONE完成` → 规则自动建推进行 → 推进表拿到投流码 → 规则自动建投放行 → 投放表改动回写推进表。

KOL base（12 条规则）/ KOC base（11 条规则），结构同源。
原始脚本：transform.py / load.js / apply_diff.js / ads_match.py（本 skill 的 `scripts/` 是它们的通用版）。

## 口径清单（每一条都是当时和用户确认过的）

| 维度 | KANS 口径 |
|---|---|
| 迁哪些 sheet | KOC-List-Tracker 只取 KOCList 子表；Posts Tracker 只取 Free KOC Posting Schedule；跨境 EMMA 表只取 Powder 行 |
| 产品映射 | white essence / whitening serum → Whitening Essence；suncreen/sunscreen → Whitening Suncreen；White Cream 无对应选项 → **不迁、不加选项** |
| 丢弃 | 无产品、达人ID 为空 |
| 去重键 | KOL = 达人+报价+产品+BD；KOC（无报价）= 达人+产品；推进表同达人同产品多条已发布视频 → 按视频各一行 |
| 跨快照压制 | Google 无报价而飞书已有更全记录→不登记；同价同产品仅 BD 不同→不登记（BD 以飞书为准）；飞书报价空而 Google 有→补价不新增 |
| 状态映射 | Already Posted/Draft Done/Draft in Progress/Delay → DONE完成；Unresponsive/备注 no reply → No Reply未回复；Cancel/reject/Confirm=NO → Reject驳回；其余留空 |
| 推进表 Process | Already Posted→Released；Draft in Progress→Awaiting Demo；Draft Done→Demo Check；Delay→Pending |
| 推进表收什么 | 只收审核表 DONE 的达人 |
| BD 映射 | 英文名→飞书人员；几位离职 BD 的达人统一归到现任 BD-A；离职/查无此人的留空并备注「原表BD:」，KOC 时用户又定为过渡给该产品近 30 天众数 BD |
| 上级 LM | 按 BD 走（不是按产品）；跨境店行一律填跨境负责人 |
| 投放字段 | 从 Google 投放表按 Video ID 优先、(达人+产品) 兜底匹配；Ads planner 全填当时的投放负责人 |
| 量级 | 按粉丝数重算：<1万 Nano / 1-10万 Micro / 10-50万 Macro / 50-100万 BIG / >100万 Mega |
| Niche | 对不上选项留空 |
| Seller | Google 来源 = 本土店；EMMA = 跨境店 |
| 数字 | 费用转纯数值；百分比/金额对齐飞书现有写法 |
| 日期缺失 | 发布日缺失用视频ID>>32（UTC+7，抽样 89% 差 ≤1 天） |

## 迁移后遗留的结构性问题（新品牌上线前可以提前规避）
1. BD 绕过审核表直接在推进表建行 → 两表脱钩（326 组），历史合作费/是否合作过查不到
2. 推进表触发条件是 DONE → 推进表实际是"已完成表"，制作中的达人进不去
3. 规则回路刷空行（见 pitfalls 第 3 条）
4. 子表（投放表）因写入时规则停着没自动建行，0 行
