# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from _config import PERIOD, VND, OUT, FILE_PREFIX
from style import hdr, title, widths, pct_color, note_block, YELLOW, DEEPYELLOW, BORDER
f=pd.read_pickle('out/aff_cur.pkl')
paid=set(open(f'{OUT}/paid_kol.txt').read().split())
f['h']=f['达人用户名'].astype(str).str.strip().str.lower(); f['is_kol']=f.h.isin(paid)
def kol(pid):
    s=f[f['商品 ID']==pid]
    if not len(s) or s.amt.sum()==0: return None,0.0
    return s.loc[s.is_kol,'amt'].sum()/s.amt.sum(), s.amt.sum()/VND/1e4
# ══════════════ 示例数据：换成你自己的导出 ══════════════
# 每条 = (计划名, 商品ID, 品线, 上期成本, 上期收入, 本期成本, 本期收入, 备注)
# 成本/收入单位都是本币万元口径下的原始值，直接照搬你后台「GMV MAX 商品广告」导出的两期数字。
# 备注留空即可，写了会渲染成表格里的黄色批注块。
PLANS=[
 ('计划A-主推品','1000000000000000001','线A', 70000,250000, 75000,270000, '🟢 示例备注：本期成本 +7%、收入 +8%，ROI 同步抬升，是最该提预算的一条'),
 ('计划B','1000000000000000002','线A', 35000,110000, 28000,93000, ''),
 ('计划C','1000000000000000003','线B', 23000,73000, 20000,64000, ''),
 ('计划D-单品','1000000000000000004','线A', 2000,10000, 1500,6800, '🔴 示例备注：连续第三周被砍预算，但 ROI 仍是全表最高'),
 ('计划E','1000000000000000005','线B', 1500,4400, 1000,2600, '🔴 示例备注：ROI 跌破目标，达人端两期都是 0% KOL'),
 ('计划F','1000000000000000006','线B', 1500,3600, 1560,3500, '🟡 示例备注：上期无达人订单，本期首次有'),
 ('计划G-单品','1000000000000000007','线B', 900,3200, 550,1300, '🔴 示例备注：ROI 跌幅全表最大，目标只达成四成'),
]
# 上期 KOL 占比（None = 上期没有达人订单，表里显示「—」）
PREV_KOL={'计划A-主推品':.63,'计划B':.61,'计划C':.41,
 '计划D-单品':.15,'计划E':.0,'计划F':None,'计划G-单品':.0}
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
        fill=(YELLOW if line=='线B' else None))
SUB=[p for p in PLANS if p[5] is not None]
pc=sum(p[3] for p in SUB); pr=sum(p[4] for p in SUB); cc=sum(p[5] for p in SUB); cr=sum(p[6] for p in SUB)
P7=['1000000000000000004','1000000000000000006','1000000000000000003','1000000000000000009',
    '1000000000000000002','1000000000000000001','1000000000000000008']
f7=f[f['商品 ID'].isin(P7)]; k7=f7.loc[f7.is_kol,'amt'].sum()/f7.amt.sum()
ac=sum(p[3] for p in PLANS); ar=sum(p[4] for p in PLANS)
bc=sum(p[5] for p in PLANS); br=sum(p[6] for p in PLANS)
put(['★ 合计 / 加权（7 条计划，两期齐全）',ac,ar,ar/ac,bc,br,br/bc,bc/ac-1,br/ar-1,br/bc-ar/ac,
     .5649,.4351,k7,1-k7,(k7-.5649)*100],'D9E1F2',True)
r+=1
ws.cell(row=r,column=1,value='按品线拆（全品线口径，两期齐全）　│　线A / 线B 的归属见上面 PLANS 的第 3 个字段　│　左半商品卡金额取平台原生 ¥；右半 KOL/KOC 来自 affiliate_orders，按达人GMV加权')
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC)
c=ws.cell(row=r,column=1); c.fill=PatternFill('solid',fgColor='D9E2F3'); c.font=Font(bold=True,size=10,color='1F3864'); c.border=BORDER; r+=1
LINE_ALL={'线A':['1000000000000000004','1000000000000000006','1000000000000000009'],
          '线B':['1000000000000000003','1000000000000000002','1000000000000000001','1000000000000000008']}
PREV_LINE_KOL={'线A':.6141,'线B':.3884}   # 8月W2 已发布的品线小计（同为达人GMV加权、全品线口径）
for lab,sel in [('线A小计','线A'),('线B小计','线B')]:
    S=[p for p in PLANS if p[2]==sel]
    a=sum(p[3] for p in S); b=sum(p[4] for p in S); x=sum(p[5] for p in S); y=sum(p[6] for p in S)
    fs=f[f['商品 ID'].isin(LINE_ALL[sel])]
    k=fs.loc[fs.is_kol,'amt'].sum()/fs.amt.sum(); pk=PREV_LINE_KOL[sel]
    put([lab,a,b,b/a,x,y,y/x,x/a-1,y/b-1,y/x-b/a,pk,1-pk,k,1-k,(k-pk)*100],
        ('FCE4E4' if sel=='线B' else 'DDEBF7'),True)
r+=1
notes=[
 # 示例数据：换成你自己的导出。这些备注会渲染成表底的黄色结论块，
 # 写法建议：🟢 好转 / 🔴 恶化 / 🟡 观察 / ⚠️ 口径提醒，每条先给结论再给数字。
 '🟢🟢【务必用合计行，别只看部分计划】计划齐全时成本 −5.7%、收入 −4.5%、ROI 反而在涨。只拿到部分计划时算出的结论会反向 —— 缺掉的那条主推计划占本期成本近六成，正好是拉总量的。',
 '🔴【分化在品线，不在总量】线A 成本小幅下降而 ROI 上升；线B 砍了一成多、效率还在退。线B 是本期真正在退的那条线。',
 '🔴【单品计划连续第三周被两端同时砍】商品卡成本 −26.8%，达人 KOL 占比 −4.6pp，而它的 ROI 是全表最高。连续两期报告都点出同一问题。',
 '🟢【最该加预算的是主推品】目标 ROI 达成 99.8%，但成本已超预算 45.8% —— 说明它一直被预算卡着跑，且占本期成本近六成。',
 '🟡【某计划首次跑出达人视频成交】样本很小，先当观察项。',
 '🔴【效率最差项】ROI 跌幅全表最大，目标只达成四成。见「目标ROI达成」sheet。',
 '⚠️【KOL/KOC 与左侧不是一套口径】末五列来自 affiliate_orders 导出，与左半商品卡口径不同，不要横向相减。',
 '⚠️【付费达人清单会变】清单人数变化会结构性抬高或压低 KOL 占比，跨期对比时先看清单规模。',
 '【判定方式】付费达人清单匹配 affiliate_orders 的「达人用户名」：命中即 KOL，其余全部 KOC。',
 '【口径 PS】ROI = 收入 ÷ 成本。ROI变化 与 KOL占比变化 为 pp（绝对差）。',
]
r=note_block(ws,r,notes,NC)
widths(ws,[30,11,11,10,11,11,10,11,11,12,12,12,12,12,13])
# ---- sheet2 目标ROI达成 ----
ws2=wb.create_sheet('目标ROI达成 + 达人GMV'); NC2=8
title(ws2,1,f'商品卡计划 · 目标 ROI 达成率 + 本期达人视频 GMV（本期 {PERIOD}）',NC2)
for i,h in enumerate(['广告计划名称','目标 ROI','实际 ROI','达成率','计划预算(¥)','本期成本(¥)','本期达人视频GMV(万¥)','本期KOL占比'],1):
    ws2.cell(row=2,column=i,value=h)
hdr(ws2,2,NC2)
# 示例数据：换成你自己的导出。(计划名, 目标ROI, 计划预算, 本期成本, 商品ID)
TGT=[('计划A-主推品',3.60,51600,75000,'1000000000000000001'),
     ('计划B',3.30,23220,28000,'1000000000000000002'),
     ('计划C',3.20,23220,20000,'1000000000000000003'),
     ('计划E',3.20,1548,1000,'1000000000000000005'),
     ('计划F',3.00,1548,1560,'1000000000000000006'),
     ('计划D-单品',5.50,2322,1500,'1000000000000000004'),
     ('计划G-单品',5.50,1548,550,'1000000000000000007')]
# 实际 ROI = 本期收入 ÷ 本期成本（与上面 PLANS 的两期数字保持一致）
ACT={nm:(rev/cost) for nm,_pid,_line,_c1,_r1,cost,rev,_note in PLANS}
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
 # 示例数据：换成你自己的导出
 '🔴【欠达计划（达成率 <85%）】列出计划名与达成率，并指出是否集中在同一条品线 —— 集中说明是品线问题，分散说明是单计划问题。',
 '🟢【主力计划接近满达成】列出占成本大头的几条及其达成率，说明主力盘是否健康。',
 '🔴🔴【预算是不是真实约束】成本 ÷ 预算 >100% 且达成率高 = 该提预算；预算给了却花不出去（<70%）= 不是预算限制，是量起不来。',
 '【口径】目标 ROI / 计划预算 / 排期时间取自计划详情页头部；达人视频 GMV 与 KOL 占比来自 affiliate_orders，与左侧商品卡成本不是一套口径。',
],NC2)
widths(ws2,[30,12,12,12,14,14,20,14])
p=f'{OUT}/{FILE_PREFIX}_{PERIOD}_GMV-MAX商品卡对比.xlsx'; wb.save(p); print('saved',p)
print('可比5条: 成本 %d->%d (%.2f%%) 收入 %d->%d (%.2f%%) ROI %.4f->%.4f'%(pc,cc,(cc/pc-1)*100,pr,cr,(cr/pr-1)*100,pr/pc,cr/cc))
