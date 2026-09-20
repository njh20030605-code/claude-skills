# -*- coding: utf-8 -*-
"""图1 · 左：大盘渠道占比结构两周对比；右：KANS 各渠道增幅 vs 大盘同渠道"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import common as C

p = argparse.ArgumentParser()
p.add_argument("--cur", required=True)
p.add_argument("--pri", required=True)
p.add_argument("--rate", type=float, default=C.DEFAULT_RATE)
p.add_argument("--cur-label", default="本周")
p.add_argument("--pri-label", default="上周")
p.add_argument("--out", default="01_渠道结构对比.png")
a = p.parse_args()
C.setup_font()

cur, pri = C.read_export(a.cur), C.read_export(a.pri)
B = C.build(cur, pri)
M = B["market"]
k1 = cur.set_index("store").loc[C.KANS]
k0 = pri.set_index("store").loc[C.KANS]
kans = np.array([k1[c] / k0[c] - 1 if k0[c] else np.nan for c in C.CH]) * 100
k_tot = (k1["gmv"] / k0["gmv"] - 1) * 100

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 5.4),
                               gridspec_kw={"width_ratios": [1.08, 1], "wspace": 0.16})
# ---- 左：占比结构
left = [0, 0]
for i in range(5):
    ax1.barh([1, 0], [M["share1"][i], M["share0"][i]], left=left, height=.5,
             color=C.PAL[i], zorder=3, edgecolor="white", lw=1.3)
    for j, (v, l) in enumerate(zip([M["share1"][i], M["share0"][i]], left)):
        if v > 3.2:
            ax1.text(l + v / 2, [1, 0][j], f"{v:.1f}%", ha="center", va="center",
                     fontsize=11, color="white", fontweight="bold")
    left = [left[0] + M["share1"][i], left[1] + M["share0"][i]]
ax1.set_yticks([1, 0]); ax1.set_yticklabels([a.cur_label, a.pri_label], fontsize=11)
ax1.set_xlim(0, 100); ax1.set_xticks([]); ax1.set_ylim(-.6, 1.6)
ax1.set_title("① 大盘渠道 GMV 占比结构", fontsize=13, fontweight="bold", loc="left", pad=10)
for s in ax1.spines.values():
    s.set_visible(False)
ax1.legend(handles=[Patch(color=C.PAL[i], label=C.NM[i]) for i in range(5)],
           loc="upper center", bbox_to_anchor=(.5, -.04), ncol=5, frameon=False, fontsize=11)

# ---- 右：KANS vs 大盘 各渠道增幅
CAP = 132
order = np.argsort(kans)
y = np.arange(5); h = .36
for i, o in enumerate(order):
    kv, mv = kans[o], M["ch_chg"][o]
    ax2.barh(y[i] + h / 2, min(kv, CAP), h, color=C.C_KANS, zorder=3)
    ax2.barh(y[i] - h / 2, min(mv, CAP), h, color=C.C_MKT, zorder=3)
    if kv > CAP:
        ax2.annotate("", xy=(CAP + 13, y[i] + h / 2), xytext=(CAP + 1, y[i] + h / 2),
                     arrowprops=dict(arrowstyle="-|>", color=C.C_KANS, lw=2.6), zorder=4)
        ax2.text(CAP + 17, y[i] + h / 2, f"{kv:+.0f}%", va="center", fontsize=12,
                 fontweight="bold", color="#7A4B00")
    else:
        ax2.text(min(kv, CAP) + 3, y[i] + h / 2, f"{kv:+.0f}%", va="center",
                 fontsize=11.5, fontweight="bold", color="#7A4B00")
    ax2.text(mv + 3, y[i] - h / 2, f"{mv:+.0f}%", va="center", fontsize=11, color="#2C3E50")
    gap = kv - mv
    ax2.text(CAP + 52, y[i], f"跑赢 {gap:+.0f}pp" if gap > 0 else f"跑输 {abs(gap):.0f}pp",
             va="center", fontsize=11, fontweight="bold" if gap < 0 else "normal",
             color=C.C_UP if gap < 0 else C.C_DN)
ax2.set_yticks(y); ax2.set_yticklabels([C.NM[o] for o in order], fontsize=12)
ax2.set_xlim(0, CAP + 108); ax2.set_xticks([]); ax2.set_ylim(-.7, 5.3)
ax2.axhline(4.72, color="#E5E5E5", lw=1)
ax2.text(CAP + 52, 4.45, "KANS vs 大盘", fontsize=10.5, color="#999999")
worst = C.NM[int(np.argmin(kans - M["ch_chg"]))]
if (kans - M["ch_chg"]).min() < 0:
    ax2.text(0, 5.05, f"{worst}是 KANS 唯一跑输大盘的渠道（注意大盘为 GMV 加权值，"
                      f"需同时看店铺中位数）", fontsize=11, color=C.C_UP, fontweight="bold")
ax2.set_title("② KANS 各渠道环比增幅 vs 大盘同渠道", fontsize=13, fontweight="bold",
              loc="left", pad=10)
for s in ax2.spines.values():
    s.set_visible(False)
ax2.legend(handles=[Patch(fc=C.C_KANS, label=f"KANS（总 GMV {k_tot:+.0f}%）"),
                    Patch(fc=C.C_MKT, label=f"大盘（总 GMV {M['gmv_chg']:+.0f}%）")],
           loc="upper center", bbox_to_anchor=(.5, -.06), ncol=2, frameon=False, fontsize=11)

fig.suptitle(f"越南美妆个护 TikTok Shop 渠道结构与增幅对比（{a.cur_label} vs {a.pri_label}）",
             fontsize=15, fontweight="bold", y=1.12, x=0.005, ha="left")
fig.text(0.005, 1.028, f"可比口径：两周均在类目 Top200 的 {M['n']} 家店铺；占比分母为五渠道之和",
         fontsize=11, color="#777777", ha="left", va="bottom")
C.foot(fig, f"数据来源：平台导出，汇率 1USD={a.rate}CNY。增幅超出坐标范围的用箭头后标注实际值。", y=-0.10)
C.save(fig, a.out)
