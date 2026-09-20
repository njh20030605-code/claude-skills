# -*- coding: utf-8 -*-
import json, numpy as np, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, W1L, W2L, OUT, SKILL_CHART
sys.path.insert(0,SKILL_CHART)
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import common as C
REG,BLK=C.setup_cjk_font(); P=C.PALETTE
T=json.load(open(f'{OUT}/ts.json')); cur,prev=T['cur'],T['prev']
K=['Search','推荐','其他']
CP,CC='#9FB6CD','#C0392B'
PAN=[('观看占比','view_share','%',False),('成交占比','gmv_share','%',False),
     ('进房率 = 观看÷曝光（对数轴）','tap','%',True),('CTOR（点击加权）','ctor','%',False)]
fig,axes=plt.subplots(1,4,figsize=(21,7.6),dpi=150)
x=np.arange(3); w=0.36
for ax,(t,key,unit,logy) in zip(axes,PAN):
    a=[prev[k][key]*100 for k in K]; b=[cur[k][key]*100 for k in K]
    ax.bar(x-w/2,a,w,color=CP,zorder=3,label=W1L)
    ax.bar(x+w/2,b,w,color=CC,zorder=3,label=W2L)
    if logy: ax.set_yscale('log')
    top=max(max(a),max(b))
    for xi,v in zip(x-w/2,a):
        ax.text(xi,v*0.955 if logy else v-top*0.018,f'{v:.2f}%',ha='center',va='top',fontsize=10.2,
                color='white',fontweight='bold')
    for xi,v,va_ in zip(x+w/2,b,a):
        d=(v-va_)
        ax.text(xi,v*1.06 if logy else v+top*0.02,f'{v:.2f}%',ha='center',va='bottom',fontsize=10.8,color=CC,fontweight='bold')
        ax.text(xi,(v*1.30 if logy else v+top*0.085),f'{d:+.2f}pp',ha='center',va='bottom',fontsize=9.6,
                color=('#C0392B' if d>0 else '#00875A'),fontweight='bold')
    if not logy: ax.set_ylim(0,top*1.30)
    else: ax.set_ylim(min(min(a),min(b))*0.45, top*2.4)
    ax.set_xticks(x); ax.set_xticklabels(K,fontsize=12)
    ax.set_title(t,fontsize=13.5,fontproperties=BLK,color='#1B2733',pad=12)
    ax.grid(axis='y',color=P['grid'],lw=0.9,zorder=0)
    C.style_axes(ax)
H=fig.get_figheight()
fig.suptitle(f'Step9 · 流量入口结构｜本期 {W2L[3:]} vs 上期 {W1L[3:]}（红=↑ / 绿=↓，与全套报告统一）',
             fontsize=18,fontproperties=BLK,x=0.035,ha='left',y=1-0.30/H)
fig.text(0.035,1-0.66/H,'分组：推荐 = For You feed + LIVE feed｜其他 = Shop tab + Inbox + Other channels + Following｜CTOR 点击加权',
         fontsize=11.5,color='#6B7785',va='center')
fig.legend(handles=[Patch(fc=CP,label=f'上期 {W1L[3:]}'),Patch(fc=CC,label=f'本期 {W2L[3:]}')],
           loc='upper right',bbox_to_anchor=(0.985,1-0.34/H),ncol=2,frameon=False,fontsize=12)
plt.subplots_adjust(top=1-1.32/H,bottom=0.175,left=0.045,right=0.985,wspace=0.24)
fig.text(0.035,0.085,'数据源 Creator-Live-Traffic-Source 导出（两期各一份）｜成交 GMV = Attributed GMV ÷ 3,890｜点击 ≈ 观看 × CTR',
         fontsize=10.5,color=P['ann_grey'])
fig.text(0.035,0.040,'【读法】配色为中国财务口径 红=上升 / 绿=下降，不代表好坏 —— 进房率上升是推荐位曝光 −22.1% 的机械效应（不是变好），Search/推荐 CTOR 下降才是真实恶化',
         fontsize=10.5,color=P['ann_grey'])
fig.savefig(f'{OUT}/KANS_VN_{PERIOD}_Step9_流量入口结构.png',dpi=150,facecolor='white',bbox_inches='tight')
print('ok')
