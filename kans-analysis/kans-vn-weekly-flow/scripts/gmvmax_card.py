# -*- coding: utf-8 -*-
"""GMV-MAX 商品卡 · 两期对比 + 达人视频 KOL/KOC

🔴 列结构已由用户确认，**固定 15 列，不要加也不要减**：
   A 广告计划名称
   B/C/D  周期1 成本 / 收入 / ROI
   E/F/G  周期2 成本 / 收入 / ROI
   H/I/J  成本环比 / 收入环比 / ROI变化-pp
   K/L/M/N/O  上期KOL占比 / 上期KOC占比 / 本期KOL占比 / 本期KOC占比 / KOL占比变化-pp
   曾经加过「SKU订单数 / 平均下单成本 / 达人视频GMV」三列，用户明确要求去掉。

数据来源：
  · 左侧成本/收入 → 商家中心 › 营销 › 店铺广告 › 广告计划数据分析（GMV-MAX 商品卡），
    每条计划逐个截图「概览」卡片（成本 / 总收入 / ROI），窗口设成报告周期。
  · 右侧 KOL/KOC → 先跑 kol_koc.py，把它打印的两期占比填进下面的 R 表。

🔴 这是**商品卡口径**，与周报主口径的直播 campaign 是两套投放，成本与收入都不可相加。
🔴 品线归属（红系抗老 / 白系美白）要跟 Step11 单链接表的品线口径保持一致。
"""
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter
NAVY='1F3864'; BLUE_H='BDD7EE'; ORANGE_H='FBE5D6'; GREEN_H='E2EFDA'; KK_H='FFF2CC'
RED='C00000'; GREEN='00B050'; YEL='FFF2CC'
TH=Side(style='thin',color='9DA6B0'); BD=Border(left=TH,right=TH,top=TH,bottom=TH)
P1='周期1：2026-08-03 ~ 08-09'   # 每期改
P2='周期2：2026-08-10 ~ 08-16'   # 每期改
# (名称, 品线, 上期成本, 上期收入, 本期成本, 本期收入, 上期KOL占比, 本期KOL占比, 上期达人GMV, 本期达人GMV)
R=[('MKT-白精华-0708','白系',94052,332926,72466,256468,0.6432,0.6262,199631,129909),
   ('MKT-素颜霜-0708','白系',31315,102787,34874,111643,0.5570,0.6053, 66372, 50046),
   ('MKT-红精华-0708','红系',21933, 67432,23383, 73119,0.3138,0.4090, 51036, 48311),
   ('OL-白精华single-0715','白系',2324,12142, 2089, 10211,0.3532,0.1483,  4359,  2438),
   ('MKT-红洁面-0708','红系',1362,  4070, 1503,  4429,0.0000,0.0000,  1743,  1163),
   ('MKT-红面霜-0803','红系',928,   1695, 1531,  3584,  None,  None,     0,     0),
   ('OL-红精华single-0722','红系',825,3119,  875,  3248,0.0000,0.0000,  1043,  1403)]
R.sort(key=lambda x:-x[5])
NC=15
wb=openpyxl.Workbook(); ws=wb.active; ws.title='GMV-MAX商品卡'
ws.cell(row=1,column=1,value='').fill=PatternFill('solid',fgColor=NAVY)
def band(a,b,t):
    ws.merge_cells(start_row=1,start_column=a,end_row=1,end_column=b)
    c=ws.cell(row=1,column=a,value=t); c.fill=PatternFill('solid',fgColor=NAVY)
    c.font=Font(bold=True,color='FFFFFF',size=11); c.alignment=Alignment(horizontal='center',vertical='center')
band(2,4,P1); band(5,7,P2); band(8,10,'环比变化'); band(11,15,'达人视频 KOL/KOC（两期对比）')
ws.row_dimensions[1].height=22; ws.row_dimensions[2].height=32
H=[('广告计划名称','D9D9D9'),('成本(¥)',BLUE_H),('收入(¥)',BLUE_H),('ROI',BLUE_H),
   ('成本(¥)',ORANGE_H),('收入(¥)',ORANGE_H),('ROI',ORANGE_H),
   ('成本环比',GREEN_H),('收入环比',GREEN_H),('ROI变化-pp',GREEN_H),
   ('上期KOL占比',KK_H),('上期KOC占比',KK_H),('本期KOL占比',KK_H),('本期KOC占比',KK_H),('KOL占比变化-pp',KK_H)]
for i,(t,f) in enumerate(H,1):
    c=ws.cell(row=2,column=i,value=t); c.fill=PatternFill('solid',fgColor=f)
    c.font=Font(bold=True,size=10); c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); c.border=BD
r=3
def put(name,pc,pr_,cc_,cr,pk,ck,bold=False,fill=None):
    global r
    proi=pr_/pc if pc else None; croi=cr/cc_ if cc_ else None
    vals=[name,pc,pr_,proi,cc_,cr,croi,
          (cc_/pc-1) if pc else None,(cr/pr_-1) if pr_ else None,(croi-proi) if (proi and croi) else None,
          pk,(1-pk) if pk is not None else None,ck,(1-ck) if ck is not None else None,
          ((ck-pk)*100) if (pk is not None and ck is not None) else None]
    for j,v in enumerate(vals,1):
        c=ws.cell(row=r,column=j,value=v); c.border=BD
        if j in (2,3,5,6): c.number_format='#,##0'
        if j in (4,7): c.number_format='0.00'
        if j in (8,9):
            c.number_format='0.00%'
            if isinstance(v,float): c.font=Font(color=RED if v>0 else GREEN,bold=bold)
        if j==10:
            c.number_format='+0.00;-0.00;0.00'
            if isinstance(v,float): c.font=Font(color=RED if v>0 else GREEN,bold=bold)
        if j in (11,12,13,14): c.number_format='0.00%'
        if j==15:
            c.number_format='+0.0"pp";-0.0"pp";0.0"pp"'
            if isinstance(v,float): c.font=Font(color=RED if v>0 else GREEN,bold=bold)
        if j>1: c.alignment=Alignment(horizontal='center')
        if bold and j not in (8,9,10,15): c.font=Font(bold=True)
        if fill: c.fill=PatternFill('solid',fgColor=fill)
    r+=1
S=lambda i,sel=None: sum(x[i] for x in R if sel is None or x[1]==sel)
def wk(idx_rate,idx_gmv,sel=None):
    P=[x for x in R if (sel is None or x[1]==sel) and x[idx_gmv]]
    g=sum(x[idx_gmv] for x in P)
    return (sum((x[idx_rate] or 0)*x[idx_gmv] for x in P)/g) if g else None
for n,line,pc,pr_,cc_,cr,pk,ck,pa,ca in R:
    put(n,pc,pr_,cc_,cr,pk,ck,fill=YEL if line=='红系' else None)
put('合计 / 加权',S(2),S(3),S(4),S(5),wk(6,8),wk(7,9),bold=True,fill='D9E1F2')
r+=1
ws.cell(row=r,column=1,value='按品线拆（红系 = 红精华 / 红洁面 / 红面霜 / 红精华single；白系 = 白精华 / 素颜霜 / 白精华single）')
ws.cell(row=r,column=1).font=Font(bold=True,color=RED)
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC); r+=1
for lb in ['白系','红系']:
    put(f'{lb}小计',S(2,lb),S(3,lb),S(4,lb),S(5,lb),wk(6,8,lb),wk(7,9,lb),bold=True,fill='E2F3F2' if lb=='红系' else 'F2F2F2')
r+=1
NOTE=[
 '🔴【KOL/KOC 与左侧不是一套口径】末五列来自 affiliate_orders 导出（两期各一份，内容形式全部为「视频」），是**达人视频渠道**成交；左侧成本/收入是 GMV-MAX 商品卡投放。两者不可相加，这里只是把同一商品ID 的达人结构贴旁边看。',
 '【判定方式】付费达人清单（去重 610 个用户名）匹配 affiliate_orders 的「达人用户名」：命中即 KOL，其余全部 KOC。金额用「支付金额」÷3,890 折 RMB，已剔除订单状态=客户未付款（本期 606 行 / 上期 18 行）。合计与小计行的 KOL/KOC 为**按达人 GMV 加权**，不是各行简单平均。',
 '🟡【同一份清单套两期】清单是当前累计签约名单。若期间有新签，上期 KOL 占比会被高估。两期匹配率几乎一致（本期 346 人命中 159 = 46.0%，上期 355 人命中 164 = 46.2%），占比可比性没问题，绝对值可能整体偏高。',
 '🟢【核心发现一 · 红系达人盘最抗跌】达人视频 GMV 整体 32.42 万 → 23.33 万元（−28.0%），其中白系 −32.5%、红系仅 −5.5%；红精华 single 逆势 +34.5%。',
 '🟢【核心发现二 · 付费达人正在往红系倾斜】红系 KOL 占比 29.8% → 38.8%（+9.1pp），红精华 31.4% → 40.9%（+9.5pp）；白系 61.7% → 61.4% 基本不动。与商品卡投放「红系成本 +9.0% / 白系 −14.3%」是同一个动作的两个侧面。',
 '🔴【问题项】OL-白精华single-0715：达人 GMV −44.1%、KOL 占比 −20.5pp（全表最大跌幅），同时商品卡成本 −10.1%、ROI 4.89 仍是全表最高。**投放端和达人端同时在砍最优质的资产。**',
 '🟡【合计行是假象】整体 KOL 占比 56.4% → 56.5% 看着没动，拆开是「白系稳、红系 +9.1pp」。总量不动不代表结构不动，别只看合计行。',
 '⚠️ MKT-红面霜-0803 两期均无达人视频订单，KOL/KOC 留空（不是 0%）。另有本期 4 个商品 2,617 元、上期 3 个商品 2,404 元的达人 GMV 不属于这 7 条计划，已排除，对合计分母影响 <1.1%。',
 '【口径 PS】ROI = 收入 ÷ 成本。ROI变化 与 KOL占比变化 为 pp（绝对差），不是百分比。黄底 = 红系抗老计划。环比配色 红=↑ 绿=↓。左侧金额为平台原生 ¥ 显示值。',
]
for t in NOTE:
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC)
    c=ws.cell(row=r,column=1,value=t); c.fill=PatternFill('solid',fgColor='DDEBF7')
    c.font=Font(size=9,color='1F4E79'); c.alignment=Alignment(wrap_text=True,vertical='center')
    ws.row_dimensions[r].height=30 if len(t)>100 else 16
    r+=1
for i,w in enumerate([24,11,12,8,11,12,8,11,11,12,12,12,12,12,13],1): ws.column_dimensions[get_column_letter(i)].width=w
ws.freeze_panes='B3'
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, OUT
wb.save(f'{OUT}/KANS_VN_{PERIOD}_GMV-MAX商品卡对比.xlsx')
print('ok  上期KOL加权',round(wk(6,8),4),'本期',round(wk(7,9),4))
for lb in ['白系','红系']: print(lb,round(wk(6,8,lb),4),'→',round(wk(7,9,lb),4))
