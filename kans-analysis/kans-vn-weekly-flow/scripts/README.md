# 周报图表脚本使用顺序

```
1) 改 _config.py 的 PERIOD / W1 / W2 / VND / USD
2) 准备中间数据（列名见 _config.py 底部注释）
     out/daily_base.csv    ← GMV-MAX campaign 导出按日聚合
     out/market_daily.csv  ← Kalodata history 接口
     host_raw.txt          ← REPORT PERFORMANCE Google Sheet（gviz 抓法见 SKILL.md）
3) python std_charts.py      → 图1 每日GMV+ROI / 图2 趋势共振PanelA / 图3 大盘分渠道
4) python host_periods.py    → period.csv / period_ex88.csv / period_host.csv / host_pk.csv
5) python step12_charts.py       → Step12 主播排名.png + Step12 时段数据.png（含环比）
5b) python host_period_chart.py  → Step12 主播×时段对比.png（只本期，排班决策用）
6) python seg5_chart.py      → Step9 5段核心指标条形图.png（🔴 周报/月报都必做；A/B 两个 dict + 顶部「一句话」每期手改，见文件头）
7) python uv_breakdown.py    → 往 Step9_流量结构.xlsx 追加「④ UV价值 分维度」sheet（每期必做）
8) python kol_koc.py         → 两期 affiliate_orders + 付费达人清单 → 按商品ID 出 KOL/KOC 占比
9) python gmvmax_card.py     → GMV-MAX 商品卡两期对比 xlsx（把 8 的结果填进 R 表；固定 15 列）
```

所有图统一：中文字体 Noto Sans CJK、红=↑ 绿=↓、W1/W2 分区底色 + 中间虚线、页脚口径行。
**图上不要用 emoji**（缺字形）。
