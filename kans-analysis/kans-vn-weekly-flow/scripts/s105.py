# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from _config import PERIOD, VND, OUT
from style import hdr, title, widths, pct_color, note_block, YELLOW, DEEPYELLOW, BORDER
f=pd.read_pickle('out/aff_cur.pkl')
paid=set(open(f'{OUT}/paid_kol.txt').read().split())
f['h']=f['达人用户名'].astype(str).str.strip().str.lower(); f['is_kol']=f.h.isin(paid)
def kol(pid):
    s=f[f['商品 ID']==pid]
    if not len(s) or s.amt.sum()==0: return None,0.0
    return s.loc[s.is_kol,'amt'].sum()/s.amt.sum(), s.amt.sum()/VND/1e4
# 计划 ← 商品ID 映射（按商品名判定，与 8月W2 一致）
PLANS=[
 ('MKT-白精华-0708','1731561143212017689','白', 72466,256468, 75207,270129, '🟢🟢 全表最大计划（占本期成本 58.3%、收入 61.1%）：**成本 +3.78%、收入 +5.33%、ROI 3.539→3.592，是唯一在加投且效率还在升的计划**；目标 3.60 达成 99.8%，但预算 51,600 已被超投 45.8% —— 最该正式提预算的一条'),
 ('MKT-素颜霜-0708','1731728613455398937','白', 34874,111643, 28573,93553, ''),
 ('MKT-红精华-0708','1731559750857099289','红', 23383,73119, 20572,63992, ''),
 ('OL-白精华single-0715','1734336273358619673','白', 2089,10211, 1529,6836, '🔴 连续第三周被砍：成本 −26.8%，而 ROI 4.47 仍是全表最高'),
 ('MKT-红洁面-0708','1731558826539714585','红', 1503,4429, 995,2611, '🔴 成本 −33.8%、ROI 2.947→2.624，目标 3.20 只达成 82.0%；达人端两期都是 0% KOL（纯 KOC 自然量）'),
 ('MKT-红面霜-0803','1731174494226646041','红', 1531,3584, 1561,3487, '🟡 上期两期均无达人订单，本期首次有（KOL 7.87%）'),
 ('OL-红精华single-0722','1734336201423553561','红', 875,3248, 545,1268, '🔴 ROI 3.71 → 2.33（−1.38 全表最大跌幅），目标 5.50 只达成 42%'),
]
PREV_KOL={'MKT-白精华-0708':.6262,'MKT-素颜霜-0708':.6053,'MKT-红精华-0708':.4090,
 'OL-白精华single-0715':.1483,'MKT-红洁面-0708':.0,'MKT-红面霜-0803':None,'OL-红精华single-0722':.0}
wb=openpyxl.Workbook(); ws=wb.active; ws.title='GMV-MAX商品卡'; NC=15
ws.cell(row=1,column=2,value='周期1：2026-08-10 ~ 08-16'); ws.cell(row=1,column=5,value='周期2：2026-08-17 ~ 08-23')
ws.cell(row=1,column=8,value='环比变化'); ws.cell(row=1,column=11,value='达人视频 KOL/KOC（两期对比 · 按达人GMV加权 · 全品线口径，不受商品卡缺计划影响）')
for c0,c1 in [(2,4),(5,7),(8,10),(11,15)]:
    ws.merge_cells(start_row=1,start_column=c0,end_row=1,end_column=c1)
    c=ws.cell(row=1,column=c0); c.font=Font(bold=True,size=10,color='FFFFFF')
    c.fill=PatternFill('solid',fgColor='7F7F7F'); c.alignment=Alignment(horizontal='center')
H=['广告计划名称','成本(¥)','收入(¥)','ROI','成本(¥)','收入(¥)','ROI','成本环比','收入环比','ROI变化-pp',
   '上期KOL占比','上期KOC占比','本期KOL占比','本期KOC占比','KOL占比变化-pp']
for i,h in enumerate(H,1): ws.cell(row=2,column=i,value=h)
hdr(ws,2,NC)
r=3
def put(vals,fill=None,bold=False):
    global r
    for j,v in enumerate(vals,1):
        c=ws.cell(row=r,column=j,value=v); c.border=BORDER; c.font=Font(size=10,bold=bold)
        c.alignment=Alignment(horizontal='left' if j==1 else 'center')
        if j in(2,3,5,6) and isinstance(v,(int,float)): c.number_format='#,##0'
        if j in(4,7) and isinstance(v,(int,float)): c.number_format='0.0000'
        if j in(8,9) and isinstance(v,(int,float)): c.number_format='0.00%'
        if j==10 and isinstance(v,(int,float)): c.number_format='+0.0000;-0.0000'
        if j in(11,12,13,14) and isinstance(v,(int,float)): c.number_format='0.00%'
        if j==15 and isinstance(v,(int,float)): c.number_format='+0.00;-0.00'
        if fill: c.fill=PatternFill('solid',fgColor=fill)
    for j in (8,9,10,15):
        _v=ws.cell(row=r,column=j).value
        if isinstance(_v,(int,float)): pct_color(ws.cell(row=r,column=j),_v)
    r+=1
NOTES={}
for nm,pid,line,pc,pr,cc,cr in [(p[0],p[1],p[2],p[3],p[4],p[5],p[6]) for p in PLANS]:
    k,dg=kol(pid); pk=PREV_KOL[nm]
    NOTES[nm]=[p[7] for p in PLANS if p[0]==nm][0]
    put([nm,pc,pr,pr/pc, cc,cr,(cr/cc if cc else None),
         (cc/pc-1 if cc else None),(cr/pr-1 if cc else None),((cr/cc)-(pr/pc) if cc else None),
         pk,(1-pk if pk is not None else None),k,(1-k if k is not None else None),
         ((k-pk)*100 if (k is not None and pk is not None) else None)],
        fill=(YELLOW if line=='红' else None))
SUB=[p for p in PLANS if p[5] is not None]
pc=sum(p[3] for p in SUB); pr=sum(p[4] for p in SUB); cc=sum(p[5] for p in SUB); cr=sum(p[6] for p in SUB)
P7=['1731561143212017689','1731728613455398937','1731559750857099289','1734336273358619673',
    '1731558826539714585','1731174494226646041','1734336201423553561']
f7=f[f['商品 ID'].isin(P7)]; k7=f7.loc[f7.is_kol,'amt'].sum()/f7.amt.sum()
ac=sum(p[3] for p in PLANS); ar=sum(p[4] for p in PLANS)
bc=sum(p[5] for p in PLANS); br=sum(p[6] for p in PLANS)
put(['★ 合计 / 加权（7 条计划，两期齐全）',ac,ar,ar/ac,bc,br,br/bc,bc/ac-1,br/ar-1,br/bc-ar/ac,
     .5649,.4351,k7,1-k7,(k7-.5649)*100],'D9E1F2',True)
r+=1
ws.cell(row=r,column=1,value='按品线拆（全品线口径，两期齐全）　│　白系 = 白精华 / 素颜霜 / 白精华single　│　红系 = 红精华 / 红洁面 / 红面霜 / 红精华single　│　左半商品卡金额取平台原生 ¥；右半 KOL/KOC 来自 affiliate_orders，按达人GMV加权')
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC)
c=ws.cell(row=r,column=1); c.fill=PatternFill('solid',fgColor='D9E2F3'); c.font=Font(bold=True,size=10,color='1F3864'); c.border=BORDER; r+=1
LINE_ALL={'白':['1731561143212017689','1731728613455398937','1734336273358619673'],
          '红':['1731559750857099289','1731558826539714585','1731174494226646041','1734336201423553561']}
PREV_LINE_KOL={'白':.6141,'红':.3884}   # 8月W2 已发布的品线小计（同为达人GMV加权、全品线口径）
for lab,sel in [('白系小计','白'),('红系小计','红')]:
    S=[p for p in PLANS if p[2]==sel]
    a=sum(p[3] for p in S); b=sum(p[4] for p in S); x=sum(p[5] for p in S); y=sum(p[6] for p in S)
    fs=f[f['商品 ID'].isin(LINE_ALL[sel])]
    k=fs.loc[fs.is_kol,'amt'].sum()/fs.amt.sum(); pk=PREV_LINE_KOL[sel]
    put([lab,a,b,b/a,x,y,y/x,x/a-1,y/b-1,y/x-b/a,pk,1-pk,k,1-k,(k-pk)*100],
        ('FCE4E4' if sel=='红' else 'DDEBF7'),True)
r+=1
notes=[
 '🟢🟢【7 条计划两期已齐全 —— 结论与「只看 5 条」时完全不同，务必用合计行】成本 136,721 → 128,982 元（−5.66%）、收入 462,702 → 441,876 元（−4.50%）、**ROI 3.3843 → 3.4259（+0.042，在涨）**。此前只拿到 5 条时算出的「成本 −15.89% / ROI −0.011」是缺口造成的假象 —— 缺掉的 MKT-白精华-0708 占本期成本 58.3%，而它**成本 +3.78%、收入 +5.33%、ROI 还在升**，正好是拉总量的那条。**商品卡端本期是「小幅缩量 + 效率微升」，不是缩量也不是效率问题。**',
 '🔴【真正的分化在品线，不在总量】白系（白精华+素颜霜+白精华single）成本 109,429 → 105,309（−3.77%）、收入 −2.06%、**ROI 3.4572 → 3.5184（+0.061）**；红系（红精华+红洁面+红面霜+红精华single）成本 27,292 → 23,673（−13.26%）、收入 −15.43%、**ROI 3.0918 → 3.0143（−0.078）**。**白系几乎没砍且效率在升，红系砍了 13% 效率还在退** —— 与 Step11「红系自播归因 −17.3% vs 白系 −7.2%」完全同向，红系是本期真正在退的那条线。',
 '🔴【记住这个教训：缺一条大计划能把总量结论带偏 10pp】只拿到 5 条时算出「成本 −15.89% / ROI −0.011」，补齐后真实是「成本 −5.66% / ROI **+0.042**」—— 方向都反了。以后凡是缺计划，一律先补齐再下任何总量判断，别用可比子集当结论。',
 '🔴【OL-白精华single-0715 连续第三周被两端同时砍】商品卡成本 2,089 → 1,529 元（−26.8%，上期已 −10.1%），达人 KOL 占比 14.83% → 10.25%（−4.58pp，上期已 −20.49pp）。而它的 ROI 4.47 是全表最高。**这是连续两期报告都点出来的同一个问题，仍在恶化。**',
 '🟢【最该加预算的是白精华，不是别的】MKT-白精华-0708 目标 ROI 3.60、实际 3.5918（达成 99.8%），但成本 75,207 已经超预算 51,600 的 **45.8%** —— 说明它一直在被预算卡着跑。它占本期商品卡成本 58.3%、收入 61.1%，是唯一「量大 + 达标 + 还在超投」的计划。',
 '🟢【红面霜首次跑出达人视频成交】上期两期都无达人订单（当时留空），本期有 25 单 / 0.18 万元 / KOL 7.87%。样本很小，先当观察项。',
 '🔴【OL-红精华single-0722 是本期效率最差项】ROI 3.71 → 2.33（−1.38，全表最大跌幅），目标 ROI 5.50 只达成 42.4%；成本已从 875 砍到 545 元（−37.7%）。见「目标ROI达成」sheet。',
 '🔴【上期已修正 —— 品线小计的 KOL 占比之前算错了】8月W3 初版把品线小计的上期 KOL 占比按「商品卡成本」加权（红系那行还把上期没有达人订单的红面霜当 0% 算进了分母），与口径要求的「按达人 GMV 加权」不符。本表已改为：右半 KOL/KOC 一律**全品线口径 + 达人GMV加权**，上期直接取 8月W2 已发布的品线小计值（同口径同权重），本期用 affiliate_orders 重算。修正后：白系 61.41% → 63.47%（+2.06pp）、红系 38.84% → 35.28%（−3.56pp）、合计 56.49% → 57.65%（+1.16pp）。',
 '⚠️【KOL/KOC 与左侧不是一套口径】末五列来自 affiliate_orders 导出（内容形式全部为「视频」），是**达人视频渠道**成交；左侧成本/收入是 GMV-MAX 商品卡投放。两者不可相加，也不可与直播 campaign（本期净成本 46,718 元）相加 —— 三套口径互不相加。',
 '🔴【本期只有一期 affiliate_orders】上期（08/10–08/16）那份没给，因此末五列的上期 KOL/KOC 直接引用 8月W2 已发布值。',
 '🔴【付费达人清单从 610 个涨到 679 个（+11.3%），KOL 占比会被结构性抬高】上期用的是 610 个去重用户名，本期清单（Paid KOL Posting Schedule · K 列，原始 873 行）去重后 679 个。本期匹配率 301 个达人命中 139 = 46.2%，与上期 46.2% 一致，所以占比方向可用；但**合计 KOL 占比 56.49% → 57.65%（+1.16pp）里有一部分来自清单变长，不全是真实结构变化**。要做严格环比需要用上期同一份清单重算，或把新增的 69 个名单单列出来。',
 '【判定方式】清单匹配 affiliate_orders 的「达人用户名」：命中即 KOL，其余全部 KOC。金额用「支付金额」÷3,890 折 RMB，已剔除订单状态=客户未付款（本期 1,086 行 / 4,007 行 = 27.1%，比例远高于上期，不剔会把结构算歪）。合计与小计行的 KOL/KOC 按达人 GMV 加权，不是各行简单平均。',
 '【口径 PS】ROI = 收入 ÷ 成本。ROI变化 与 KOL占比变化 为 pp（绝对差）。黄底 = 红系抗老计划。环比配色 红=↑ 绿=↓。左侧金额为平台原生 ¥ 显示值。',
]
r=note_block(ws,r,notes,NC)
widths(ws,[30,11,11,10,11,11,10,11,11,12,12,12,12,12,13])
# ---- sheet2 目标ROI达成 ----
ws2=wb.create_sheet('目标ROI达成 + 达人GMV'); NC2=8
title(ws2,1,'商品卡计划 · 目标 ROI 达成率 + 本期达人视频 GMV（本期 08/17–08/23）',NC2)
for i,h in enumerate(['广告计划名称','目标 ROI','实际 ROI','达成率','计划预算(¥)','本期成本(¥)','本期达人视频GMV(万¥)','本期KOL占比'],1):
    ws2.cell(row=2,column=i,value=h)
hdr(ws2,2,NC2)
TGT=[('MKT-白精华-0708',3.60,51600,75207,'1731561143212017689'),
     ('MKT-素颜霜-0708',3.30,23220,28573,'1731728613455398937'),
     ('MKT-红精华-0708',3.20,23220,20572,'1731559750857099289'),
     ('MKT-红洁面-0708',3.20,1548,995,'1731558826539714585'),
     ('MKT-红面霜-0803',3.00,1548,1561,'1731174494226646041'),
     ('OL-白精华single-0715',5.50,2322,1529,'1734336273358619673'),
     ('OL-红精华single-0722',5.50,1548,545,'1734336201423553561')]
ACT={'MKT-白精华-0708':270129/75207,'MKT-红洁面-0708':2611/995,'MKT-素颜霜-0708':93553/28573,'MKT-红精华-0708':63992/20572,'MKT-红面霜-0803':3487/1561,
     'OL-白精华single-0715':6836/1529,'OL-红精华single-0722':1268/545}
r=3
for nm,tg,bud,cost,pid in TGT:
    k,dg=kol(pid); act=ACT[nm]
    vals=[nm,tg,act,act/tg,bud,cost,dg,k]
    for j,v in enumerate(vals,1):
        c=ws2.cell(row=r,column=j,value=v); c.border=BORDER; c.font=Font(size=10)
        c.alignment=Alignment(horizontal='left' if j==1 else 'center')
        if j in(2,3): c.number_format='0.00'
        if j==4: c.number_format='0.0%'
        if j in(5,6): c.number_format='#,##0'
        if j==7: c.number_format='0.0000'
        if j==8: c.number_format='0.00%'
        if act/tg<0.85: c.fill=PatternFill('solid',fgColor='FFC7CE')
    r+=1
r+=1
r=note_block(ws2,r,[
 '🔴【四条计划欠达（<85%）】OL-红精华single-0722 **42.3%**（2.33/5.50）、MKT-红面霜-0803 74.5%（2.23/3.00）、OL-白精华single-0715 81.3%（4.47/5.50）、MKT-红洁面-0708 82.0%（2.62/3.20）。**四条里三条是红系** —— 红系整体达不到自己设的目标。',
 '🟢【三条主力全部接近满达成】MKT-白精华-0708 **99.8%**（3.5918/3.60）、素颜霜 99.2%（3.27/3.30）、红精华 97.2%（3.11/3.20）。这三条占本期商品卡成本 96.4%。',
 '🔴🔴【预算是白精华的真实约束】白精华成本 75,207 / 预算 51,600 = **145.8%**，长期超投还能保住 99.8% 达成率 —— 这是最该正式提预算的一条。反向看：红洁面 995 / 1,548 = 64.3%、红精华single 545 / 1,548 = 35.2%，预算给了却花不出去，说明不是预算限制而是量起不来。',
 '【口径】目标 ROI / 计划预算 / 排期时间取自计划详情页头部；达人视频 GMV 与 KOL 占比来自 affiliate_orders，与左侧商品卡成本不是一套口径。',
],NC2)
widths(ws2,[30,12,12,12,14,14,20,14])
p=f'{OUT}/KANS_VN_{PERIOD}_GMV-MAX商品卡对比.xlsx'; wb.save(p); print('saved',p)
print('可比5条: 成本 %d->%d (%.2f%%) 收入 %d->%d (%.2f%%) ROI %.4f->%.4f'%(pc,cc,(cc/pc-1)*100,pr,cr,(cr/pr-1)*100,pr/pc,cr/cc))
