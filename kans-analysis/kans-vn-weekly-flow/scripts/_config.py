# -*- coding: utf-8 -*-
"""每期只改这一个文件。其余脚本从这里读窗口 / 汇率 / 路径 / 品牌标签 / 班次。

🔴 下面所有值都是【示例】，换成你自己的。占位符含义与 SKILL.md「参数」一节一一对应。
"""
import os

# ============ 品牌 / 市场（示例数据：换成你自己的） ============
BRAND        = '你的品牌'                 # {{品牌}}          例：KANS
MARKET       = '越南'                     # {{市场}}          例：越南
ROOM         = '直播间'                   # {{直播间}}        例：SKINCARE 直播间
SHOP_NAME    = 'Your Shop'                # {{店铺名}}        例：Kans Official Vietnam（榜单 / 竞品表里找自己用）
FILE_PREFIX  = 'YourBrand_VN'             # {{文件前缀}}      产出文件名前缀，例：KANS_VN
TITLE_PREFIX = f'{BRAND} {MARKET} {ROOM}'  # 图表主标题前缀

# 直播 GMV-MAX 计划（与商品卡是两套投放，不可相加）
LIVE_CAMPAIGN_ID = '1000000000000001'      # {{直播计划ID}}   示例数据：换成你自己的导出

# 数据源标签（只用于图表页脚 / 表底口径行）
HOST_SHEET_LABEL   = '{{主播表}}（例：REPORT PERFORMANCE › Tháng 0X | SKINCARE）'
MARKET_SOURCE_NAME = 'Kalodata'            # {{大盘数据源}}   例：Kalodata / TTMS
MARKET_CATEGORY    = '美妆个护'            # {{类目}}         例：美妆个护 / Beauty & Personal Care
MARKET_REGION      = 'VN'                  # {{shop_region}}  例：VN / TH / ID

# ============ 每期必改 ============
PERIOD      = '1月W2'                        # 期次，文件名用
W1          = ('2026-01-05', '2026-01-11')   # 上期（周一→周日）
W2          = ('2026-01-12', '2026-01-18')   # 本期
W1L         = 'W1 01/05–01/11'
W2L         = 'W2 01/12–01/18'
VND         = 3890.0                     # {{汇率}}      1 RMB = ? 本币（越南例 3890 VND）
USD         = 6.75                       # {{USD汇率}}   1 USD = ? RMB
BREAKEVEN   = 4.1                        # {{盈亏线}}    退款后 ROI 盈亏线（按你自己的佣金/退款/人力反算）
FEE_FACTOR  = 1.04                       # {{平台服务费系数}} 广告消耗乘数（例 VXP 1.04；没有就填 1.0）
LOCAL_CCY   = 'VND'                      # 本币代码，例 VND / THB / IDR
CURRENCY_NOTE = f'1 RMB = {VND:,.0f} {LOCAL_CCY}'   # 页脚口径行用

# ============ 班次（必须覆盖 24h；跨夜段 00:00–05:59 记作 24–30h 归前一直播日） ============
# {{班次}}  例：6 班次 06-10 / 10-14 / 14-18 / 18-22 / 22-02 / 02-06
SHIFTS = [('早班 06-10', 6, 10), ('午班 10-14', 10, 14), ('下午 14-18', 14, 18),
          ('晚班 18-22', 18, 22), ('夜班 22-02', 22, 26), ('凌晨 02-06', 26, 30)]
SHIFT_ORDER = [s[0] for s in SHIFTS]

# ============ 路径 ============
_HERE = os.path.dirname(os.path.abspath(__file__))
# 产出目录（同时放中间 csv）：环境变量 WEEKLY_OUT 优先，否则脚本旁的 out/
OUT = os.environ.get('WEEKLY_OUT', os.path.join(_HERE, 'out'))
os.makedirs(OUT, exist_ok=True)


def _find_skill_chart():
    """kans-livestream-charts/scripts（common.py 所在）。环境变量 SKILL_CHART 优先，其余按常见位置探测。"""
    cands = [os.environ.get('SKILL_CHART', ''),
             os.path.join(_HERE, '..', '..', 'kans-livestream-charts', 'scripts'),      # 本仓库布局
             os.path.expanduser('~/.claude/skills/kans-livestream-charts/scripts'),
             os.path.expanduser('~/.claude/skills/synced/kans-livestream-charts/scripts')]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, 'common.py')):
            return os.path.abspath(c)
    return cands[1]


SKILL_CHART = _find_skill_chart()

# ============ 中间数据文件（由 prep 步骤生成，列名固定） ============
# daily_base.csv    : date, net_cost_rmb, gmv_rmb                （14 天，W1+W2）
# market_daily.csv  : date, total_yi, live_yi, video_yi, other_yi （14 天，亿本币）
# host_raw.txt      : day,start,end,dur,host,gmv_vnd,spend_vnd,views,clicks,ctor（无表头）
# 想先空跑一遍全链路：python3 make_sample_inputs.py 会往 OUT 写一套示例中间文件
