# -*- coding: utf-8 -*-
"""图5 · 本周 TopN 店铺 GMV 与排名变化（实心=本周，虚线框=上周）"""
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
p.add_argument("--n", type=int, default=20)
p.add_argument("--out", default="05_TopN排名与GMV.png")
a = p.parse_args()
C.setup_font()

cur, pri = C.read_export(a.cur), C.read_export(a.pri)
r0 = {n: i + 1 for i, n in enumerate(pri.store)}
g0 = pri.set_index("store")["gmv"]
rows = [(i + 1, s, g) for i, (s, g) in enumerate(zip(cur.store[:a.n], cur.gmv[:a.n]))]
krk = int(cur.index[cur.store == C.KANS][0]) + 1
extra = krk > a.n
if extra:
    rows.append((krk, C.KANS, float(cur.set_index("store").loc[C.KANS, "gmv"])))

fig, ax = plt.subplots(figsize=(12, .38 * len(rows) + 2.2))
y = np.arange(len(rows))[::-1].astype(float)
if extra:
    y[-1] -= 1.0
labels = []
for i, (rk, s, g1) in enumerate(rows):
    isk = s == C.KANS
    ax.barh(y[i], C.wan(g1, a.rate), .52, color=C.C_KANS if isk else C.C_NOW, zorder=3)
    if s in g0.index:
        ax.barh(y[i], C.wan(g0[s], a.rate), .52, color="none", edgecolor="#4D4D4D",
                lw=1.1, ls=(0, (3, 2)), zorder=4)
    prk = r0.get(s)
    if prk is None:
        dlt, col = "新进", C.C_UP
    elif prk > rk:
        dlt, col = f"↑{prk-rk}", C.C_UP
    elif prk < rk:
        dlt, col = f"↓{rk-prk}", C.C_DN
    else:
        dlt, col = "持平", "#999999"
    ax.annotate(f"{C.wan(g1, a.rate):,.0f}万", (C.wan(g1, a.rate), y[i]), xytext=(7, 0),
                textcoords="offset points", va="center", fontsize=9, fontweight="bold")
    ax.annotate(dlt, (C.wan(g1, a.rate), y[i]), xytext=(66, 0), textcoords="offset points",
                va="center", fontsize=9.5, color=col, fontweight="bold")
    labels.append(("★ " if isk else "") + f"{rk}  " + C.label(s))
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9.5)
for t, (rk, s, g) in zip(ax.get_yticklabels(), rows):
    if s == C.KANS:
        t.set_color("#7A4B00"); t.set_fontweight("bold")
ax.set_xlim(0, C.wan(max(r[2] for r in rows), a.rate) * 1.28)
ax.set_xlabel("总 GMV（万元）", fontsize=9.5)
ax.grid(axis="x", color="#EEEEEE", lw=.8, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
if extra:
    ax.axhline(y[-1] + .62, color="#DDDDDD", lw=.9)
ax.set_ylim(y[-1] - .9, y[0] + .8)
ax.legend(handles=[Patch(fc=C.C_NOW, label=f"{a.cur_label}"),
                   Patch(fc="white", ec="#4D4D4D", ls="--", label=f"{a.pri_label}"),
                   Patch(fc=C.C_KANS, label=f"韩束 KANS（第{krk}名）")],
          loc="lower right", frameon=False, fontsize=9)
ax.set_title(f"{a.cur_label} Top{a.n} 店铺 GMV 与排名变化（左侧数字为本周排名，右侧为名次变化）",
             fontsize=12.5, fontweight="bold", loc="left")
C.foot(fig, "名次变化对照上周 Top200 位次；「新进」表示上周不在 Top200，不代表上周为 0。"
            "本图为店铺层，多店品牌未合并。")
C.save(fig, a.out)
