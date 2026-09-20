---
name: tiktok-batch-budget-update
description: 在 TikTok 广告管理平台（ads.tiktok.com/i18n/manage/adgroup）用 Claude in Chrome 按「广告组ID → 新日预算」清单批量改预算。当用户粘贴一份 ID+数字的清单并说「调一下预算 / 按我发的改预算 / 批量改日预算 / 把新预算加进去 / 改总预算」时使用。核心：广告组ID是广告组名称的数字后缀；「修改预算」弹窗的输入框在嵌套 shadow DOM 里，必须用 native value setter + composed 事件写入；靠「已修改 N 个广告组」计数校验（要另起一次 JS 调用才读得到最新值）；提交前必须逐条列出对照表让用户确认。
---

# TikTok 广告组批量改预算

按用户给的「广告组ID  新预算」清单，在已打开的「修改预算」弹窗里批量写入新日预算/总预算。

## 前提

用户已经在 `ads.tiktok.com/i18n/manage/adgroup` 勾选了广告组并打开了「修改预算」弹窗。
如果弹窗没开：先截图确认列表页状态，让用户勾选并点开弹窗，不要自己去猜着勾选广告组。

用户清单的典型格式（制表符或空格分隔，无表头）：

```
7664548737817054485	60
7642356927774739733	20
```

左边是广告组ID，右边是新预算（单位就是弹窗里显示的币种，通常 USD）。

## 关键 DOM 事实（踩过的坑，别重新试）

1. **弹窗主体不在 `.vi-dialog` 里**。`.vi-dialog.bulk-adjust-dialog` 只有 header 和 footer；
   表格在独立节点 `.bulk-adjust-form-table`。对着 `[role="dialog"]` 查 `tr` 会返回 0 行。
2. **行**：`.bulk-adjust-form-table .vi-table__body-wrapper tbody tr`
   单元格顺序：`[0]` 广告组名称、`[1]` 总消耗、`[2]` 当前预算、`[3]` 新预算输入框。
3. **广告组ID = 名称的数字后缀**，正则 `/(\d{15,})\s*$/`。
   例：`0721-withmayanh-White Essence-BC-护肤人群-7664548737817054485`。
   表格里没有独立的 ID 列，只能这样取。
4. **输入框在两层 shadow DOM 里**：
   `[x-name="x-input-number"]` → shadowRoot → `x-input-*` → shadowRoot → `<input>`。
   直接 `row.querySelector('input')` 永远是 null。用 `references/set_budget.js` 里的 `deepInput()` 递归穿透。
5. **写值必须用 native setter + composed 事件**：
   ```js
   const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
   inp.focus(); setter.call(inp, '60');
   inp.dispatchEvent(new Event('input',{bubbles:true,composed:true}));
   inp.dispatchEvent(new Event('change',{bubbles:true,composed:true}));
   inp.blur();
   ```
   少了 `composed:true` 事件跨不出 shadow 边界，组件收不到。
6. **`已修改 N 个广告组` 计数在同一次 JS 调用里读是旧值**（Vue 还没重渲染）。
   必须**另起一次 `javascript_tool` 调用**去读，否则会误判成失败。

## 执行流程

1. **先只读一次**，把 15 行左右的 `[行号, 广告组ID, 当前预算]` 全部 dump 出来，不写任何值。
2. **在本地把清单和页面行对上**，分成三类：
   - 需要改的（当前值 ≠ 目标值）→ 写入
   - 已经等于目标值 → **留空跳过**，不要写重复值（留空 = 不改，写值会让"已修改"数虚高）
   - 弹窗里被勾选、但**不在用户清单里**的行 → 留空，并且**必须在回复里单独警告用户**
   - 用户清单里有、但弹窗里找不到的 ID → 也要单独报出来（可能没勾选，或落在「无法修改」tab）
3. **一次 JS 调用写完所有需要改的行**（`references/set_budget.js`），返回逐行日志。
4. **另起一次 JS 调用**回读所有 input 的 value + `已修改 N 个广告组` 计数，确认 N == 需要改的行数。
5. 截图确认弹窗状态。
6. **列出对照表（ID / 当前 / 新）让用户确认，然后才点「提交」。**
   提交是不可逆操作，永远不要自动点。

## Tab 说明

弹窗有三个 tab：`日预算`（默认）、`总预算`、`无法修改`。
用户没特别说就是**日预算**。要改总预算先切 tab 再重新 dump 行。
「无法修改」tab 里的广告组是平台不允许改的（预算类型不符、状态限制等），如果用户清单里的 ID 出现在这里，直接告诉用户改不了，别硬试。

## 输出格式

给用户的回复里包含：

- 需要改动的表格：`广告组ID | 当前 | 新预算`
- 已达标跳过的 ID 列表（一行带过即可）
- ⚠️ 异常项：勾选了但不在清单的、清单里但没找到的
- 最后一句：问是否点「提交」
