---
name: kans-livestream-charts
description: 生成 KANS 越南直播运营周报/月报的三类标准图表。当用户提供直播间日度数据（KANS Campaign 导出）和/或大盘品类数据（TTMS Serums & Essences 导出），并要求做 (1) 每日 GMV+ROI 周对比柱线图、(2) KANS 直播 vs 大盘直播 GMV 相关性验证双面板图、(3) 品类大盘堆叠 GMV 趋势图 时使用。输入可以是干净 CSV，也可以是平台原始 xlsx（脚本自动解析）。
---

# KANS 越南直播运营 · 标准图表三件套

把日常复盘里反复要画的三张图固定成脚本。给数据 → 跑脚本 → 出 PNG。
配色、字体、口径三张图统一，可直接进周报/月报。

## 何时用
- 用户上传直播间或大盘的日度数据，要画下面任意一张或多张图。
- 关键词：周对比 / GMV ROI / 相关性 / 脱钩 / 大盘趋势 / 堆叠 / 复盘图。

## 通用约定（已写死在 `scripts/common.py`）
- **中文字体**：自动探测 Noto Sans CJK SC（找不到退化到文泉驿），无需手动设置。
- **ROI 口径**：`ROI = 总收入 / 成本`（毛口径，平台展示口径）。
- **汇率**：USD→RMB 默认 `6.8`（图1可用 `--rate` 改；`--no-rmb` 保持美元）。
- **大盘只用『直播』列**：相关性图严禁拿大盘总 GMV 对比 KANS 直播，必须用 `live_k`。
- 输出统一 PNG，`bbox_inches="tight"`，可直接贴。

## 输入数据契约
两张表，列名固定（CSV 直接用；xlsx 走自动解析器，按表头定位列，列序变了也能读）：

**KANS 日度** —— 驱动图1，并作为图2的 KANS 序列
| 列 | 含义 |
|---|---|
| `date` | `MM-DD`，如 `06-08` |
| `spend_usd` | 当日花费(USD) |
| `gmv_usd` | 当日直播 GMV / 总收入(USD) |

> 原始 xlsx：KANS 直播间 Campaign 导出（含 `启动时间/成本/总收入` 列）。解析器按日聚合、自动跳过无数据的排期占位行。

**大盘日度** —— 驱动图3，并作为图2的大盘序列
| 列 | 含义 |
|---|---|
| `date` | `MM-DD` |
| `short_k` | 短视频 GMV(千USD) |
| `live_k` | 直播 GMV(千USD) |
| `card_k` | 商品卡 GMV(千USD) |

> 原始 xlsx：TTMS · Serums & Essences 导出（含 `日期/短视频GMV/直播GMV/商品卡GMV`）。解析器自动跳过『区间最大值』汇总行。

示例数据见 `examples/kans_daily.csv`、`examples/market_daily.csv`（即今天 06 月这批）。

## 三张图怎么跑（在 `scripts/` 目录下）

### 图1 · 每日 GMV 与 ROI（周对比）
柱=每日 GMV(折RMB)，按周换色；线=ROI(右轴)；含退款后盈亏线 + 每周小结框 + 环比。
```
python 1_gmv_roi_weekly.py --input ../examples/kans_daily.csv \
    --start 06-08 --end 06-21 --out out1.png
```
常用参数：`--rate 6.8` 汇率 ｜ `--breakeven 4.1` 盈亏线 ｜ `--no-rmb` 保持USD ｜ `--title "..."`。
按周切分：从 `--start` 起每 7 天一周（自动画第1周/第2周…，≤3周时画小结框）。

### 图2 · KANS 直播 vs 大盘直播 · 相关性验证
左 Panel A 两条指数曲线看共振；右 Panel B 散点+回归+相关系数。
```
python 2_livestream_correlation.py --kans ../examples/kans_daily.csv \
    --market ../examples/market_daily.csv --start 06-01 --end 06-20 \
    --promo 06-05 06-06 06-18 --ramp 06-17 06-19 --out out2.png
```
参数：`--promo` 平台大促日(红星) ｜ `--ramp` KANS自播拉量日(绿三角，高亮脱钩) ｜
`--index-base window_mean|first_day`。
- **`window_mean`（默认）**：各自÷时段均值×100。适合单张图看共振。
- **`first_day`**：各自÷首日×100。**要跨不同时间窗口叠看老图时用这个**（见下方备注）。

### 图3 · 品类大盘 GMV 趋势（堆叠）
堆叠柱(直播/短视频/商品卡)+总GMV线+大促事件标注。
```
python 3_market_stacked_gmv.py --input ../examples/market_daily.csv --out out3.png
```
事件标注（6.6爆发/6.7急跌/6.18二次高峰/日常基本盘）在脚本顶部 `EVENTS` 列表里，
文案用 `{peak}/{total}/{live_share}/{dod}` 占位符自动填数；换月改这里即可。

## 方法论备注（别踩坑）
1. **相关系数对线性缩放完全免疫**：换分母、换币种(USD↔VND)都不改变 r。结论永远看 Panel B 的 r/回归，不看 Panel A 的线高。
2. **指数化(÷均值×100)只是视觉手段，不能跨窗口比绝对高度**：均值随时间段变，同一天在 13 日图和 20 日图里的指数会不同（原始值没变）。要让新图能和旧图直接叠，用 `--index-base first_day`。
3. **相关性崩塌≠数据错**：窗口拉长后 r 下降，是因为新增数据里出现脱钩（如 KANS 自播拉量大盘没跟），是真实结论。
4. **盈亏线**：图1 默认 4.1 = 退款后盈亏线（口径：平台抽佣+人力+仓储+物流+退款率综合）。

## 文件清单
```
kans-livestream-charts/
├── SKILL.md
├── scripts/
│   ├── common.py                  # 字体/配色/格式/数据读取与xlsx解析
│   ├── 1_gmv_roi_weekly.py        # 图1
│   ├── 2_livestream_correlation.py# 图2
│   └── 3_market_stacked_gmv.py    # 图3
└── examples/
    ├── kans_daily.csv             # KANS 日度示例(06-01~06-21)
    ├── market_daily.csv           # 大盘日度示例(06-01~06-20)
    └── README.md
```

依赖：`python3` + `matplotlib pandas numpy scipy openpyxl`（环境已具备）。
