# -*- coding: utf-8 -*-
"""Step12 两张横向对比图：① 主播排名  ② 时段数据（6 班次）

每期改下面两行副标题即可；其余从 _config.py 读。
表格式横向条形：左 GMV 双色条，右侧 GMV万/环比/ROI/单h/UV/时长 各列都写 上期 → 本期。
"""
SUB_HOST  = '两期均为纯平销周，GMV 环比无大促基数干扰；但 GMV 排序主要由排班时长决定，主播能力看 ROI / 单h GMV / UV 三项效率口径'
SUB_SHIFT = '跨班次直播段按小时重叠拆分、按时长比例分摊 GMV / 消耗 / 观看；两期均为纯平销周，无需剔大促口径'
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, W1L, W2L, OUT
sys.path.insert(0, __import__('_config').SKILL_CHART)
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import common as C
REG,BLK=C.setup_cjk_font()
C_A,C_B='#9FB6CD','#C0392B'; UP,DN='#C0392B','#1A8A78'; GREY,INK='#8A929B','#23303D'
PREV_L,CUR_L=f'上期 {W1L}',f'本期 {W2L}'
ORDER=['早班 06-10','午班 10-14','下午 14-18','晚班 18-22','夜班 22-02','凌晨 02-06']

pk=pd.read_csv(f'{OUT}/host_pk.csv'); pk.columns=['wk','host','场次','时长','GMV万','消耗万','ROI','单h','UV']
per=pd.read_csv(f'{OUT}/period.csv',index_col=0).reindex(ORDER)
ph=pd.read_csv(f'{OUT}/period_host.csv')
prev=pk[pk.wk=='上期'].set_index('host'); curr=pk[pk.wk=='本期'].set_index('host')
# 加权 UV = 总GMV元 ÷ 总Views（不能对各主播 UV 取算术平均）
def _wuv(df):
    views = (df['GMV万'] * 1e4 / df['UV']).sum()
    return df['GMV万'].sum() * 1e4 / views
PREV_UV, CUR_UV = _wuv(prev), _wuv(curr)

def rec(s):
    if s is None: return None
    return dict(gmv=s['GMV万']*1e4,roi=s['ROI'],gph=s['单h'],uv=s['UV'],h=s['时长'])

HOSTS=[]
for h in curr.sort_values('GMV万',ascending=False).index:
    HOSTS.append(dict(name=h,prev=rec(prev.loc[h]) if h in prev.index else None,cur=rec(curr.loc[h])))
gp=prev[['GMV万','消耗万','时长']].sum(); gc=curr[['GMV万','消耗万','时长']].sum()
TOT=dict(prev=dict(gmv=gp['GMV万']*1e4,roi=gp['GMV万']/gp['消耗万'],gph=gp['GMV万']*1e4/gp['时长'],uv=PREV_UV,h=gp['时长']),
         cur=dict(gmv=gc['GMV万']*1e4,roi=gc['GMV万']/gc['消耗万'],gph=gc['GMV万']*1e4/gc['时长'],uv=CUR_UV,h=gc['时长']))
SHIFTS=[]
for p in ORDER:
    x=per.loc[p]
    pv=None if x['上期·GMV万']!=x['上期·GMV万'] else dict(gmv=x['上期·GMV万']*1e4,roi=x['上期·ROI'],gph=x['上期·单h'],uv=x['上期·UV'],h=x['上期·时长'])
    cv=dict(gmv=x['本期·GMV万']*1e4,roi=x['本期·ROI'],gph=x['本期·单h'],uv=x['本期·UV'],h=x['本期·时长'])
    top=list(ph[ph.period==p].nlargest(2,'GMV万').host)
    SHIFTS.append(dict(name=p,prev=pv,cur=cv,top=top))

X_NAME=1.0; BX0,BX1=13.0,34.0; X_GMV=45.0; X_CHG=55.5; X_ROI=64.5; X_GPH=76.0; X_UV=85.5; X_H=95.5
def fmt(v,k):
    if v is None: return '—'
    return {'gmv':f'{(v or 0)/1e4:.2f}','roi':f'{v:.2f}','gph':f'{v:,.0f}','uv':f'{v:.2f}','h':f'{v:.0f}'}[k]

def render(items,title,sub_title,fname,band_color,section,total=None,note=''):
    gmax=max([i['cur']['gmv']/1e4 for i in items]+[i['prev']['gmv']/1e4 for i in items if i['prev']]
             +([total['cur']['gmv']/1e4] if False else []))
    bx=lambda v: BX0+v/(gmax*1.02)*(BX1-BX0)
    ROWS=[('SEC',section)]+[('R',i) for i in items]+([('T',total)] if total else [])
    n=len(ROWS)
    fig,ax=plt.subplots(figsize=(16.6,0.78*n+3.2),dpi=150)
    ax.set_xlim(0,100); ax.set_ylim(n+0.4,-1.9); ax.axis('off')
    ax.add_patch(Rectangle((X_NAME-0.6,-1.62),99.6-X_NAME,1.5,fc='#F4F6F8',ec='none',zorder=0))
    ax.text((BX0+BX1)/2,-1.30,'GMV（万元）',ha='center',va='center',fontsize=12.5,fontproperties=BLK,color=INK)
    for x,t in [(X_GMV,'GMV 万元'),(X_CHG,'环比'),(X_ROI,'ROI'),(X_GPH,'单h GMV 元'),(X_UV,'UV价值 元'),(X_H,'时长 h')]:
        ax.text(x,-1.30,t,ha='right' if x in (X_CHG,X_H,X_UV,X_GPH) else 'center',va='center',fontsize=12.5,fontproperties=BLK,color=INK)
    ax.text(X_GMV,-0.62,'上期 → 本期',ha='center',va='center',fontsize=10,color=GREY)
    for x in (X_ROI,X_GPH,X_UV,X_H):
        ax.text(x,-0.62,'上期 → 本期',ha='right' if x!=X_ROI else 'center',va='center',fontsize=10,color=GREY)
    ax.plot([X_NAME-0.6,99.0],[-0.10,-0.10],color='#C9D2DA',lw=1.2)
    ax.legend([Rectangle((0,0),1,1,fc=C_A),Rectangle((0,0),1,1,fc=C_B)],[PREV_L,CUR_L],
              loc='upper left',bbox_to_anchor=(0.005,1.035),ncol=2,frameon=False,fontsize=11)
    def draw(y,name,prev,cur,bold=False,band=None,sub=None,bars=True):
        if band: ax.add_patch(Rectangle((X_NAME-0.6,y-0.44),99.6-X_NAME,0.88,fc=band,ec='none',zorder=0))
        ax.text(X_NAME,y if not sub else y-0.16,name,ha='left',va='center',
                fontsize=12.6 if bold else 12.2,color=INK,fontproperties=BLK if bold else None)
        if sub: ax.text(X_NAME,y+0.22,sub,ha='left',va='center',fontsize=9.6,color=GREY)
        if bars:
            gpv=prev['gmv']/1e4 if prev else 0; gcv=cur['gmv']/1e4
            ax.add_patch(Rectangle((BX0,y-0.34),max(bx(gpv)-BX0,0.001),0.30,fc=C_A,ec='none',zorder=3))
            ax.add_patch(Rectangle((BX0,y+0.04),bx(gcv)-BX0,0.30,fc=C_B,ec='none',zorder=3))
        ax.text(X_GMV,y,f'{fmt(prev["gmv"] if prev else None,"gmv")}  →  {fmt(cur["gmv"],"gmv")}',
                ha='center',va='center',fontsize=11.6,color=INK,fontproperties=BLK)
        if prev and prev['gmv']:
            v=(cur['gmv']/prev['gmv']-1)*100
            ax.text(X_CHG,y,f'{v:+.0f}%',ha='right',va='center',fontsize=11.6,fontproperties=BLK,color=UP if v>0 else DN)
        else:
            ax.text(X_CHG,y,'新增',ha='right',va='center',fontsize=11,fontproperties=BLK,color='#B7950B')
        for x,key,ha in [(X_ROI,'roi','center'),(X_GPH,'gph','right'),(X_UV,'uv','right'),(X_H,'h','right')]:
            a=prev.get(key) if prev else None
            ax.text(x,y,f'{fmt(a,key)} → {fmt(cur.get(key),key)}',ha=ha,va='center',fontsize=11.2,color=INK)
    y=0
    for kind,it in ROWS:
        if kind=='SEC':
            ax.text(X_NAME,y,it,ha='left',va='center',fontsize=13.5,fontproperties=BLK,color=UP)
            ax.plot([X_NAME,99.0],[y+0.46,y+0.46],color='#F0C9C4',lw=1.1); y+=1; continue
        if kind=='T':
            draw(y,'合计 / 加权',it['prev'],it['cur'],bold=True,band='#D9E1F2',bars=False)
        else:
            draw(y,it['name'],it['prev'],it['cur'],band=band_color,
                 sub=('主力：'+' / '.join(it['top']) if it.get('top') else None))
        y+=1
    H=fig.get_figheight()
    fig.suptitle(title,fontsize=16.5,fontproperties=BLK,y=1-0.30/H,color=INK)
    if sub_title: fig.text(0.5,1-0.68/H,sub_title,ha='center',fontsize=12.6,fontproperties=BLK,color=UP)
    fig.text(0.5,0.018,note,ha='center',fontsize=10,color=GREY)
    plt.subplots_adjust(top=1-1.05/H,bottom=0.05,left=0.012,right=0.988)
    fig.savefig(f'{OUT}/{fname}',dpi=150,facecolor='white',bbox_inches='tight')
    plt.close(fig)

FOOT=('数据源：2026 REPORT PERFORMANCE｜KANS › Tháng 08 | SKINCARE　│　GMV / 消耗取 GMV Host、Spend Ads Host 原生列　│　'
      'VND ÷ 3,890 → RMB　│　00:00–05:59 跨夜段归前一直播日　│　UV价值 = GMV元 ÷ Views　│　已剔除每日末尾 #N/A 平衡行')
render(HOSTS,
       f'KANS 越南 SKINCARE 直播间 · 主播排名｜本期 {W2L} vs 上期 {W1L}',
       SUB_HOST,
       f'KANS_VN_{PERIOD}_Step12_主播排名.png',None,'① 主播排名（按本期 GMV 降序）',total=TOT,note=FOOT)
render(SHIFTS,
       f'KANS 越南 SKINCARE 直播间 · 时段数据（6 班次）｜本期 {W2L} vs 上期 {W1L}',
       SUB_SHIFT,
       f'KANS_VN_{PERIOD}_Step12_时段数据.png','#FFF6DC','② 时段数据（6 班次）',total=None,
       note=FOOT+'　│　时段「主力」= 本期该班 GMV 前 2')
print('ok')
