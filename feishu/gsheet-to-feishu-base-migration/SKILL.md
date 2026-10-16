---
name: gsheet-to-feishu-base-migration
description: 把 Google 表格（达人合作表、报价表、推进表、投放表等）迁移到飞书多维表格（Base）的通用流程，含首次灌数、增量补迁、字段回填和回滚。沉淀自 KANS 越南 KOL/KOC 两次迁移踩过的坑。当用户说「迁移 Google 表到飞书 / 把谷歌表搬进多维表格 / 灌历史数据 / 补迁增量 / 新表上线前导数据」，或提到某个品牌（如一叶子、韩束）的达人表要迁到飞书 Base 时使用。也适用于飞书旧表→新 Base 的结构迁移。
---

# Google 表 → 飞书多维表格迁移

核心原则：**迁移不是搬表，是按新表的字段口径重建数据**。每一步都留台账，每一次写入都能回滚。

工具都在 `scripts/`（下面用 `$S` 代指 `~/.claude/skills/gsheet-to-feishu-base-migration/scripts`）：

| 脚本 | 用途 |
|---|---|
| `fbase.js` | 飞书 Base 读写：resolve / schema / dump / workflows / apply（停规则→写→恢复）/ rollback / persons / people |
| `gsheet_xlsx_to_json.py` | Google 导出的 xlsx → 每 sheet 一个 JSON（原始值）+ CSV 原样备份 |
| `transform_template.py` | 清洗/去重/增量比对/出 diff.json + 台账 xlsx 的模板（复制到项目目录再改） |

凭据：`~/.feishu/credentials.json`（公司 My Claude 应用）。读不到某个 Base → 让用户在 Base 右上角「分享」里把 `My Claude` 加成可管理/可编辑。

**项目目录**：每个项目在 `./gsheet-migrations/<品牌>_<日期>/` 下单独建，脚本、源 JSON、dump、diff、applied 记录都放这里。**别只放 scratchpad**（会被系统清理，回滚记录丢了就回不去）。

---

## 流程（按顺序，不跳步）

### 0. 开工前问清楚（一次问完，用 AskUserQuestion）
- 目标 Base 链接（wiki 链接要先 `node $S/fbase.js resolve <token>` 换 app_token）
- 源 Google 表链接 + **具体迁哪几个 sheet**（用户口头说的「汇总表」可能对应多个 sheet，列出来让用户勾）
- 首次灌空表 还是 增量补迁（表已上线、同事在用？）
- 产品/选项映射、人员映射里拿不准的（见第 3 步），**不要自己猜**

### 1. 摸清目标表
```bash
cd <项目目录>
node $S/fbase.js schema <app>          # 全部表、字段名、类型、单选选项 → schema_<app>.json
node $S/fbase.js workflows <app>       # 自动化规则清单 + 状态备份
node $S/fbase.js dump <app> <tbl>      # 已有数据快照（增量迁移必做，每次写前都重拉）
```
看清：哪些是公式/查找引用（不写）、哪些单选（只能填已有选项）、哪些人员字段、规则之间怎么串（谁触发谁建行/回写）。

### 2. 取源数据
- **只用 xlsx 导出**（原始值）。在用户已登录 Google 的 Chrome 里打开 `https://docs.google.com/spreadsheets/d/<ID>/export?format=xlsx` 下载。
- **不要用 gviz/CSV 接口**：给的是显示值（8% vs 0.08），还会静默截断（实测 1031 行只返回 133 行）。前后两次比对必须用同一种导出方式，否则几千行假变更。
- `python3 $S/gsheet_xlsx_to_json.py 源.xlsx sheets/` → 看每个 sheet 行数和表头，和用户确认范围。

### 3. 定映射口径（写进台账「映射口径」页，用户确认后再写）
- **产品**：源写法 → 飞书单选选项原文。映射不上的行 → 丢弃进台账，**不要自己加选项**。
- **人员**：源里的英文名/昵称 → open_id。
  - 已在 Base 里出现过的人：`node $S/fbase.js people <app>` 直接拿 open_id↔姓名
  - 新人：让用户把 ta 加成 Base 协作者 → 拿 open_id → `fbase.js persons <app> <tbl> <人员字段> ou_xxx` 回读姓名核对
  - 通讯录查无此人 / 已离职 → **留空**，原名写进备注字段 `原表BD: xxx`；要不要过渡给别人由用户定
  - 注意同名不同人（同一品牌可能有两个同名 BD）
- **唯一键**：TikTok @handle 归一化（去@、小写、从主页链接里抽），**不用姓名**。有视频的数据用 Video ID 最安全。
- **去重键**：有报价 = 达人+报价+产品+BD；无报价(KOC) = 达人+产品；按视频建行 = Video ID。

### 4. 清洗 → diff.json + 台账
复制 `transform_template.py` 到项目目录，改 ★ 处。模板已带的规则：
- 公式列/查找引用/系统字段不写；单选只收已有选项；人员匹配不上留空
- 费用去货币符号/杂字符转纯数字（支持 1.2K、越南写法 1.000.000）；非数字原值**不丢**，追加进备注 `【字段名】原值`
- 百分比里逗号当小数点（8,5%）要修
- 日期统一转毫秒时间戳；dd/mm 字符串被 Google 误转成 mm/dd 的要按月份线索纠正
- 达人量级按粉丝数重算，不信旧标签（KANS 实测 29% 对不上）
- 无产品行、达人ID 为空的空壳行丢弃
- 缺发布日：TikTok 视频ID>>32 = 发布时间戳（UTC+7）兜底

产出 `迁移台账.xlsx`（待写入 / 丢弃行 / 合并去重 / 选项未匹配 / 映射口径）——**先给用户看台账和统计，点头了再写**。

### 5. 写入（停规则 → 写 → 恢复）
```bash
node $S/fbase.js apply <app> diff.json --test                        # 每表写 1 行、回读、删掉：核对字段格式
node $S/fbase.js apply <app> diff.json                               # 正式写
node $S/fbase.js apply <app> diff.json --keep "审核-推进-自动新增"     # 需要某条规则在写入时继续跑
```
- apply 会先备份规则状态 → 停掉所有启用规则（除 --keep）→ delete/update/create → finally 恢复并复核
- **为什么必须停规则**：提醒类规则会给同事刷几百条消息；回写/联动规则会把数据写到错的行上
- 产出 `applied_<tbl>_<时间>.json`，记着每条 created/updated record_id
- 写完 `count` 核对行数 = 预期

### 6. 写后核对 + 交接
- 重新 dump，按产品/人员/状态出分布，和台账对数
- 抽 5–10 行在飞书界面肉眼看（人员显示、日期、链接、单选）
- 多表串联的（审核→推进→投放），核对子表该自动建的行是否建了（规则停着写进去的不会触发，要么补迁子表要么让规则回放）
- 在 Base 里建/更新「📋 更新日志 & 交接说明」表，写清：来源、口径、行数、未决问题
- 更新 memory（项目 token、口径、遗留问题）

### 回滚
```bash
node $S/fbase.js rollback <app> <tbl> applied_<tbl>_<时间>.json   # 删掉本次新建的行
```
update 不能自动回滚 → 要靠写入前的 dump 还原。所以**每次写前都 dump**。

---

## 必读：踩过的坑
写入前过一遍 `references/pitfalls.md`（改单选选项清空整列、规则匹配键串行、规则回路刷空行、字段被改名……）。
KANS 的完整口径作为参照样例在 `references/kans-precedent.md`——**口径是参照，不是照抄**，新品牌的产品线、人员、表结构都要重新确认。
