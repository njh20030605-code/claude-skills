# -*- coding: utf-8 -*-
"""主播 / 时段拆分：从 host_raw.txt 生成 period.csv / period_ex88.csv / period_host.csv / host_pk.csv

host_raw.txt 列（无表头，逗号分隔）：
    day,start,end,dur,host,gmv_vnd,spend_vnd,views,clicks,ctor
  · day  = 日（两位，如 03/16），脚本按 >=W2 起始日 判本期/上期
  · dur  = 该段时长（小时），**以 Duration 列为准**，不要用 起止时间 反推（表里常不一致）
  · gmv/spend 取 GMV Host / Spend Ads Host 原生列（VND，越南数字格式已在抓取时清洗）

抓取来源：Google Sheet「2026 REPORT PERFORMANCE | KANS」› Tháng 0X | SKINCARE
  🔴 Drive MCP 的 read_file_content 会把每个 sheet 截断到 ~87 行，**拿不到整月**。
     用 Claude in Chrome 打开 gviz 接口读全量（同源，CSP 不拦）：
       https://docs.google.com/spreadsheets/d/<ID>/gviz/tq?tqx=out:html&gid=<GID>
     再用 javascript_tool 取 document.querySelectorAll(\'table tr\')，分片输出（单次约 1300 字符上限）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import W2, VND, OUT
import pandas as pd, numpy as np

CUT = int(W2[0][-2:])          # 本期起始日
BINS = [('早班 06-10',6,10),('午班 10-14',10,14),('下午 14-18',14,18),
        ('晚班 18-22',18,22),('夜班 22-02',22,26),('凌晨 02-06',26,30)]
ORDER = [b[0] for b in BINS]
PROMO_DAY = None               # 若上期含大促日，填日号（如 8）→ 生成剔除大促的日均可比表

d = pd.read_csv(f'{OUT}/host_raw.txt', header=None,
                names=['day','st','et','dur','host','gmv','spend','views','clicks','ctor'])
d['gmv'] = d.gmv / VND
d['spend'] = d.spend / VND

def sh(t):
    h, m = str(t).split(':')
    v = int(h) + int(m) / 60
    return v + 24 if v < 6 else v          # 00:00–05:59 跨夜尾段归前一直播日

d['s'] = d.st.map(sh)
d['e'] = d.s + d.dur

rows = []
for _, r in d.iterrows():
    for name, a, b in BINS:                # 跨班次段按小时重叠拆分
        ov = max(0, min(r.e, b) - max(r.s, a))
        if ov > 0:
            f = ov / r.dur
            rows.append(dict(period=name, day=r.day, host=r.host, h=ov,
                             gmv=r.gmv * f, spend=r.spend * f,
                             views=r.views * f, clicks=r.clicks * f))
sp = pd.DataFrame(rows)
sp['wk'] = np.where(sp.day >= CUT, '本期', '上期')

def agg(x):
    return pd.Series(dict(GMV万=x.gmv.sum()/1e4, 消耗万=x.spend.sum()/1e4, 时长=x.h.sum(),
                          ROI=x.gmv.sum()/x.spend.sum() if x.spend.sum() else np.nan,
                          单h=x.gmv.sum()/x.h.sum() if x.h.sum() else np.nan,
                          UV=x.gmv.sum()/x.views.sum() if x.views.sum() else np.nan))

P = sp.groupby(['period','wk']).apply(agg, include_groups=False).unstack('wk')
res = pd.DataFrame(index=ORDER)
for m in ['GMV万','消耗万','时长','ROI','单h','UV']:
    for w in ['上期','本期']:
        res[f'{w}·{m}'] = P[(m, w)] if (m, w) in P.columns else np.nan
res['GMV环比'] = res['本期·GMV万']/res['上期·GMV万'] - 1
res['ROI变化'] = res['本期·ROI'] - res['上期·ROI']
res['单h环比'] = res['本期·单h']/res['上期·单h'] - 1
res['UV环比']  = res['本期·UV']/res['上期·UV'] - 1
res.to_csv(f'{OUT}/period.csv')

cu = sp[sp.wk == '本期']
ph = cu.groupby(['period','host']).apply(agg, include_groups=False).reset_index()
ph = ph[ph.时长 >= 0.5]
ph['period'] = pd.Categorical(ph.period, ORDER, ordered=True)
ph.sort_values(['period','GMV万'], ascending=[True, False]).to_csv(f'{OUT}/period_host.csv', index=False)

def agg2(x):
    return pd.Series(dict(场次=len(x), 时长=x.dur.sum(), GMV万=x.gmv.sum()/1e4,
                          消耗万=x.spend.sum()/1e4, ROI=x.gmv.sum()/x.spend.sum(),
                          单h=x.gmv.sum()/x.dur.sum(), UV=x.gmv.sum()/x.views.sum()))
d.groupby([np.where(d.day >= CUT, '本期', '上期'), 'host']).apply(agg2, include_groups=False)\
 .to_csv(f'{OUT}/host_pk.csv')

# 🔴 上期含大促时必做：剔除大促日的「日均」可比表，否则所有环比都是基数效应
if PROMO_DAY:
    sp2 = sp[~((sp.wk == '上期') & (sp.day == PROMO_DAY))]
    nd_prev = sp2[sp2.wk == '上期'].day.nunique()
    nd_cur  = sp2[sp2.wk == '本期'].day.nunique()
    P2 = sp2.groupby(['period','wk']).apply(agg, include_groups=False).unstack('wk')
    r2 = pd.DataFrame(index=ORDER)
    for m in ['GMV万','ROI','单h','UV','时长']:
        for w in ['上期','本期']:
            r2[f'{w}·{m}'] = P2[(m, w)] if (m, w) in P2.columns else np.nan
    r2['上期·日均GMV万'] = r2['上期·GMV万'] / nd_prev
    r2['本期·日均GMV万'] = r2['本期·GMV万'] / nd_cur
    r2['日均GMV环比'] = r2['本期·日均GMV万']/r2['上期·日均GMV万'] - 1
    r2['ROI变化'] = r2['本期·ROI'] - r2['上期·ROI']
    r2['单h环比'] = r2['本期·单h']/r2['上期·单h'] - 1
    r2['UV环比']  = r2['本期·UV']/r2['上期·UV'] - 1
    r2.to_csv(f'{OUT}/period_ex88.csv')

print('ok', len(sp), '段-班次组合；总量核对(元)：', round(d[d.day>=CUT].gmv.sum(),1))
