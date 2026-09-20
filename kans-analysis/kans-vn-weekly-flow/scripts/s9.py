# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, json, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from _config import PERIOD, VND, OUT
from style import hdr, title, widths, pct_color, note_block, YELLOW, GREY, BORDER, NOTEBLUE
M=json.load(open(f'{OUT}/metrics.json')); A,B=M['prev'],M['cur']
T=json.load(open(f'{OUT}/ts.json')); cur,prev,fp=T['cur'],T['prev'],T['freshprev']
wb=openpyxl.Workbook()

# ================= ① 5段流量结构 =================
ws=wb.active; ws.title='① 5段流量结构'; NC=5
title(ws,1,f'Step9 · 流量结构 5 段｜本期 08/17–08/23 vs 上期 08/10–08/16（CLP 总量口径）',NC)
ws.cell(row=2,column=1,value='总量只信 CLP（Creator-Live-Performance，35列）；入口拆分用 Creator-Live-Traffic-Source。GMV 已折 RMB（÷3890）。★ = 与 LIVE Manager 后台卡片同口径的指标。')
ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=NC)
ws.cell(row=2,column=1).font=Font(size=9,italic=True,color='555555')
for i,h in enumerate(['指标','上期 08/10–08/16','本期 08/17–08/23','环比','备注'],1): ws.cell(row=3,column=i,value=h)
hdr(ws,3,NC)
r=4
def sec(t):
    global r
    ws.cell(row=r,column=1,value=t); ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC)
    c=ws.cell(row=r,column=1); c.fill=PatternFill('solid',fgColor='D9E2F3'); c.font=Font(bold=True,size=10,color='1F3864')
    c.border=BORDER; r+=1
def row(name,pv,cv,fmt='#,##0',pp=False,note='',hl=False):
    global r
    ws.cell(row=r,column=1,value=name); ws.cell(row=r,column=2,value=pv); ws.cell(row=r,column=3,value=cv)
    v=(cv-pv) if pp else (cv/pv-1 if pv else None)
    ws.cell(row=r,column=4,value=v); ws.cell(row=r,column=5,value=note)
    for j in range(1,NC+1):
        c=ws.cell(row=r,column=j); c.border=BORDER; c.font=Font(size=10)
        c.alignment=Alignment(horizontal='left' if j in(1,5) else 'center',wrap_text=(j==5))
        if j in(2,3): c.number_format=fmt
        if j==4: c.number_format=('+0.0000;-0.0000' if pp and fmt!='0.00%' else ('+0.00%;-0.00%' if pp else '0.00%'))
        if hl: c.fill=PatternFill('solid',fgColor=YELLOW)
    pct_color(ws.cell(row=r,column=4),v); r+=1
sec('① 流量')
row('曝光 Impressions',A['impr'],B['impr'])
row('观看 Views',A['clp_views'],B['clp_views'])
row('★ 进房率 = Tap-through（观看÷曝光）',A['tap'],B['tap'],'0.00%',True,'＝后台「Tap-through rate」卡。🔴 上升是推荐位曝光收缩的机械结果，不是承接变好 —— 见 sheet ②',True)
row('场次',A['sess'],B['sess'],'#,##0',False,'上期 8/15 曾拆两场；本期未拆，判断用总时长')
row('直播时长(h)',A['dur'],B['dur'],'#,##0.00',False,'CLP Duration 汇总；主播报表 136.00h，差 +0.09%')
row('场均时长(h)',A['sess_avg_h'],B['sess_avg_h'],'#,##0.00',False,'上升由上期拆场造成，非真变长')
sec('② 转化漏斗')
row('商品曝光 Product Impressions',A['prod_impr'],B['prod_impr'],'#,##0',False,'🟢 唯一在涨的漏斗上游 +4.15%')
row('商品点击 Product clicks',A['prod_clicks'],B['prod_clicks'])
row('订单数 Attributed orders',A['orders'],B['orders'],'#,##0',False,'🟢 本期首次拿到上期+本期两份 CLP，上期不再靠 AOV 反推（上期值取 8月W2 发布口径）')
row('SKU订单数',A['sku_orders'],B['sku_orders'])
row('LIVE CTR（点击÷观看）',A['live_ctr'],B['live_ctr'],'0.00%',True,'CLP「LIVE CTR」列，后台无此卡')
row('★ CTR（点击÷商品曝光）',A['ctr'],B['ctr'],'0.00%',True,'🔴 ＝后台「CTR」卡。分母是商品曝光，不是观看。本期最实质的恶化项',True)
row('★ CTOR（订单÷点击）',A['ctor'],B['ctor'],'0.00%',True,'＝后台「CTOR」卡。总量基本持平，但拆到入口是两涨一跌，见 sheet ②')
row('CTOR-SKU（SKU单÷点击）',A['ctor_sku'],B['ctor_sku'],'0.00%',True,'CLP「CTOR (SKU orders)」列')
row('SKU order rate（SKU单÷观看）',A['sku_rate'],B['sku_rate'],'0.00%',True,'端到端转化')
row('AOV（GMV÷订单数）',A['aov'],B['aov'],'#,##0.00',False,'🔴 分母是 Attributed orders，不是 SKU orders（后者约差 2 倍）')
sec('③ 变现效率')
row('CLP 归因 GMV(元)',A['clp_gmv'],B['clp_gmv'],'#,##0.00')
row('每小时 GMV(元)',A['gmv_per_h'],B['gmv_per_h'],'#,##0.00')
row('Show GPM(元/千曝光)',A['show_gpm'],B['show_gpm'],'#,##0.00',False,'🟢 曝光收缩带来的机械改善')
row('Watch GPM(元/千观看)',A['watch_gpm'],B['watch_gpm'],'#,##0.00',False,'手算 GMV÷观看×1000')
row('UV 价值(元/观看)＝ WatchGPM÷1000',A['uv_clp'],B['uv_clp'],'0.0000',False,'🟢 几乎没动（−0.27%）：每个进来的人的价值稳住了',True)
sec('④ 互动效率')
row('新增粉丝',A['followers'],B['followers'])
row('★ Follow rate 关注率（新粉÷观看）',A['follow_rate'],B['follow_rate'],'0.00%',True,'＝后台「Follow rate」卡')
row('点赞数',A['likes'],B['likes'])
row('点赞率（点赞÷观看）',A['like_rate'],B['like_rate'],'0.00%',True,'🔴 −13.76pp，跌幅远超观看 −6.18%，是内容/互动引导问题不是量的问题')
row('评论数',A['comments'],B['comments'])
row('评论率（评论÷观看）',A['comment_rate'],B['comment_rate'],'0.00%',True,'与观看同幅，属量缩自然结果')
row('分享数',A['shares'],B['shares'],'#,##0',False,'🔴 上期待办 f 未执行：267 → 186（−30.3%）。历史单日峰值 1,026')
row('分享率（分享÷观看）',A['share_rate'],B['share_rate'],'0.00%',True,'0.225% → 0.167%，零成本增量动作继续退')
sec('⑤ 入口结构（明细见 sheet ②）')
for k in ['Search','推荐','其他']:
    row(f'{k} · 观看占比',prev[k]['view_share'],cur[k]['view_share'],'0.00%',True)
    row(f'{k} · 成交占比',prev[k]['gmv_share'],cur[k]['gmv_share'],'0.00%',True)
r+=1
notes=[
 '🔴🔴【判断范式 —— 本期进房率是个陷阱，别拿它当承接指标】曝光 −10.18%、观看 −6.18% → 进房率 2.92% → 3.05%（+0.13pp）看着在变好。但拆到入口：推荐位曝光从 267.7 万掉到 208.5 万（−22.1%），而推荐是全场最低进房位（1.75%→2.14%）。低进房位曝光大幅收缩 → 整体进房率被机械抬高，与承接能力无关。',
 '🔴 真实承接指标全线下滑：★CTR（点击÷商品曝光）3.23% → 2.81%（−0.42pp）；三入口 CTOR 两跌一涨 —— Search 5.14%→4.46%（−0.68pp）、推荐 4.91%→3.90%（−1.01pp）、其他 5.60%→6.53%（+0.93pp）。商品曝光 +4.15% 的同时点击 −9.48%，等于「货架露出更多、点的人更少」。',
 '🟡 与上期正好相反，形成一组对照：上期是「进房率跌 + CTOR 全涨 = 结构性稀释，承接没变差」；本期是「进房率涨 + CTOR 多数跌 = 结构性收缩，承接确实变差」。**进房率连续两周给出与真实承接相反的信号 —— 建议从本期起把它降级为观察项，考核用 ★CTR + 各入口 CTOR + UV 价值三件套。**',
 '🟢 UV 价值 / Watch GPM 几乎没动（1.6979 → 1.6933，−0.27%）：单个观众的变现价值稳住了，GMV 的下滑基本等于观看的下滑。这说明问题在「进店人数与点击意愿」，不在「成交效率」。',
 '🔴 互动里点赞率是唯一超跌项：点赞 −29.9%、点赞率 54.43% → 40.67%（−13.76pp），而观看只 −6.18%、评论率基本持平。这不是量缩的自然结果，是互动引导动作退了。分享 267 → 186（−30.3%），上期待办 f「分享激励重新上」未执行。',
 '【口径 PS】① 总量一律用 CLP，入口表只做结构拆分，不作总量来源。② CTOR 分母是商品点击，不是观看。③ 环比配色全套统一 红=↑ 绿=↓（含 sheet ②），颜色只表方向不表好坏。',
]
r=note_block(ws,r,notes,NC)
widths(ws,[38,20,20,14,95]); ws.freeze_panes='A4'

# ================= ② 三入口精度对比 =================
ws2=wb.create_sheet('② 三入口精度对比'); NC2=6
title(ws2,1,'Step9 · 三入口精度对比（纵列版）｜本期 08/17–08/23 vs 上期 08/10–08/16',NC2)
ws2.cell(row=2,column=1,value='分组：推荐 = For You feed + LIVE feed｜其他 = Shop tab + Inbox + Other channels + Following｜CTOR 点击加权（点击 ≈ 观看 × CTR）。配色与全套报告统一：红 = ↑ / 绿 = ↓（中国财务口径，不代表好坏）。')
ws2.merge_cells(start_row=2,start_column=1,end_row=2,end_column=NC2)
ws2.cell(row=2,column=1).font=Font(size=9,italic=True,color='555555')
for i,h in enumerate(['入口','指标','上期 08/10–08/16','本期 08/17–08/23','环比','备注'],1): ws2.cell(row=3,column=i,value=h)
hdr(ws2,3,NC2)
NOTE={'Search':'进房入口王但 UV 最低；观看/进房率/CTOR 三项齐跌 → 必须去对品广消耗',
      '推荐':'付费主战场；曝光 −22.1% 是本期总曝光下滑的主因，CTOR 跌幅最大 −1.01pp',
      '其他':'🟢 唯一三项全涨的入口：观看 +3.6%、成交 +3.6%、CTOR +0.93pp，UV 4.03 是 Search 的 5.3 倍',
      '合计':'与 CLP 总量有小差异属正常（入口表按曝光归集）'}
r=4
for k in ['Search','推荐','其他','合计']:
    first=True
    for lab,key,fmt,pp in [('观看','views','#,##0',False),('观看占比','view_share','0.00%',True),
                           ('成交 GMV(元)','gmv','#,##0.00',False),('成交占比','gmv_share','0.00%',True),
                           ('进房率','tap','0.00%',True),('CTOR(点击加权)','ctor','0.00%',True),
                           ('UV价值(元/观看)','uv','0.0000',False)]:
        pv,cv=prev[k][key],cur[k][key]
        v=(cv-pv) if pp else (cv/pv-1)
        vals=[k if first else '',lab,pv,cv,v,NOTE[k] if first else '']
        for j,x in enumerate(vals,1):
            c=ws2.cell(row=r,column=j,value=x); c.border=BORDER; c.font=Font(size=10)
            c.alignment=Alignment(horizontal='left' if j in(1,2,6) else 'center',wrap_text=(j==6))
            if j in(3,4): c.number_format=fmt
            if j==5: c.number_format=('+0.00%;-0.00%' if pp else '0.00%')
            if k=='合计': c.fill=PatternFill('solid',fgColor='DDEBF7')
        pct_color(ws2.cell(row=r,column=5),v)
        first=False; r+=1
r+=1
notes2=[
 '🔴【Search 三项齐跌 —— 必须去对品广】观看 57,843 → 52,981（−8.41%）、进房率 39.52% → 38.21%（−1.31pp）、CTOR 5.14% → 4.46%（−0.68pp）三项齐跌，构成技能定义的「必须对品广消耗」条件。而同期**品牌广告消耗 5,751.60 → 6,325.51 USD（+9.98%）** —— 品广多花了一成钱，Search 进店还少了 8.4%，承接也更差。这是连续第二周的 Search 断链，且本期钱是加了的，性质比上期更严重。',
 '🔴【推荐位是总曝光下滑的主因】推荐曝光 267.7 万 → 208.5 万（−22.1%），观看 −4.75%、成交 GMV −10.05%、CTOR −1.01pp（三入口跌幅最大）、UV 2.229 → 2.105（−5.6%）。付费主战场量效双降。',
 '🟢【「其他」是唯一全面变好的入口】观看 +3.56%、成交 GMV +3.58%、成交占比 24.18% → 26.77%（+2.59pp）、CTOR 5.60% → 6.53%（全场最高）、UV 4.035（Search 0.755 的 5.3 倍）。观看占比只有 11.1% 却贡献 26.8% 成交 —— 仍是最被低估的增量池，且已经连续两周是三入口里表现最好的。',
 '🟡【成熟度提醒 —— 「其他」的实际增幅可能被低估】用你 8/24 重导的上期 TrafficSource 与 8月W2 发布值对照，7 天额外成熟度带来的 GMV 上修并不均匀：推荐 +0.88%、Search +3.71%、**其他 +20.55%**。「其他」入口（Shop tab / Inbox / Other channels）的归因尾巴最长，因此本期（期末+1 天）的其他入口 GMV 48,970 元大概率仍在偏低位置，真实增幅高于 +3.58%。',
 '【观看 ≠ 成交】Search 占 48.3% 观看只贡献 21.9% 成交；推荐占 40.7% 观看贡献 51.4% 成交；其他占 11.1% 观看贡献 26.8% 成交。做流量判断不要用观看占比代替成交占比。',
 '【配色】全套报告统一 红 = ↑ / 绿 = ↓（中国财务口径），颜色只表示方向、不表示好坏 —— 例如推荐进房率 +0.39pp 标红但那是曝光收缩的机械效应，不是变好。【口径】入口表 GMV 为 Attributed GMV（VND ÷ 3890）；与 CLP 总量的小差异属归集方式差异。',
]
r=note_block(ws2,r,notes2,NC2)
widths(ws2,[12,20,20,20,14,100]); ws2.freeze_panes='A4'

# ================= ⓪ 指标口径映射 =================
ws0=wb.create_sheet('⓪ 指标口径映射（对后台）'); NC0=5
title(ws0,1,'🔴 CLP 列 ↔ LIVE Manager 后台卡片 · 口径映射（每期先看这张，别把名字弄混）',NC0)
for i,h in enumerate(['后台卡片 / CLP 列名','公式（分子 ÷ 分母）','本期重算值','上期重算值','说明'],1): ws0.cell(row=2,column=i,value=h)
hdr(ws0,2,NC0)
MAP=[('Tap-through rate（后台卡）','Views ÷ Impressions',B['tap'],A['tap'],'＝周报里的「进房率」，同一个东西两个名字'),
 ('CTR（后台卡）','Product clicks ÷ Product Impressions',B['ctr'],A['ctr'],'🔴 分母是【商品曝光】，不是观看'),
 ('CTOR（后台卡）','Attributed orders ÷ Product clicks',B['ctor'],A['ctor'],'🔴 分子是【订单数】，不是 SKU 订单数'),
 ('Follow rate（后台卡）','New followers ÷ Views',B['follow_rate'],A['follow_rate'],''),
 ('LIVE CTR（CLP 列）','Product clicks ÷ Views',B['live_ctr'],A['live_ctr'],'25.05%，容易被误当成后台 CTR（差约 9 倍）'),
 ('CTOR (SKU orders)（CLP 列）','SKU orders ÷ Product clicks',B['ctor_sku'],A['ctor_sku'],'14.80%，容易被误当成后台 CTOR（差约 2 倍）'),
 ('SKU order rate（CLP 列）','SKU orders ÷ Views',B['sku_rate'],A['sku_rate'],'端到端转化'),
 ('AOV','Attributed GMV ÷ Attributed orders',B['aov'],A['aov'],'🔴 分母不是 SKU orders；用 SKU 单会把 AOV 砍一半')]
r=3
for n,f_,cv,pv,note in MAP:
    for j,x in enumerate([n,f_,cv,pv,note],1):
        c=ws0.cell(row=r,column=j,value=x); c.border=BORDER; c.font=Font(size=10)
        c.alignment=Alignment(horizontal='left' if j in(1,2,5) else 'center',wrap_text=(j==5))
        if j in(3,4): c.number_format=('#,##0.00' if 'AOV' in n else '0.00%')
        if n.endswith('（后台卡）'): c.fill=PatternFill('solid',fgColor='FFF2CC')
    r+=1
r+=1
r=note_block(ws0,r,[
 '【为什么会对不上】平台在两个地方用了同名不同义的指标：LIVE Manager 的 CTR / CTOR 卡片是「商品曝光」「订单数」口径；CLP 导出里另有 LIVE CTR（点击÷观看）与 CTOR (SKU orders)（SKU单÷点击）两列，本期数值 25.05% 与 14.80%，量级差 2–9 倍。周报里必须把分母写在指标名里。',
 '【差 1–3% 是正常的】本表用周合计重算（Σ分子 ÷ Σ分母），后台卡片是逐场加权 + 四舍五入，两者差 1–3% 属正常；差超过 5% 才要回头查解析。',
 '🟢【上期缺口已补】8月W2 报告里上期订单数是从 AOV 反推的（±1%）。本期你同时给了上期与本期两份 CLP 导出，订单数已是实数。但请注意：上期那份 CLP（8/24 导）缺 8/10 整场且多 7 天成熟度，本表上期列仍用 8月W2 发布值以保成熟度对齐。',
],NC0)
widths(ws0,[34,40,16,16,70])
p=f'{OUT}/KANS_VN_{PERIOD}_Step9_流量结构.xlsx'; wb.save(p); print('saved',p)
