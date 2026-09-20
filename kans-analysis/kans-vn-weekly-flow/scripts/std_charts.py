# -*- coding: utf-8 -*-
"""
KANS 越南周报 · 标准图表三件套（窗口/汇率全部从 _config.py 读）
  图1  每日 GMV 与 ROI（两周连排对比，周换色）
  图2  A·趋势共振对比（KANS 直播 GMV vs 大盘直播 GMV，指数化 + 底部数据条）
  图3  大盘分渠道 GMV 日趋势（堆叠柱 + 总GMV线 + 底部周合计条）
窗口与汇率：见 _config.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, W1, W2, W1L, W2L, VND as _VND, BREAKEVEN, OUT as _OUT, SKILL_CHART
sys.path.insert(0, SKILL_CHART)
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyBboxPatch
from matplotlib.lines import Line2D
from scipy import stats
import common as C

OUT = _OUT
REG, BLK = C.setup_cjk_font()
P = C.PALETTE
VND = _VND
UP, DN = '#C0392B', '#00875A'          # 红=↑ 绿=↓


d = pd.read_csv(f'{OUT}/daily_base.csv', parse_dates=['date'])
mk = pd.read_csv(f'{OUT}/market_daily.csv', parse_dates=['date'])
d = d[(d['date'] >= W1[0]) & (d['date'] <= W2[1])].reset_index(drop=True)
mk = mk[(mk['date'] >= W1[0]) & (mk['date'] <= W2[1])].reset_index(drop=True)
assert len(d) == 14 and len(mk) == 14, (len(d), len(mk))

LAB = [f"{t.month:02d}-{t.day:02d}" for t in d['date']]
X = np.arange(14)
WEEK = X // 7


def wsplit(a):
    return a[:7].sum(), a[7:].sum()


def pct(a, b):
    return (b - a) / a * 100


def framebox(fig, x0, y0, x1, y1):
    fig.patches.append(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0, transform=fig.transFigure,
        boxstyle='round,pad=0.004,rounding_size=0.008',
        fc='white', ec='#C9D2DA', lw=1.2, zorder=1, clip_on=False))


def band(ax, ymaxfrac=0.965, c1='#EEF4FA', c2='#F2FAF6', lab_y=0.955):
    ax.axvspan(-0.7, 6.5, color=c1, alpha=0.75, zorder=0)
    ax.axvspan(6.5, 13.65, color=c2, alpha=0.6, zorder=0)
    ax.axvline(6.5, color='#8A929B', ls='--', lw=1.6, alpha=0.85, zorder=4)
    ax.text(3, lab_y, W1L, transform=ax.get_xaxis_transform(), ha='center',
            fontsize=13, color='#6B7785', fontproperties=BLK)
    ax.text(10, lab_y, W2L, transform=ax.get_xaxis_transform(), ha='center',
            fontsize=13, color='#6B7785', fontproperties=BLK)


# ======================================================================
# 图1 · 每日 GMV 与 ROI（周对比）
# ======================================================================
gmv = d['gmv_rmb'].to_numpy(float)
spend = d['net_cost_rmb'].to_numpy(float)
roi = gmv / spend
cyc = P['week_cycle']
bar_c = [cyc[w] for w in WEEK]

fig, ax = plt.subplots(figsize=(18, 9.4), dpi=150)
ax2 = ax.twinx()
band(ax, lab_y=1.055)
ax.bar(X, gmv, 0.62, color=bar_c, zorder=3, edgecolor='white', lw=0.5)
ymax = gmv.max() * 1.30
for xi, v, w in zip(X, gmv, WEEK):
    ax.text(xi, v + ymax * 0.012, f'¥{v:,.0f}', ha='center', va='bottom',
            fontsize=10.6, color=cyc[w], fontweight='bold')

roi_top = max(6.6, roi.max() * 1.25)
ax2.plot(X, roi, color=P['roi'], lw=2.6, ls=(0, (6, 3)), zorder=5)
ax2.scatter(X, roi, color=P['roi'], marker='D', s=70, zorder=6, edgecolor='white', lw=0.8)
for xi, v, g in zip(X, roi, gmv):
    mvis = v / roi_top * ymax
    dy = -19 if (mvis - g > ymax * 0.085 or mvis < g) else 19
    ax2.annotate(f'{v:.2f}', (xi, v), xytext=(0, dy), textcoords='offset points',
                 ha='center', va='center', fontsize=10, color=P['roi'],
                 bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=P['roi'], lw=1.1), zorder=8)
ax2.axhline(BREAKEVEN, color=P['breakeven'], ls=':', lw=1.5, zorder=2)
ax2.text(13.55, BREAKEVEN + roi_top * 0.012, f'退款后盈亏线 {BREAKEVEN}', ha='right', va='bottom',
         fontsize=10.5, color='#666666')

g1, g2 = wsplit(gmv)
s1, s2 = wsplit(spend)
r1, r2 = g1 / s1, g2 / s2
for k, (lab, gg, rr, col) in enumerate([
        (f'第1周 {W1L[3:]}', g1, r1, cyc[0]), (f'第2周 {W2L[3:]}', g2, r2, cyc[1])]):
    ax.text(0.012 + k * 0.148, 0.975, f'{lab}\n周GMV  ¥{gg:,.0f}\n周ROI  {rr:.2f}',
            transform=ax.transAxes, ha='left', va='top', fontsize=10.6, color='#333333',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', ec=col, lw=1.6), linespacing=1.5)
ax.text(0.012 + 2 * 0.148, 0.975,
        f'环比 WoW\nGMV  {pct(g1, g2):+.1f}%\nROI  {r2-r1:+.2f}',
        transform=ax.transAxes, ha='left', va='top', fontsize=10.6, color='#333333',
        bbox=dict(boxstyle='round,pad=0.5', fc='#FFF6EC', ec=P['roi'], lw=1.6), linespacing=1.5)

ax.set_ylim(0, ymax); ax2.set_ylim(0, roi_top); ax.set_xlim(-0.7, 13.65)
ax.set_xticks(X); ax.set_xticklabels(LAB, fontsize=11)
ax.set_ylabel('GMV（人民币 ¥）', fontsize=12.5)
ax2.set_ylabel('ROI', fontsize=12.5, color=P['roi'])
ax2.tick_params(axis='y', colors=P['roi'])
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f}'))
ax.grid(axis='y', color=P['grid'], lw=0.8, zorder=0)
C.style_axes(ax, ('top',)); C.style_axes(ax2, ('top',))
handles = [Patch(fc=cyc[0], label='GMV 第1周'), Patch(fc=cyc[1], label='GMV 第2周'),
           Line2D([0], [0], color=P['roi'], lw=2.6, ls=(0, (6, 3)), marker='D', mec='white', label='ROI')]
ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.66, 1.0), ncol=3,
          frameon=False, fontsize=11.5)
fig.suptitle(f'KANS 越南 SKINCARE 直播间 · 每日 GMV 与 ROI（{PERIOD} {W2L[3:]} vs {W1L[3:]}）',
             fontsize=17, fontproperties=BLK, y=0.985)
fig.text(0.5, 0.012,
         'GMV / 花费口径：GMV-MAX campaign 1000000000000001 导出（Gross revenue / Net Cost）'
         '   │   ROI = 总收入 ÷ 净成本   │   1 RMB = 3,890 VND   │   盈亏线 4.1 = 退款后综合成本线',
         ha='center', fontsize=10.5, color=P['ann_grey'])
plt.subplots_adjust(top=0.88, bottom=0.09, left=0.058, right=0.945)
fig.savefig(f'{OUT}/KANS_VN_{PERIOD}_图1_每日GMV与ROI周对比.png', dpi=150,
            facecolor='white', bbox_inches='tight')
plt.close(fig)

# ======================================================================
# 图3 · 大盘分渠道 GMV 日趋势（先算，图2 要用）
# ======================================================================
live = (mk['live_yi'].to_numpy(float) * 1e8 / VND / 1e4)
video = (mk['video_yi'].to_numpy(float) * 1e8 / VND / 1e4)
other = (mk['other_yi'].to_numpy(float) * 1e8 / VND / 1e4)
total = live + video + other

fig, ax = plt.subplots(figsize=(18, 10.2), dpi=150)
band(ax, lab_y=0.895)
w = 0.62
ax.bar(X, live, w, color=P['live'], zorder=3, label='直播成交')
ax.bar(X, video, w, bottom=live, color=P['short'], zorder=3, label='短视频成交')
ax.bar(X, other, w, bottom=live + video, color=P['card'], zorder=3, label='其他（商品卡/商城等，残差）')
ax.plot(X, total, color=P['total_line'], lw=2.4, zorder=5)
ax.scatter(X, total, color=P['total_line'], s=46, zorder=6, edgecolor='white', lw=1.0)
for xi, v in zip(X, total):
    ax.text(xi, v + total.max() * 0.028, f'{v:,.0f}', ha='center', va='bottom',
            fontsize=11, color=P['total_line'], fontweight='bold')
for xi, l, v in zip(X, live, video):
    ax.text(xi, l / 2, f'{l:,.0f}', ha='center', va='center', fontsize=9.6, color='white')
    ax.text(xi, l + v / 2, f'{v:,.0f}', ha='center', va='center', fontsize=9.6, color='#5A4415')

ax.set_ylim(0, total.max() * 1.34); ax.set_xlim(-0.7, 13.65)
ax.set_xticks(X); ax.set_xticklabels(LAB, fontsize=11)
ax.set_ylabel('GMV（万 RMB）', fontsize=12.5)
ax.grid(axis='y', color=P['grid'], lw=1.0, zorder=0)
C.style_axes(ax)
leg = [Line2D([0], [0], color=P['total_line'], lw=2.4, marker='o', mec='white', label='总 GMV'),
       Patch(fc=P['live'], label='直播成交'), Patch(fc=P['short'], label='短视频成交'),
       Patch(fc=P['card'], label='其他（商品卡/商城等，残差）')]
ax.legend(handles=leg, loc='upper left', bbox_to_anchor=(0.005, 0.995), ncol=4,
          frameon=False, fontsize=11.5, handlelength=1.6, columnspacing=2.0)
fig.suptitle(f'越南 TikTok 美妆个护 L1 大盘 · 分渠道 GMV 日趋势（14天 {W1[0][5:].replace("-","/")}–{W2[1][5:].replace("-","/")} · W1 vs W2）',
             fontsize=17.5, fontproperties=BLK, x=0.058, ha='left', y=0.985)

# 底部周合计条
plt.subplots_adjust(top=0.9, bottom=0.30, left=0.058, right=0.985)
framebox(fig, 0.058, 0.115, 0.985, 0.245)
cols_x = [0.075, 0.40, 0.545, 0.705, 0.865]
tot1, tot2 = wsplit(total); lv1, lv2 = wsplit(live); vd1, vd2 = wsplit(video); ot1, ot2 = wsplit(other)
hdr = ['大盘周合计与环比（万RMB）', '总 GMV', '直播成交', '短视频成交', '其他']
hcol = ['#333333', '#23303D', P['live'], '#B07A1E', '#5C6672']
for xx, t, cc in zip(cols_x, hdr, hcol):
    fig.text(xx, 0.218, t, fontsize=12.5, color=cc, fontproperties=BLK, va='center', zorder=3)
fig.text(cols_x[0], 0.180, 'W1 → W2', fontsize=11.5, color='#8A929B', va='center', zorder=3)
for xx, (a, b) in zip(cols_x[1:], [(tot1, tot2), (lv1, lv2), (vd1, vd2), (ot1, ot2)]):
    fig.text(xx, 0.180, f'{a:,.0f} → {b:,.0f}', fontsize=12.5, color='#23303D', va='center', zorder=3)
fig.text(cols_x[0], 0.143, '环比', fontsize=11.5, color='#8A929B', va='center', zorder=3)
for xx, (a, b) in zip(cols_x[1:], [(tot1, tot2), (lv1, lv2), (vd1, vd2), (ot1, ot2)]):
    v = pct(a, b)
    fig.text(xx, 0.143, f'{v:+.1f}%', fontsize=14, color=UP if v > 0 else DN,
             fontproperties=BLK, va='center', zorder=3)
sh1 = lv1 / tot1 * 100; sh2 = lv2 / tot2 * 100
vs1 = vd1 / tot1 * 100; vs2 = vd2 / tot2 * 100
os1 = ot1 / tot1 * 100; os2 = ot2 / tot2 * 100
fig.text(0.058, 0.075,
         f'渠道结构占比    直播 {sh1:.1f}% → {sh2:.1f}%（{sh2-sh1:+.1f}pp）  │  '
         f'短视频 {vs1:.1f}% → {vs2:.1f}%（{vs2-vs1:+.1f}pp）  │  其他 {os1:.1f}% → {os2:.1f}%（{os2-os1:+.1f}pp）  │  '
         f'日均 {total.mean():,.0f} 万（区间 {total.min():,.0f}–{total.max():,.0f} 万，峰值 {LAB[int(total.argmax())]}）',
         fontsize=11, color='#5C6672', va='center')
fig.text(0.985, 0.040,
         '数据源 Kalodata「美妆个护」L1 类目 每日核心指标（history 接口，region=VN / currency=VND）  │  '
         '亿VND ÷ 3,890 折万RMB  │  其他 = 总成交 − 直播 − 视频',
         fontsize=10, color=P['ann_grey'], ha='right', va='center')
fig.savefig(f'{OUT}/KANS_VN_{PERIOD}_图3_大盘分渠道GMV趋势.png', dpi=150,
            facecolor='white', bbox_inches='tight')
plt.close(fig)

# ======================================================================
# 图2 · A·趋势共振对比（指数化）
# ======================================================================
kans_i = gmv / gmv.mean() * 100
mkt_i = live / live.mean() * 100
r_all, p_all = stats.pearsonr(live, gmv)
sp_all, _ = stats.spearmanr(live, gmv)
r_w1, p_w1 = stats.pearsonr(live[:7], gmv[:7])
r_w2, p_w2 = stats.pearsonr(live[7:], gmv[7:])

fig, ax = plt.subplots(figsize=(18, 9.6), dpi=150)
band(ax, lab_y=0.955)
ax.axhline(100, color=P['fit_grey'], ls='--', lw=1.3, zorder=1)
ax.plot(X, mkt_i, color=P['market'], lw=2.6, marker='o', ms=8, mec='white', mew=1.1,
        zorder=4, label='大盘 直播GMV（指数）')
ax.plot(X, kans_i, color=P['kans'], lw=2.6, marker='s', ms=7.5, mec='white', mew=1.1,
        zorder=5, label='KANS 直播GMV（指数）')
for xi, vm, vk in zip(X, mkt_i, kans_i):
    up_m = vm >= vk
    ax.annotate(f'{vm:.0f}', (xi, vm), xytext=(0, 13 if up_m else -15), textcoords='offset points',
                ha='center', fontsize=10.2, color=P['market'], zorder=7,
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.8))
    ax.annotate(f'{vk:.0f}', (xi, vk), xytext=(0, -15 if up_m else 13), textcoords='offset points',
                ha='center', fontsize=10.2, color=P['kans'], zorder=7,
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.8))
ax.set_xticks(X); ax.set_xticklabels(LAB, fontsize=10.5)
ax.set_xlim(-0.7, 13.65)
ax.set_ylabel('指数（各自 ÷ 14日均值 × 100）', fontsize=12)
_lo=min(mkt_i.min(),kans_i.min()); _hi=max(mkt_i.max(),kans_i.max())
ax.set_ylim(_lo-(_hi-_lo)*0.10, _hi+(_hi-_lo)*0.16)
ax.grid(axis='y', color=P['grid'], lw=0.9, zorder=0)
C.style_axes(ax)
ax.legend(loc='upper left', bbox_to_anchor=(0.005,0.90), frameon=True, framealpha=0.95, fontsize=11.5, edgecolor='#D5DBE1')
fig.text(0.058, 0.965,
         f'A · 趋势共振对比 ｜ KANS 直播 GMV vs 越南美妆个护大盘 直播 GMV（14天 {W1[0][5:].replace("-","/")}–{W2[1][5:].replace("-","/")}）',
         fontsize=18, fontproperties=BLK, color='#1B2733', va='center')

plt.subplots_adjust(top=0.9, bottom=0.30, left=0.058, right=0.985)
framebox(fig, 0.058, 0.115, 0.985, 0.255)
fig.text(0.075, 0.228, '周合计与环比（万RMB）', fontsize=12.5, color='#333333',
         fontproperties=BLK, va='center', zorder=3)
lv1, lv2 = wsplit(live)
kg1, kg2 = g1 / 1e4, g2 / 1e4
for i, (name, a, b, col) in enumerate([('大盘 · 直播成交', lv1, lv2, P['market']),
                                       ('KANS 直播间 GMV', kg1, kg2, P['kans'])]):
    yy = 0.190 - i * 0.038
    fig.text(0.082, yy, name, fontsize=12, color=col, fontproperties=BLK, va='center', zorder=3)
    fig.text(0.290, yy, f'{a:,.2f} → {b:,.2f}' if b < 100 else f'{a:,.0f} → {b:,.0f}',
             fontsize=12.5, color='#23303D', va='center', zorder=3)
    v = pct(a, b)
    fig.text(0.415, yy, f'{v:+.1f}%', fontsize=14, color=UP if v > 0 else DN,
             fontproperties=BLK, va='center', zorder=3)
fig.add_artist(Line2D([0.487, 0.487], [0.128, 0.242], color='#D5DBE1', lw=1.1,
                      transform=fig.transFigure))
fig.text(0.510, 0.228, '相关系数（不做判断，仅列数）', fontsize=12.5, color='#333333',
         fontproperties=BLK, va='center', zorder=3)
fig.text(0.518, 0.190, '14天全样本', fontsize=11.5, color='#5C6672', va='center', zorder=3)
fig.text(0.615, 0.190, f'Pearson r = {r_all:+.2f}（p={p_all:.2f}）', fontsize=12,
         color='#23303D', va='center', zorder=3)
fig.text(0.820, 0.190, f'Spearman ρ = {sp_all:+.2f}', fontsize=12, color='#23303D',
         va='center', zorder=3)
fig.text(0.518, 0.152, '分周', fontsize=11.5, color='#5C6672', va='center', zorder=3)
fig.text(0.615, 0.152, f'W1 r = {r_w1:+.2f}（p={p_w1:.2f}）', fontsize=12,
         color='#23303D', va='center', zorder=3)
fig.text(0.820, 0.152, f'W2 r = {r_w2:+.2f}（p={p_w2:.2f}）', fontsize=12,
         color='#23303D', va='center', zorder=3)
fig.text(0.058, 0.062,
         '口径：大盘只取 Kalodata「美妆个护」直播成交列（严禁用总 GMV）；KANS 取 GMV-MAX Campaign 总收入。'
         '相关系数对线性缩放免疫（VND↔RMB 不影响 r）；指数化仅为把两条量级不同的线画到同一张图。',
         fontsize=10.5, color=P['ann_grey'], va='center')
fig.savefig(f'{OUT}/KANS_VN_{PERIOD}_图2_趋势共振对比PanelA.png', dpi=150,
            facecolor='white', bbox_inches='tight')
plt.close(fig)

print(f'W1 GMV={g1:,.0f} ROI={r1:.2f} | W2 GMV={g2:,.0f} ROI={r2:.2f} | WoW {pct(g1,g2):+.1f}%')
print(f'大盘直播 {lv1:,.0f} -> {lv2:,.0f} ({pct(lv1,lv2):+.1f}%) | 总 {tot1:,.0f} -> {tot2:,.0f} ({pct(tot1,tot2):+.1f}%)')
print(f'r_all={r_all:.3f} p={p_all:.3f} sp={sp_all:.3f} | W1 r={r_w1:.3f} p={p_w1:.3f} | W2 r={r_w2:.3f} p={p_w2:.3f}')
