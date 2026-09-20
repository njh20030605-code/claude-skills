# -*- coding: utf-8 -*-
"""每期只改这一个文件。其余脚本从这里读窗口 / 汇率 / 路径。"""
# ============ 每期必改 ============
PERIOD      = '8月W3'                    # 文件名用
W1          = ('2026-08-10', '2026-08-16')   # 上期（周一→周日）
W2          = ('2026-08-17', '2026-08-23')   # 本期
W1L         = 'W1 08/10–08/16'
W2L         = 'W2 08/17–08/23'
VND         = 3890.0                     # 1 RMB = ? VND
USD         = 6.75                       # 1 USD = ? RMB
BREAKEVEN   = 4.1                        # 退款后盈亏线
OUT         = '/home/claude/w/out'        # 产出目录（同时放中间 csv）
SKILL_CHART = '/root/.claude/skills/synced/kans-livestream-charts/scripts'  # common.py 所在

# ============ 中间数据文件（由 prep 步骤生成，列名固定） ============
# daily_base.csv    : date, net_cost_rmb, gmv_rmb                （14 天，W1+W2）
# market_daily.csv  : date, total_yi, live_yi, video_yi, other_yi （14 天，亿VND）
# host_raw.txt      : day,start,end,dur,host,gmv_vnd,spend_vnd,views,clicks,ctor
