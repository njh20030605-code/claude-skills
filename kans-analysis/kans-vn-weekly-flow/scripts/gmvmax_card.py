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
🔴 品线归属（如 红系抗老 / 白系美白）要跟 Step11 单链接表的品线口径保持一致。

用法：python3 gmvmax_card.py   （不依赖外部文件；每期只改下面的参数块）
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, W1, W2, VND, OUT, FILE_PREFIX
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter

# ======================= 参数块（每期改这里） =======================
P1=f'周期1：{W1[0]} ~ {W1[1][5:]}'
P2=f'周期2：{W2[0]} ~ {W2[1][5:]}'
# 品线名（两条即可；与 Step11 保持一致）
LINE_A, LINE_B = '白系', '红系'
# (名称, 品线, 上期成本, 上期收入, 本期成本, 本期收入, 上期KOL占比, 本期KOL占比, 上期达人GMV, 本期达人GMV)
# 示例数据：换成你自己的导出（KOL 占比两期都无达人订单时填 None，脚本会留空不写 0%）
R=[('商品卡计划-A', LINE_A, 90000, 320000, 75000, 260000, 0.64, 0.62, 200000, 130000),
   ('商品卡计划-B', LINE_A, 30000, 100000, 35000, 110000, 0.56, 0.60,  65000,  50000),
   ('商品卡计划-C', LINE_B, 22000,  68000, 23000,  73000, 0.31, 0.41,  50000,  48000),
   ('商品卡计划-D', LINE_A,  2300,  12000,  2100,  10000, 0.35, 0.15,   4400,   2400),
   ('商品卡计划-E', LINE_B,  1400,   4000,  1500,   4400, 0.00, 0.00,   1700,   1200),
   ('商品卡计划-F', LINE_B,   900,   1700,  1500,   3600,  None,  None,      0,      0),
   ('商品卡计划-G', LINE_B,   800,   3100,   900,   3200, 0.00, 0.00,   1000,   1400)]
KOL_LIST_N = 600            # 付费达人清单去重后人数（kol_koc.py 会打印）
UNPAID_ROWS = ('本期 N 行 / 上期 M 行')   # 剔除「客户未付款」的行数，kol_koc.py 会打印
MATCH_NOTE  = '本期 A 人命中 B = X%，上期 C 人命中 D = Y%'   # 两期匹配率，kol_koc.py 会打印
# 结论文案：每期按本期方向重写，下面只是形态模板
FINDINGS=[
 f'🟢【核心发现一】达人视频 GMV 整体 A → B 万元（±X%），其中{LINE_A} ±X%、{LINE_B} ±X%；<某计划>逆势 ±X%。',
 f'🟢【核心发现二】付费达人是否在往某品线倾斜：{LINE_B} KOL 占比 X% → Y%（±Zpp）；与商品卡投放「{LINE_B}成本 ±X% / {LINE_A} ±Y%」是否同向。',
 '🔴【问题项】<计划名>：达人 GMV ±X%、KOL 占比 ±Ypp（全表最大跌幅），同时商品卡成本 ±Z%、ROI 仍是全表最高 —— 投放端和达人端是否同时在砍最优质的资产。',
 '🟡【合计行是假象】整体 KOL 占比 X% → Y% 看着没动，拆开是「一条线稳、另一条 ±Zpp」。总量不动不代表结构不动，别只看合计行。',
]
# =====================================================================

NAVY='1F3864'; BLUE_H='BDD7EE'; ORANGE_H='FBE5D6'; GREEN_H='E2EFDA'; KK_H='FFF2CC'
RED='C00000'; GREEN='00B050'; YEL='FFF2CC'
TH=Side(style='thin',color='9DA6B0'); BD=Border(left=TH,right=TH,top=TH,bottom=TH)
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
    """KOL 占比按达人 GMV 加权（铁律：不能用成本/收入/行数当权重）"""
    P=[x for x in R if (sel is None or x[1]==sel) and x[idx_gmv]]
    g=sum(x[idx_gmv] for x in P)
    return (sum((x[idx_rate] or 0)*x[idx_gmv] for x in P)/g) if g else None
for n,line,pc,pr_,cc_,cr,pk,ck,pa,ca in R:
    put(n,pc,pr_,cc_,cr,pk,ck,fill=YEL if line==LINE_B else None)
put('合计 / 加权',S(2),S(3),S(4),S(5),wk(6,8),wk(7,9),bold=True,fill='D9E1F2')
r+=1
_members=lambda ln: ' / '.join(x[0] for x in R if x[1]==ln)
ws.cell(row=r,column=1,value=f'按品线拆（{LINE_B} = {_members(LINE_B)}；{LINE_A} = {_members(LINE_A)}）')
ws.cell(row=r,column=1).font=Font(bold=True,color=RED)
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC); r+=1
for lb in [LINE_A,LINE_B]:
    put(f'{lb}小计',S(2,lb),S(3,lb),S(4,lb),S(5,lb),wk(6,8,lb),wk(7,9,lb),bold=True,fill='E2F3F2' if lb==LINE_B else 'F2F2F2')
r+=1
_blank=[x[0] for x in R if x[6] is None and x[7] is None]
NOTE=[
 '🔴【KOL/KOC 与左侧不是一套口径】末五列来自 affiliate_orders 导出（两期各一份，内容形式全部为「视频」），是**达人视频渠道**成交；左侧成本/收入是 GMV-MAX 商品卡投放。两者不可相加，这里只是把同一商品ID 的达人结构贴旁边看。',
 f'【判定方式】付费达人清单（去重 {KOL_LIST_N} 个用户名）匹配 affiliate_orders 的「达人用户名」：命中即 KOL，其余全部 KOC。金额用「支付金额」÷{VND:,.0f} 折 RMB，已剔除订单状态=客户未付款（{UNPAID_ROWS}）。合计与小计行的 KOL/KOC 为**按达人 GMV 加权**，不是各行简单平均。',
 f'🟡【同一份清单套两期】清单是当前累计签约名单。若期间有新签，上期 KOL 占比会被高估。两期匹配率（{MATCH_NOTE}）接近才说明占比可比，绝对值可能整体偏高。',
 *FINDINGS,
 (f'⚠️ {" / ".join(_blank)} 两期均无达人视频订单，KOL/KOC 留空（不是 0%）。' if _blank else '')+'不属于上表计划的达人 GMV 已排除，需在此写明对合计分母的影响（<X%）。',
 f'【口径 PS】ROI = 收入 ÷ 成本。ROI变化 与 KOL占比变化 为 pp（绝对差），不是百分比。黄底 = {LINE_B}计划。环比配色 红=↑ 绿=↓。左侧金额为平台原生 ¥ 显示值。',
]
for t in NOTE:
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=NC)
    c=ws.cell(row=r,column=1,value=t); c.fill=PatternFill('solid',fgColor='DDEBF7')
    c.font=Font(size=9,color='1F4E79'); c.alignment=Alignment(wrap_text=True,vertical='center')
    ws.row_dimensions[r].height=30 if len(t)>100 else 16
    r+=1
for i,w in enumerate([24,11,12,8,11,12,8,11,11,12,12,12,12,12,13],1): ws.column_dimensions[get_column_letter(i)].width=w
ws.freeze_panes='B3'
p=f'{OUT}/{FILE_PREFIX}_{PERIOD}_GMV-MAX商品卡对比.xlsx'
wb.save(p); print('saved',p)
print('ok  上期KOL加权',round(wk(6,8),4),'本期',round(wk(7,9),4))
for lb in [LINE_A,LINE_B]: print(lb,round(wk(6,8,lb),4),'→',round(wk(7,9,lb),4))
