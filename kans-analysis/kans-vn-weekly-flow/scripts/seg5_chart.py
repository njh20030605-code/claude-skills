# -*- coding: utf-8 -*-
"""流量结构 5 段核心指标条形图

每期只改下面 A（上期）/ B（本期）两个 dict 与 HEAD 那句话；其余从 _config.py 读。

🔴 铁律（踩过才写的，别改）：
  1. 总量只信 CLP（Creator-Live-Performance）；截图/入口表只做结构拆分，不作总量来源。
  2. **每个比率指标名后面必须用括号写死「分子÷分母」**，后台同口径的四项打 ★。
     后台 CTR = 点击÷商品曝光；后台 CTOR = 订单数÷点击。
     CLP 的 LIVE CTR = 点击÷观看（大 8 倍）、CTOR (SKU orders) = SKU单÷点击（大 2 倍）—— 别混。
  3. **AOV 分母是 Attributed orders，不是 SKU orders**（差约 2 倍）。
  4. **UV价值 = GMV ÷ Views 必须单独列一行**（＝ WatchGPM ÷ 1000，标签里写明同源，
     否则并排两行环比一模一样会被问）。UV 是主播/时段表的主指标，5 段表里不能只放 Watch GPM。
  5. 页脚拆两行，否则 bbox_inches='tight' 会把图横向拉爆。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, W1L, W2L, VND, OUT, SKILL_CHART
sys.path.insert(0, SKILL_CHART)
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import common as C
REG,BLK=C.setup_cjk_font()
UP,DN='#C0392B','#1A8A78'; GREY,INK='#8A929B','#23303D'
# 🔴 指标名一律用平台原名，括号里写死分母，避免与后台卡片对不上
A=dict(曝光=4072386,观看=118833,商品曝光=953855,时长h=139.30,场次=8,商品点击=30852,SKU订单=4561,订单=2181,
       GMV=201769.7647,新粉=539,点赞=64676,评论=6207,分享=267)   # 上期＝8月W2 已发布口径（期末+1 日成熟度，与本期对齐）
B=dict(曝光=3657750,观看=111487,商品曝光=993427,时长h=135.8833,场次=7,商品点击=27928,SKU订单=4133,订单=1972,
       GMV=188784.9979,新粉=495,点赞=45343,评论=5805,分享=186)   # 本期全部取自 CLP 汇总（7 场，含 8/17–8/23）
for g in (A,B):
    g['进房率']=g['观看']/g['曝光']; g['场均时长']=g['时长h']/g['场次']
    g['LIVECTR']=g['商品点击']/g['观看']            # CLP「LIVE CTR」列
    g['CTR']=g['商品点击']/g['商品曝光']              # 后台「CTR」卡
    g['CTOR']=g['订单']/g['商品点击']                # 后台「CTOR」卡
    g['CTORSKU']=g['SKU订单']/g['商品点击']          # CLP「CTOR (SKU orders)」列
    g['观看SKU']=g['SKU订单']/g['观看']              # CLP「SKU order rate」列
    g['每小时GMV']=g['GMV']/g['时长h']
    g['ShowGPM']=g['GMV']/g['曝光']*1000; g['WatchGPM']=g['GMV']/g['观看']*1000
    g['UV']=g['GMV']/g['观看']          # UV价值 = GMV ÷ Views（＝ WatchGPM ÷ 1000，同一个数两种写法）
    g['AOV']=g['GMV']/g['订单']
    g['点赞率']=g['点赞']/g['观看']; g['分享率']=g['分享']/g['观看']
    g['评论率']=g['评论']/g['观看']; g['关注率']=g['新粉']/g['观看']
f_wan=lambda v:f'{v/1e4:,.1f}万' if v<1e6 else f'{v/1e4:,.0f}万'
f_h=lambda v:f'{v:.2f}h'; f_yuan=lambda v:f'{v:,.0f}元'; f_yuan1=lambda v:f'{v:,.1f}元'
f_p2=lambda v:f'{v*100:.2f}%'; f_p1=lambda v:f'{v*100:.1f}%'; f_p3=lambda v:f'{v*100:.3f}%'
ROWS=[('SEC','① 流量'),
 ('M','总曝光','曝光',f_wan,False,False),('M','总观看','观看',f_wan,False,True),
 ('M','进房率 = Tap-through（观看÷曝光）','进房率',f_p2,True,True),
 ('M','直播总时长','时长h',f_h,False,False),
 ('M','场均时长*','场均时长',f_h,False,False),
 ('SEC','② 转化漏斗　（后台卡片口径 = 加粗两行）'),
 ('M','商品曝光','商品曝光',f_wan,False,False),
 ('M','LIVE CTR（点击÷观看）','LIVECTR',f_p2,True,False),
 ('M','CTR（点击÷商品曝光）★后台卡','CTR',f_p2,True,True),
 ('M','CTOR（订单÷点击）★后台卡','CTOR',f_p2,True,True),
 ('M','CTOR-SKU（SKU单÷点击）','CTORSKU',f_p2,True,False),
 ('M','SKU order rate（SKU单÷观看）','观看SKU',f_p2,True,False),
 ('SEC','③ 变现效率'),
 ('M','每小时 GMV','每小时GMV',f_yuan,False,True),('M','Show GPM 千次曝光','ShowGPM',f_yuan1,False,False),
 ('M','Watch GPM 千次观看','WatchGPM',f_yuan,False,False),
 ('M','UV价值（GMV÷观看）＝ WatchGPM÷1000','UV',lambda v:f'{v:.3f}元',False,True),
 ('M','客单价 AOV（GMV÷订单数）','AOV',f_yuan1,False,False),
 ('SEC','④ 互动效率'),
 ('M','点赞率','点赞率',f_p1,True,False),('M','分享率','分享率',f_p3,True,True),
 ('M','评论率','评论率',f_p2,True,False),('M','Follow rate 关注率','关注率',f_p3,True,False)]
metrics=[r for r in ROWS if r[0]=='M']
chg={r[2]:(B[r[2]]/A[r[2]]-1)*100 for r in metrics}
n_up=sum(1 for v in chg.values() if v>0); n_all=len(metrics)
X_NAME=1.0;X_SEP=66.0;X_PREV=76.0;X_ARROW=79.5;X_CUR=83.0;X_PP=99.0
_mx=max(chg.values());_mn=min(chg.values())
lo=min(-20.0,np.floor((_mn-8)/10)*10); hi=max(20.0,np.ceil((_mx+14)/10)*10)
BX0,BX1=17.0,63.0
bx=lambda v:BX0+(v-lo)/(hi-lo)*(BX1-BX0); ZERO=bx(0)
n=len(ROWS)
fig,ax=plt.subplots(figsize=(16.4,0.62*n+3.4),dpi=150)
ax.set_xlim(0,100);ax.set_ylim(n+0.6,-1.5);ax.axis('off')
ax.text((BX0+BX1)/2,-0.95,'环比（%）',ha='center',va='center',fontsize=13,fontproperties=BLK,color=INK)
ax.text(X_PREV,-0.95,W1L,ha='right',va='center',fontsize=13,fontproperties=BLK,color='#2C7FB8')
ax.text(X_CUR,-0.95,W2L,ha='left',va='center',fontsize=13,fontproperties=BLK,color='#16A085')
ax.text(X_PP,-0.95,'pp 变化',ha='right',va='center',fontsize=12,fontproperties=BLK,color=GREY)
ax.plot([X_SEP,X_SEP],[-0.55,n-0.4],color='#D5DBE1',lw=1.1,zorder=1)
y=0
for row in ROWS:
    if row[0]=='SEC':
        ax.text(X_NAME,y,row[1],ha='left',va='center',fontsize=13.5,fontproperties=BLK,color=UP)
        ax.plot([X_NAME,X_PP],[y+0.45,y+0.45],color='#F0C9C4',lw=1.0,zorder=1); y+=1; continue
    _,name,key,fmt,is_rate,hl=row
    v=chg[key]; col=UP if v>0 else DN
    if hl: ax.add_patch(Rectangle((X_NAME-0.6,y-0.42),X_PP-X_NAME+1.2,0.84,fc='#FFF6DC',ec='none',zorder=0))
    ax.text(X_NAME,y,name,ha='left',va='center',fontsize=12.2,color=INK,fontproperties=(BLK if hl else None))
    ax.add_patch(Rectangle((min(ZERO,bx(v)),y-0.21),abs(bx(v)-ZERO),0.42,fc=col,ec='none',zorder=3))
    ax.text(bx(v)+(0.9 if v>0 else -0.9),y,f'{v:+.1f}%',ha='left' if v>0 else 'right',va='center',
            fontsize=11.5,fontproperties=BLK,color=col,zorder=4)
    ax.text(X_PREV,y,fmt(A[key]),ha='right',va='center',fontsize=11.8,color=GREY)
    ax.text(X_ARROW,y,'→',ha='center',va='center',fontsize=11.5,color='#B7BEC5')
    ax.text(X_CUR,y,fmt(B[key]),ha='left',va='center',fontsize=11.8,color=INK,fontproperties=BLK)
    if is_rate:
        pp=(B[key]-A[key])*100
        ax.text(X_PP,y,f'{pp:+.3f}pp' if abs(pp)<0.1 else f'{pp:+.2f}pp',ha='right',va='center',
                fontsize=11.5,fontproperties=BLK,color=UP if pp>0 else DN)
    y+=1
ax.plot([ZERO,ZERO],[-0.55,n-0.4],color='#23303D',lw=1.6,zorder=2)
_step=20 if (hi-lo)<=160 else 40
for t in range(int(lo//_step*_step),int(hi)+1,_step):
    if t<lo: continue
    ax.plot([bx(t),bx(t)],[-0.55,n-0.4],color='#ECECEC',lw=0.9,zorder=0)
    ax.text(bx(t),n+0.05,f'{t:+d}'.replace('+0','0'),ha='center',va='center',fontsize=10.5,color=GREY)
fig.suptitle(f'KANS 越南 SKINCARE 直播间 · 流量结构 5 段核心指标｜本期 {W2L} vs 上期 {W1L}',
             fontsize=17,fontproperties=BLK,y=0.985,color=INK)
head=(f'一句话：曝光 {chg["曝光"]:+.1f}%、观看 {chg["观看"]:+.1f}% —— 进房率 {A["进房率"]*100:.2f}% → {B["进房率"]*100:.2f}%'
      f'（{(B["进房率"]-A["进房率"])*100:+.2f}pp）「变好」是推荐位曝光 −22.1% 的机械效应，承接要看 ★CTR 与各入口 CTOR')
fig.text(0.5,0.945,head,ha='center',fontsize=13,fontproperties=BLK,color=UP)
fig.text(0.5,0.030,
 f'数据源：Creator-Live-Performance（W1 {A["场次"]}场 / W2 {B["场次"]}场）　│　GMV 为 Attributed GMV，VND ÷ {VND:,.0f} → RMB　│　'
 '颜色：红 = 上升 / 绿 = 下降（中国财务口径）　│　黄底 = 本期需重点关注项',
 ha='center',fontsize=10.5,color=GREY)
fig.text(0.5,0.014,
 '★ = 与 LIVE Manager › Live Performance 后台卡片同口径（CTR = 点击÷商品曝光、CTOR = 订单数÷点击），可直接对数；本期未提供后台卡片截图，故未做逐项对照　│　'
 '* 场均时长受场次影响（本期 7 场 / 上期 8 场，上期 8/15 曾拆两场），判断请用总时长　│　'
 '上期取 8月W2 已发布口径（期末+1 日成熟度），与本期对齐，未用 8/24 重导版本',
 ha='center',fontsize=9.6,color=GREY)
plt.subplots_adjust(top=0.925,bottom=0.075,left=0.012,right=0.988)
fig.savefig(f'{OUT}/KANS_VN_{PERIOD}_Step9_5段核心指标条形图.png',dpi=150,facecolor='white',bbox_inches='tight')
print(f'{n_up}/{n_all} 上涨')
for r in metrics: print(f'{r[1]:18s} {A[r[2]]:>14,.4f} -> {B[r[2]]:>14,.4f}  {chg[r[2]]:+7.1f}%')
