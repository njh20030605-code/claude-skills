# 示例数据

这两份是今天（2026-06）那批真实数据的快照，用来让脚本开箱即跑、也作为列名模板。
下次替换成你自己的导出即可——**列名保持一致**就行。

## kans_daily.csv
KANS 直播间日度。列：`date, spend_usd, gmv_usd`（USD）。
- 驱动 **图1**（GMV+ROI 周对比）
- 作为 **图2** 的 KANS 序列
- 也可以直接喂 KANS Campaign 原始 xlsx，脚本会自动解析（无需先转 CSV）

## market_daily.csv
大盘品类日度。列：`date, short_k, live_k, card_k`（千USD）。
- 驱动 **图3**（大盘堆叠趋势）
- 作为 **图2** 的大盘序列（**只用 live_k**）
- 也可以直接喂 TTMS Serums 原始 xlsx，脚本自动解析、自动跳过汇总行

## 快速自检
```
cd ../scripts
python3 1_gmv_roi_weekly.py        --input ../examples/kans_daily.csv  --start 06-08 --end 06-21 --out /tmp/c1.png
python3 2_livestream_correlation.py --kans ../examples/kans_daily.csv  --market ../examples/market_daily.csv --start 06-01 --end 06-20 --out /tmp/c2.png
python3 3_market_stacked_gmv.py     --input ../examples/market_daily.csv --out /tmp/c3.png
```
图2 应输出 `r_full=0.430  r_ex=0.070  spearman=0.387`，对上即正常。
