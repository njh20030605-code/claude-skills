# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, re, json, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from _config import PERIOD, VND, OUT, FILE_PREFIX
from style import hdr, title, widths, pct_color, note_block, YELLOW, DEEPYELLOW, BORDER
def vn(s):
    if pd.isna(s): return 0.0
    s=str(s).replace('₫','').replace('%','').strip()
    if s in ('','-','nan'): return 0.0
    s=s.replace('.','').replace(',','.')
    try: return float(s)
    except: return 0.0
raw=pd.read_excel('raw/ac9c8851-product_list_20260817.xlsx',header=None)
DATEHDR=str(raw.iloc[0,0])
d=raw.iloc[4:].reset_index(drop=True)
P=pd.DataFrame({'name':d[0].astype(str),'pid':d[1].astype(str).str.strip(),
  'gmv_all':d[4].map(vn),'live_attr':d[5].map(vn),'live_dir':d[6].map(vn),
  'video_attr':d[8].map(vn),'daren':d[11].map(vn),'card':d[18].map(vn),
  'orders':d[19].map(vn),'units':d[21].map(vn),'refund':d[40].map(vn)})
P=P[P.pid.str.match(r'^\d{15,}$')].copy()
# ══════════════ 示例数据：换成你自己的导出 ══════════════
# 单链接表只列这几条主推链接，其余一律归入「其他链接」不展开（清单固定，不随周变动）
DUAL_KEY='三件套'   # 双链合并的名字关键词
LINKS=[('1000000000000000010','主推链接1 · 三件套'),('1000000000000000009','主推链接2 · 单品'),
       ('1000000000000000005','主推链接3'),('1000000000000000007','主推链接4'),
       ('1000000000000000013','主推链接5 · 三件套日间版')]
tot=P.live_attr.sum()/VND/1e4; totu=P.units.sum()
# 上期数值 {商品ID: (上期GMV万元, 上期件数)}；示例数据：换成你自己的导出
PREV={'1000000000000000010':(10.9,670),'1000000000000000009':(3.3,610),
      '1000000000000000005':(1.4,125),'1000000000000000007':(1.1,45),
      '1000000000000000013':(1.1,90)}
PREV_TOT=44.3083; PREV_TOTU=22627
rows=[]
for pid,nm in LINKS:
    s=P[P.pid==pid]
    g=s.live_attr.sum()/VND/1e4; u=s.units.sum()
    rows.append(dict(pid=pid,nm=nm,pg=PREV[pid][0],pu=PREV[pid][1],cg=g,cu=u))
df=pd.DataFrame(rows).sort_values('cg',ascending=False).reset_index(drop=True)
# 品线判定
RED=r'collagen|lão hóa|lao hoa|nếp nhăn|nep nhan|black waist|peptide'
# 品线名（示例：按功效分线；换成你自己的分法）
LINE_A, LINE_B, LINE_C, LINE_OTHER = '线A·美白', '线B·抗老', '面膜', '其他'
WHT=r'niacinamide|trắng|trang sang|thâm|tham sam|đều màu|deu mau|whitening|sáng da|sang da|neige blanc'
SUN=r'chống nắng|chong nang|sunscreen|spf|nâng tông|nang tong|tone[- ]?up'
MSK=r'mặt nạ|mat na|mask'
def line(n):
    s=n.lower()
    if re.search(MSK,s): return LINE_C
    if re.search(RED,s): return LINE_B
    if re.search(WHT,s): return LINE_A
    if re.search(SUN,s): return LINE_A
    return LINE_OTHER
P['line']=P.name.map(line)
LG=P.groupby('line').agg(gmv=('live_attr','sum'),n=('pid','size')).reset_index()
LG['gmv']=LG.gmv/VND/1e4; LG['share']=LG.gmv/tot
# 上期各品线 (GMV万元, 占比)；示例数据：换成你自己的导出
_PT=44.3
PREV_LINE={LINE_B:(22.0,22.0/_PT), LINE_A:(21.7,21.7/_PT), LINE_C:(0.5,0.5/_PT), LINE_OTHER:(0.1,0.1/_PT)}
wb=openpyxl.Workbook(); ws=wb.active; ws.title='单链接SKU对比'; NC=11
title(ws,1,'单链接 SKU 对比｜本期 08/17–08/23 vs 上期 08/10–08/16（商家直播归因 GMV，含间接）',NC)
ws.cell(row=2,column=1,value=f'口径：product_list「商家直播归因 GMV」÷{VND:,.0f} 折 RMB；占比 = 占当期自播归因合计。🔴 判定清单固定为下面 5 条（全白系，2026-08 用户两次确认），红系一律归入「其他链接」不逐条展开 —— 红系的消长看下方「按品线汇总」那段。本期导出日期头：{DATEHDR}（窗口正确）。')
ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=NC)
ws.cell(row=2,column=1).font=Font(size=9,italic=True,color='555555')
H=['排名','简称','商品ID','上期GMV(万)','上期件数','上期占比','本期GMV(万)','本期件数','本期占比','GMV变化','占比变化(pp)']
for i,h in enumerate(H,1): ws.cell(row=3,column=i,value=h)
hdr(ws,3,NC)
r=4
def put(vals,fill=None,bold=False):
    global r
    for j,v in enumerate(vals,1):
        c=ws.cell(row=r,column=j,value=v); c.border=BORDER
        c.font=Font(size=10,bold=bold); c.alignment=Alignment(horizontal='left' if j==2 else 'center')
        if j in(4,7): c.number_format='#,##0.0000'
        if j in(5,8) and isinstance(v,(int,float)): c.number_format='#,##0'
        if j in(6,9): c.number_format='0.00%'
        if j==10: c.number_format='0.00%'
        if j==11: c.number_format='+0.00%;-0.00%'
        if fill: c.fill=PatternFill('solid',fgColor=fill)
    for j in (10,11):
        v=ws.cell(row=r,column=j).value
        if isinstance(v,(int,float)): pct_color(ws.cell(row=r,column=j),v)
    r+=1
for i,x in df.iterrows():
    ps=x.pg/PREV_TOT; cs=x.cg/tot
    fill=YELLOW if DUAL_KEY in x.nm else None
    put([i+1,x.nm,x.pid,x.pg,x.pu,ps,x.cg,int(x.cu),cs,x.cg/x.pg-1,cs-ps],fill)
# DUAL_KEY：同一款货有新旧两条链接时，合并展示的名字关键词
b3p=10.9+1.1; b3c=df[df.nm.str.contains(DUAL_KEY)].cg.sum(); b3cu=df[df.nm.str.contains(DUAL_KEY)].cu.sum()
put(['',f'{DUAL_KEY} 双链合计（旧链+新版）','两条合并',b3p,759,b3p/PREV_TOT,b3c,int(b3cu),b3c/tot,b3c/b3p-1,b3c/tot-b3p/PREV_TOT],YELLOW,True)
w5p=10.8895+3.2681+1.4022+1.1085+1.0704
w5c=df.cg.sum(); w5cu=df.cu.sum()
put(['','★ 指定 5 条合计','',w5p,1536,w5p/PREV_TOT,w5c,int(w5cu),w5c/tot,w5c/w5p-1,w5c/tot-w5p/PREV_TOT],DEEPYELLOW,True)
oth_c=tot-w5c; oth_p=PREV_TOT-w5p; nlink=len(P)-len(df)
put(['',f'其他链接合计（本期 {nlink} 条）','',oth_p,21091,oth_p/PREV_TOT,oth_c,int(totu-w5cu),oth_c/tot,oth_c/oth_p-1,oth_c/tot-oth_p/PREV_TOT],None,True)
# 另一条品线的 TOP2 只作备注参考，不进排名；示例数据：换成你自己的导出
R2=[('1000000000000000011','线B链接1 · 三件套',8.20),('1000000000000000012','线B链接2 · 套装',5.93)]
put(['','自播归因 GMV 合计','',PREV_TOT,PREV_TOTU,1.0,tot,int(totu),1.0,tot/PREV_TOT-1,0.0],'DDEBF7',True)
r+=1
# 品线
ws.cell(row=r,column=1,value='🔴 按品线汇总（关键词判定；分线规则见脚本顶部 LINE_A/LINE_B —— 8月W2 的规则会把同时含防晒的美白/抗老 combo 拆到防晒桶，两期边界不一致，合并后才可比。红系两期链接数都是 82 条，规则一致）')
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC)
c=ws.cell(row=r,column=1); c.fill=PatternFill('solid',fgColor='D9E2F3'); c.font=Font(bold=True,color='1F3864',size=10); r+=1
for i,h in enumerate(['品线','','','上期GMV(万)','','上期占比','本期GMV(万)','','本期占比','GMV变化','占比变化(pp)'],1):
    ws.cell(row=r,column=i,value=h)
hdr(ws,r,NC); r+=1
ORD=[LINE_B,LINE_A,LINE_C,LINE_OTHER]
for ln in ORD:
    s=LG[LG.line==ln]
    cg=float(s.gmv.iloc[0]) if len(s) else 0.0; cs=cg/tot; n=int(s.n.iloc[0]) if len(s) else 0
    pg,ps=PREV_LINE[ln]
    cu_units=int(P[P.line==ln].units.sum())
    put([ln,f'本期链接数 {n}','',pg,'n/a',ps,cg,cu_units,cs,cg/pg-1,cs-ps],
        ('FFC7CE' if ln==LINE_B else ('DDEBF7' if ln==LINE_A else None)))
r+=1
notes=[
 # 示例数据：换成你自己的导出
 f'🔴【判定清单固定不扩】单链接表只列 LINKS 里这几条主推链接，其余归入「其他链接」。清单固定才能跨期比。',
 '🟡【另一条品线的大链只在这里备注，不进排名】把它们的两期 GMV 与涨跌写在这里，避免看漏整条线的消长；要看线级消长请用下方「按品线汇总」段。',
 '🟢【件数缺口】清单固定后，件数两期齐全；缺口通常来自上期 product_list 没导。',
 '🟢【补法】补一份上期同窗口的 product_list 导出重跑即可，脚本会自动补齐上期列。',
 '⚠️【只有一期 product_list 时】上期列会留空，跨期结论先别下。',
 '🔴【品线判定的口径坑】关键词有重叠时判定顺序决定归属（例：某品同时命中两条线的词）。改 line() 里的判定顺序前，先确认历史期用的是哪一版，否则跨期不可比。',
 '【口径 PS】① GMV = 商家直播归因 GMV（含间接），与全店 GMV、GMV-MAX Gross revenue 是三套口径，不可混用。② 占比 = 占当期自播归因合计。',
]
r=note_block(ws,r,notes,NC)
widths(ws,[7,34,22,14,11,11,14,11,11,12,13])
p=f'{OUT}/{FILE_PREFIX}_{PERIOD}_Step11_单链接SKU对比.xlsx'; wb.save(p)
print('saved',p)
print('自播归因合计 %.4f 万元 (上期 %.4f, %+.2f%%) | 件数 %d'%(tot,PREV_TOT,(tot/PREV_TOT-1)*100,totu))
print('全店GMV %.2f 万元 | 达人归因 %.2f 万元 | 商家直播直接 %.2f 万元 | 商品卡 %.2f 万元'%(
 P.gmv_all.sum()/VND/1e4,P.daren.sum()/VND/1e4,P.live_dir.sum()/VND/1e4,P.card.sum()/VND/1e4))
print(LG.to_string())
print(df[['nm','pg','cg']].to_string())
