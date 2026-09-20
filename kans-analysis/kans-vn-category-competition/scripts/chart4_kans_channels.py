# -*- coding: utf-8 -*-
"""图4 · KANS 自身各渠道 GMV 两周对比 + 占比结构"""
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
p.add_argument("--out", default="04_KANS渠道结构.png")
a = p.parse_args()
C.setup_font()

cur, pri = C.read_export(a.cur), C.read_export(a.pri)
k1 = cur.set_index("store").loc[C.KANS]
k0 = pri.set_index("store").loc[C.KANS]
v1 = np.array([k1[c] for c in C.CH], float)
v0 = np.array([k0[c] for c in C.CH], float)
rank1 = int(cur.index[cur.store == C.KANS][0]) + 1
rank0 = int(pri.index[pri.store == C.KANS][0]) + 1

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.4), gridspec_kw={"width_ratios": [1.35, 1]})
x = np.arange(5); w = .36
a1.bar(x - w / 2, C.wan(v0, a.rate), w, color=C.C_PRE, label=a.pri_label, zorder=3)
a1.bar(x + w / 2, C.wan(v1, a.rate), w, color=C.C_KANS, label=a.cur_label, zorder=3)
top = C.wan(max(v1.max(), v0.max()), a.rate)
for i in range(5):
    a1.text(i - w / 2, C.wan(v0[i], a.rate) + top * .02, f"{C.wan(v0[i], a.rate):.1f}",
            ha="center", fontsize=8, color="#777777")
    a1.text(i + w / 2, C.wan(v1[i], a.rate) + top * .02, f"{C.wan(v1[i], a.rate):.1f}",
            ha="center", fontsize=8.5, fontweight="bold")
    if v0[i]:
        g = (v1[i] / v0[i] - 1) * 100
        a1.text(i, C.wan(max(v1[i], v0[i]), a.rate) + top * .09, f"{g:+.0f}%", ha="center",
                fontsize=9.5, fontweight="bold", color=C.C_UP if g > 0 else C.C_DN)
a1.set_xticks(x); a1.set_xticklabels(C.NM, fontsize=9.5)
a1.set_ylabel("GMV（万元）", fontsize=9.5); a1.set_ylim(0, top * 1.3)
a1.grid(axis="y", color="#EEEEEE", lw=.8, zorder=0)
a1.legend(frameon=False, fontsize=9)
a1.set_title("韩束 KANS 各渠道 GMV", fontsize=11, fontweight="bold", loc="left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)

p1, p0 = v1 / v1.sum() * 100, v0 / v0.sum() * 100
left = [0, 0]
for i in range(5):
    a2.barh([1, 0], [p1[i], p0[i]], left=left, height=.45, color=C.PAL[i], zorder=3,
            edgecolor="white", lw=1.2)
    for j, (v, l) in enumerate(zip([p1[i], p0[i]], left)):
        if v > 4:
            a2.text(l + v / 2, [1, 0][j], f"{v:.0f}%", ha="center", va="center",
                    fontsize=8.5, color="white", fontweight="bold")
    left = [left[0] + p1[i], left[1] + p0[i]]
a2.set_yticks([1, 0]); a2.set_yticklabels([a.cur_label, a.pri_label], fontsize=9.5)
a2.set_xlim(0, 100); a2.set_xticks([]); a2.set_ylim(-.5, 1.5)
a2.set_title("韩束 KANS 渠道占比结构", fontsize=11, fontweight="bold", loc="left")
for s in a2.spines.values():
    s.set_visible(False)
a2.legend(handles=[Patch(color=C.PAL[i], label=C.NM[i]) for i in range(5)],
          loc="upper center", bbox_to_anchor=(.5, -.05), ncol=3, frameon=False, fontsize=8.5)

gt = (k1["gmv"] / k0["gmv"] - 1) * 100
fig.suptitle(f"韩束 KANS：总 GMV {C.wan(k1['gmv'], a.rate):,.1f} 万元（{gt:+.0f}%），"
             f"排名 {rank0} → {rank1}", fontsize=13, fontweight="bold", y=1.04, x=0.005, ha="left")
aov = (f"自播客单价 {k0['aov']:.0f}→{k1['aov']:.0f} USD（平台字段为整数美元，±1 约 ±4-5%，"
       f"小幅变动不宜过度解读）") if k1.get("aov") else ""
C.foot(fig, aov)
C.save(fig, a.out)
