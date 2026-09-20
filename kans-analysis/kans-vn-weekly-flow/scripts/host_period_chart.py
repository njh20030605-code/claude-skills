# -*- coding: utf-8 -*-
"""Step12 · 主播 × 时段 对比（只本期，4 指标：GMV / ROI / UV价值 / 单小时产出）

用途：回答「这个时段该派谁」—— 排班决策直接看这张。
输入：period_host.csv（由 host_periods.py 生成）

🔴 固定形态（用户确认过，别改）：
  1. **按时段分组**，不是按主播分组 —— 排班是按班次决策的。
  2. 每个时段一个黄底分组头，头里写「本班 GMV / ROI / 单h / 时长」。
  3. 组内按 GMV 降序；GMV 用横向红条 + 数值。
  4. **ROI 与单小时产出按「是否优于本班加权」着色**：绿 = 优于、红 = 低于。
     UV 不着色（没有天然对照基准）。
  5. **绿底行 = ROI 与单小时产出双双优于本班加权 → 标「该班最优解」**，这是排班要抓的格子。
  6. **时长 <3h 的行淡显 + 标「样本不足 <3h」**，不进排班决策（2h 的 ROI 6.18 没有参考性）。
  7. **单人班次（solo）不着色** —— 本班加权就是他自己，红绿无意义。
  8. 只出本期，不做环比 —— 环比看 step12_charts.py 那两张。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, W2L, OUT, SKILL_CHART
sys.path.insert(0, SKILL_CHART)
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import common as C
REG,BLK=C.setup_cjk_font()
BAR='#C0392B'; GOOD='#1A8A78'; BAD='#C0392B'; GREY,INK='#8A929B','#23303D'
ORDER=['早班 06-10','午班 10-14','下午 14-18','晚班 18-22','夜班 22-02','凌晨 02-06']
ph=pd.read_csv(f'{OUT}/period_host.csv')
ph['period']=pd.Categorical(ph.period,ORDER,ordered=True)

# ---------- 图 A：按时段分组的横向表 ----------
X_NAME=1.0; BX0,BX1=13.5,32.0; X_GMV=41.0; X_ROI=52.0; X_UV=63.0; X_H=76.0; X_DUR=90.0; X_TAG=93.5
gmax=ph.GMV万.max()
bx=lambda v: BX0+v/(gmax*1.03)*(BX1-BX0)
ROWS=[]
for p in ORDER:
    sub=ph[ph.period==p].sort_values('GMV万',ascending=False)
    if not len(sub): continue
    ROWS.append(('SEC',p,sub))
    for _,x in sub.iterrows(): ROWS.append(('R',p,x))
    ROWS.append(('T',p,sub))
n_eff=sum(1 for k,_,_ in ROWS if k!='T')+0.35*sum(1 for k,_,_ in ROWS if k=='T')
fig,ax=plt.subplots(figsize=(17.2,0.62*n_eff+3.2),dpi=150)
ax.set_xlim(0,100); ax.set_ylim(n_eff+0.2,-2.0); ax.axis('off')
ax.add_patch(Rectangle((X_NAME-0.6,-1.75),98.6-X_NAME,1.6,fc='#F4F6F8',ec='none',zorder=0))
ax.text((BX0+BX1)/2,-1.35,'GMV（万元）',ha='center',va='center',fontsize=12.5,fontproperties=BLK,color=INK)
for x,t,ha in [(X_GMV,'GMV 万元','right'),(X_ROI,'ROI','right'),(X_UV,'UV价值 元','right'),
               (X_H,'单小时产出 元/h','right'),(X_DUR,'时长 h','right')]:
    ax.text(x,-1.35,t,ha=ha,va='center',fontsize=12.5,fontproperties=BLK,color=INK)
ax.text(X_TAG,-1.35,'判定',ha='left',va='center',fontsize=12.5,fontproperties=BLK,color=INK)
ax.plot([X_NAME-0.6,98.0],[-0.12,-0.12],color='#C9D2DA',lw=1.2)
y=0
for kind,p,item in ROWS:
    if kind=='SEC':
        tg,ts,th=item.GMV万.sum(),item.消耗万.sum(),item.时长.sum()
        ax.add_patch(Rectangle((X_NAME-0.6,y-0.44),98.6-X_NAME,0.88,fc='#FFF6DC',ec='none',zorder=0))
        ax.text(X_NAME,y,p,ha='left',va='center',fontsize=13.2,fontproperties=BLK,color='#B9560F')
        ax.text(X_NAME+12.0,y,f'本班 GMV {tg:.2f}万 · ROI {tg/ts:.2f} · 单h {tg*1e4/th:,.0f}元 · {th:.0f}h',
                ha='left',va='center',fontsize=10.4,color='#8A6D1F')
        y+=1; continue
    if kind=='T':
        y+=0.35; continue
    x=item
    sub=ph[ph.period==p]
    band_roi=sub.GMV万.sum()/sub.消耗万.sum(); band_h=sub.GMV万.sum()*1e4/sub.时长.sum()
    small=x.时长<3
    dbl = (x.ROI>band_roi) and (x.单h>band_h) and not small and len(sub)>1
    if dbl: ax.add_patch(Rectangle((X_NAME-0.6,y-0.42),98.6-X_NAME,0.84,fc='#E8F6F1',ec='none',zorder=0))
    ax.text(X_NAME+1.6,y,x.host,ha='left',va='center',fontsize=12.4,color=INK,fontproperties=BLK if dbl else None)
    ax.add_patch(Rectangle((BX0,y-0.17),max(bx(x.GMV万)-BX0,0.001),0.34,fc=BAR,ec='none',zorder=3,alpha=0.55 if small else 1.0))
    ax.text(X_GMV,y,f'{x.GMV万:.3f}',ha='right',va='center',fontsize=11.6,fontproperties=BLK,color=INK)
    solo = len(sub)==1          # 单人班次：本班加权 = 他自己，配色无意义
    for xx,v,f,ref in [(X_ROI,x.ROI,'{:.2f}',band_roi),(X_UV,x.UV,'{:.3f}',None),(X_H,x.单h,'{:,.0f}',band_h)]:
        col=INK
        if ref is not None and not small and not solo: col=GOOD if v>ref else BAD
        ax.text(xx,y,f.format(v),ha='right',va='center',fontsize=11.6,color=col,
                fontproperties=BLK if (ref is not None and not small and not solo and v>ref) else None)
    ax.text(X_DUR,y,f'{x.时长:.0f}',ha='right',va='center',fontsize=11.2,color=GREY if small else INK)
    if small: ax.text(X_TAG,y,'样本不足 <3h',ha='left',va='center',fontsize=9.6,color='#9E9E9E')
    elif dbl:  ax.text(X_TAG,y,'该班最优解',ha='left',va='center',fontsize=10,color=GOOD,fontproperties=BLK)
    y+=1
fig.suptitle(f'KANS 越南 SKINCARE 直播间 · 不同主播 × 不同时段（本期 {W2L}）',
             fontsize=16.5,fontproperties=BLK,y=1-0.30/fig.get_figheight(),color=INK)
fig.text(0.5,1-0.66/fig.get_figheight(),
         '每个时段内按 GMV 降序；绿 = 优于本班加权，红 = 低于本班加权；绿底行 = ROI 与单小时产出双双优于本班 → 该时段最该派的人',
         ha='center',fontsize=12.2,fontproperties=BLK,color='#B9560F')
fig.text(0.5,0.016,
 '数据源：2026 REPORT PERFORMANCE｜KANS › Tháng 08 | SKINCARE　│　GMV / 消耗取 GMV Host、Spend Ads Host 原生列，VND ÷ 3,890 → RMB　│　'
 '跨班次直播段按小时重叠拆分、按时长比例分摊 GMV / 消耗 / 观看　│　UV价值 = GMV元 ÷ Views　│　单小时产出 = GMV元 ÷ 时长　│　时长 <3h 的格子仅供参考，不进排班决策',
 ha='center',fontsize=9.8,color=GREY)
plt.subplots_adjust(top=1-1.05/fig.get_figheight(),bottom=0.045,left=0.012,right=0.988)
fig.savefig(f'{OUT}/KANS_VN_{PERIOD}_Step12_主播×时段对比.png',dpi=150,facecolor='white',bbox_inches='tight')
plt.close(fig)
print('A ok', n_eff)
