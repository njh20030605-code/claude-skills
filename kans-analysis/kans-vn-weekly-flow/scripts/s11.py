# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, re, json, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from _config import PERIOD, VND, OUT
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
# 🔴 固定 5 条（2026-08 用户再次确认）：只列白系这 5 条，红系一律归入「其他链接」不展开
LINKS=[('1734360557016744985','白3（精华、霜、水）'),('1734336273358619673','白 single'),
       ('1731577149049636889','白2'),('1732293821262365721','白7'),
       ('1736359308434310169','白3（霜、精华、素颜霜）')]
tot=P.live_attr.sum()/VND/1e4; totu=P.units.sum()
PREV={'1734360557016744985':(10.8895,668),'1734336273358619673':(3.2681,607),
      '1731577149049636889':(1.4022,125),'1732293821262365721':(1.1085,45),
      '1736359308434310169':(1.0704,91)}
PREV_TOT=44.3083; PREV_TOTU=22627
rows=[]
for pid,nm in LINKS:
    s=P[P.pid==pid]
    g=s.live_attr.sum()/VND/1e4; u=s.units.sum()
    rows.append(dict(pid=pid,nm=nm,pg=PREV[pid][0],pu=PREV[pid][1],cg=g,cu=u))
df=pd.DataFrame(rows).sort_values('cg',ascending=False).reset_index(drop=True)
# 品线判定
RED=r'collagen|lão hóa|lao hoa|nếp nhăn|nep nhan|black waist|peptide'
WHT=r'niacinamide|trắng|trang sang|thâm|tham sam|đều màu|deu mau|whitening|sáng da|sang da|neige blanc'
SUN=r'chống nắng|chong nang|sunscreen|spf|nâng tông|nang tong|tone[- ]?up'
MSK=r'mặt nạ|mat na|mask'
def line(n):
    s=n.lower()
    if re.search(MSK,s): return '面膜'
    if re.search(RED,s): return '红系·抗老'
    if re.search(WHT,s): return '白系·美白（含防晒/素颜霜）'
    if re.search(SUN,s): return '白系·美白（含防晒/素颜霜）'
    return '其他'
P['line']=P.name.map(line)
LG=P.groupby('line').agg(gmv=('live_attr','sum'),n=('pid','size')).reset_index()
LG['gmv']=LG.gmv/VND/1e4; LG['share']=LG.gmv/tot
PREV_LINE={'红系·抗老':(22.0511,22.0511/44.3083),'白系·美白（含防晒/素颜霜）':(20.039+1.6373,(20.039+1.6373)/44.3083),
           '面膜':(0.5194,0.5194/44.3083),'其他':(0.0616,0.0616/44.3083)}
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
    fill=YELLOW if '白3' in x.nm else None
    put([i+1,x.nm,x.pid,x.pg,x.pu,ps,x.cg,int(x.cu),cs,x.cg/x.pg-1,cs-ps],fill)
b3p=10.8895+1.0704; b3c=df[df.nm.str.contains('白3')].cg.sum(); b3cu=df[df.nm.str.contains('白3')].cu.sum()
put(['','白3 双链合计（旧链+日间版）','两条合并',b3p,759,b3p/PREV_TOT,b3c,int(b3cu),b3c/tot,b3c/b3p-1,b3c/tot-b3p/PREV_TOT],YELLOW,True)
w5p=10.8895+3.2681+1.4022+1.1085+1.0704
w5c=df.cg.sum(); w5cu=df.cu.sum()
put(['','★ 指定 5 条合计','',w5p,1536,w5p/PREV_TOT,w5c,int(w5cu),w5c/tot,w5c/w5p-1,w5c/tot-w5p/PREV_TOT],DEEPYELLOW,True)
oth_c=tot-w5c; oth_p=PREV_TOT-w5p; nlink=len(P)-len(df)
put(['',f'其他链接合计（本期 {nlink} 条）','',oth_p,21091,oth_p/PREV_TOT,oth_c,int(totu-w5cu),oth_c/tot,oth_c/oth_p-1,oth_c/tot-oth_p/PREV_TOT],None,True)
# 红系 TOP2 只作备注参考，不进排名
R2=[('1734360692245169177','红2 · Combo Toner+霜+精华',8.20),('1736024861094937625','红3 · Black Waist Combo 3 món',5.93)]
put(['','自播归因 GMV 合计','',PREV_TOT,PREV_TOTU,1.0,tot,int(totu),1.0,tot/PREV_TOT-1,0.0],'DDEBF7',True)
r+=1
# 品线
ws.cell(row=r,column=1,value='🔴 按品线汇总（关键词判定；本期把「防晒/素颜霜」并入白系 —— 8月W2 的规则会把同时含防晒的美白/抗老 combo 拆到防晒桶，两期边界不一致，合并后才可比。红系两期链接数都是 82 条，规则一致）')
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC)
c=ws.cell(row=r,column=1); c.fill=PatternFill('solid',fgColor='D9E2F3'); c.font=Font(bold=True,color='1F3864',size=10); r+=1
for i,h in enumerate(['品线','','','上期GMV(万)','','上期占比','本期GMV(万)','','本期占比','GMV变化','占比变化(pp)'],1):
    ws.cell(row=r,column=i,value=h)
hdr(ws,r,NC); r+=1
ORD=['红系·抗老','白系·美白（含防晒/素颜霜）','面膜','其他']
for ln in ORD:
    s=LG[LG.line==ln]
    cg=float(s.gmv.iloc[0]) if len(s) else 0.0; cs=cg/tot; n=int(s.n.iloc[0]) if len(s) else 0
    pg,ps=PREV_LINE[ln]
    cu_units=int(P[P.line==ln].units.sum())
    put([ln,f'本期链接数 {n}','',pg,'n/a',ps,cg,cu_units,cs,cg/pg-1,cs-ps],
        ('FFC7CE' if ln=='红系·抗老' else ('DDEBF7' if ln.startswith('白系') else None)))
r+=1
notes=[
 f'🔴【判定清单固定 5 条，不再扩】2026-08 用户两次确认：单链接表只列这 5 条白系，红系不进排名。指定 5 条合计 {w5p:.2f} → {w5c:.2f} 万元（{w5c/w5p-1:+.1%}），覆盖自播归因 {w5p/PREV_TOT:.1%} → {w5c/tot:.1%}。白3 双链 {b3p:.2f} → {b3c:.2f} 万元（{b3c/b3p-1:+.1%}），仍是单链维度第一。',
 '🟡【红系两条大链只在这里备注，不进上面的排名】红2 `1734360692245169177` 8.20 → 8.14 万元（−0.79%，本期实际是自播归因的第 2 名）；红3 `1736024861094937625` Black Waist 5.93 → **3.11 万元（−47.63%）**，是红系整体下滑的主因。两条都归在「其他链接」里。要看红系的消长请用下方「按品线汇总」段 —— 那一段就是为这件事设计的。',
 '🟢【上期件数已无缺口】回到固定 5 条后，5 条的上期件数（668/607/125/45/91，合计 1,536）在 8月W2 表里都有，「其他链接」上期件数 = 22,627 − 1,536 = 21,091，全部可算。只有「按品线汇总」段的上期件数仍是 n/a（8月W2 未按品线拆件数），需要上期 product_list 才能补。',
 '🟢【补法很简单】只要补一份 08/10–08/16 窗口的 product_list 导出，上面所有 n/a 都能填满，同时单链接与品线的环比也能变成同成熟度口径（现在上期多 7 天归因，环比系统性偏低）。这是本期唯一还缺的一份表。',
 '⚠️【只有本期 product_list】本期只拿到 08/17–08/23 一份导出，上期各链接值取自 8月W2 已发布表（同为 product_list 商家直播归因口径、同汇率）。两期成熟度不同（上期已多 7 天归因），因此**单链接的环比会系统性偏低**，方向可用、幅度偏保守 —— 与 Step9 观察到的 +3%~+20% 成熟度上修同源。',
 '🔴【品线判定的口径坑（本期新发现，写进口径提醒）】8月W2 的规则先判「防晒/素颜霜」再判红/白，会把「Combo 7 Món Dưỡng Da Chống Lão Hóa + Kem Chống Nắng」这类同时含防晒的抗老/美白 combo 整条划进防晒桶（上期 13 条 / 1.64 万元）。本期改为先判红/白、再判防晒，红系链接数两期都是 82 条（规则一致），白系与防晒的边界才是漂的 —— 因此本表把「防晒/素颜霜」并入白系后才做环比，否则会凭空造出「白系 −15%、防晒 +130%」的假结构变化。',
 '【口径 PS】① GMV = 商家直播归因 GMV（含间接），非全店 GMV、非 GMV-MAX Gross revenue，三者不可混用。② 品线关键词：collagen / lão hóa / nếp nhăn / black waist / peptide → 红系抗老；niacinamide / trắng / thâm / đều màu / whitening / sáng da / neige blanc / chống nắng / SPF / nâng tông → 白系美白（含防晒素颜霜）；mặt nạ / mask → 面膜。③ 黄底 = 白3 主讲品。④ 环比 红=↑ 绿=↓。',
]
r=note_block(ws,r,notes,NC)
widths(ws,[7,34,22,14,11,11,14,11,11,12,13])
p=f'{OUT}/KANS_VN_{PERIOD}_Step11_单链接SKU对比.xlsx'; wb.save(p)
print('saved',p)
print('自播归因合计 %.4f 万元 (上期 %.4f, %+.2f%%) | 件数 %d'%(tot,PREV_TOT,(tot/PREV_TOT-1)*100,totu))
print('全店GMV %.2f 万元 | 达人归因 %.2f 万元 | 商家直播直接 %.2f 万元 | 商品卡 %.2f 万元'%(
 P.gmv_all.sum()/VND/1e4,P.daren.sum()/VND/1e4,P.live_dir.sum()/VND/1e4,P.card.sum()/VND/1e4))
print(LG.to_string())
print(df[['nm','pg','cg']].to_string())
