# -*- coding: utf-8 -*-
"""
图3 · 异动定位散点：X=总GMV环比，Y=某渠道占比位移，气泡=本周GMV
回答「谁在涨 + 涨的量从哪个渠道来」。带标签自动避让与四个结论标注框。
"""
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
p.add_argument("--focus", default="达人直播")
p.add_argument("--min-gmv", type=float, default=100000, help="入图门槛（本周 GMV，美元）")
p.add_argument("--zone", type=float, default=20, help="红区阈值 pp")
p.add_argument("--out", default="03_异动定位散点.png")
a = p.parse_args()
C.setup_font()

cur, pri = C.read_export(a.cur), C.read_export(a.pri)
B = C.build(cur, pri)
M = B["market"]
ch = C.CH[C.NM.index(a.focus)]
d = B["brand"].copy()
d["dfocus"] = d[f"d_{ch}"]
d = d[d.gmv1 >= a.min_gmv].reset_index(drop=True)
big = (d.chg >= 100) | (d.chg <= -30) | (d.dfocus.abs() >= a.zone) | (d.name == "韩束")

CAP = float(np.percentile(d.chg, 97))
CAP = max(min(CAP, 460), 200)
d["xp"] = d.chg.clip(upper=CAP)
d["capped"] = d.chg > CAP

fig, ax = plt.subplots(figsize=(15.5, 8.8))
sz = (d.gmv1 / d.gmv1.max()) * 1750 + 60
ax.axhspan(a.zone, 66, color="#C0392B", alpha=.045, zorder=1)
ax.axhline(0, color="#B0B0B0", lw=1, zorder=2)
ax.axvline(M["gmv_chg"], color="#444444", ls="--", lw=1.3, zorder=2)
ax.scatter(d.xp[~big], d.dfocus[~big], s=sz[~big], color="#C8D0D1", alpha=.5,
           edgecolor="white", lw=.9, zorder=3)
ax.scatter(d.xp[big], d.dfocus[big], s=sz[big], color=C.C_NOW, alpha=.58,
           edgecolor="white", lw=1.1, zorder=4)
k = d[d.name == "韩束"]
if len(k):
    ax.scatter(k.xp, k.dfocus, s=sz[k.index] * 1.05, color=C.C_KANS,
               edgecolor="#7A4B00", lw=2.2, zorder=6)
for _, r in d[d.capped].iterrows():
    ax.annotate("", xy=(CAP + CAP * .06, r.dfocus), xytext=(CAP + CAP * .01, r.dfocus),
                arrowprops=dict(arrowstyle="-|>", color=C.C_NOW, lw=2), zorder=7)

lo, hi = min(-95, d.chg.min() * 1.1), CAP * 1.11
ax.set_xlim(lo, hi)
ax.set_ylim(min(-54, d.dfocus.min() * 1.25), max(66, d.dfocus.max() * 1.25))
ax.grid(color="#F2F2F2", lw=.9, zorder=0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_xlabel("总 GMV 环比（%）", fontsize=12.5, labelpad=8)
ax.set_ylabel(f"{a.focus} GMV 占比变化（pp）", fontsize=12.5)
yb = ax.get_ylim()[0]
ax.text(M["gmv_chg"], yb + 2.5, f"大盘 {M['gmv_chg']:+.0f}%", fontsize=11, color="#333333",
        fontweight="bold", ha="center")
ax.text(M["gmv_chg"] - (hi - lo) * .035, yb + 6.5, "← 跑输大盘", fontsize=11, color="#666666",
        ha="right")
ax.text(M["gmv_chg"] + (hi - lo) * .035, yb + 6.5, "跑赢大盘 →", fontsize=11, color="#666666",
        ha="left")
ax.text(lo + (hi - lo) * .01, ax.get_ylim()[1] - 3.5,
        f"红色区 = {a.focus}占比\n提升 {a.zone:.0f}pp 以上", fontsize=11.5, color="#A93226",
        fontweight="bold", va="top")

CAND = [(0, 17), (0, -21), (36, 12), (-36, 12), (36, -16), (-36, -16), (0, 34), (0, -37),
        (64, 25), (-64, 25), (64, -27), (-64, -27), (0, 51), (0, -53), (96, 13), (-96, 13),
        (104, 39), (-104, 39), (104, -39), (-104, -39), (0, 68), (0, -70), (130, 24)]
placed = []
fig.canvas.draw()
sub = d[big].copy()
sub["_p"] = np.where(sub.name == "韩束", 1e12, sub.gmv1)
for _, r in sub.sort_values("_p", ascending=False).iterrows():
    isk = r["name"] == "韩束"
    t = r["name"] if not r.capped else f"{r['name']} {r.chg:+.0f}%"
    fs = 13 if isk else 11
    px, py = ax.transData.transform((r.xp, r.dfocus))
    wd, ht = len(t) * fs * 1.02, fs * 1.6
    best, ok = CAND[0], False
    for dx, dy in CAND:
        box = (px + dx - wd / 2 - 4, py + dy - ht / 2 - 3,
               px + dx + wd / 2 + 4, py + dy + ht / 2 + 3)
        if not any(box[0] < q[2] and q[0] < box[2] and box[1] < q[3] and q[1] < box[3]
                   for q in placed):
            best, ok = (dx, dy), True
            placed.append(box); break
    if not ok:
        placed.append((px + best[0] - wd / 2, py + best[1] - ht / 2,
                       px + best[0] + wd / 2, py + best[1] + ht / 2))
    ax.annotate(t, (r.xp, r.dfocus), xytext=best, textcoords="offset points", ha="center",
                va="center", fontsize=fs, fontweight="bold" if isk else "normal",
                color="#7A4B00" if isk else "#2C3E50", zorder=9,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=.82),
                arrowprops=dict(arrowstyle="-", color="#AAAAAA", lw=.8, shrinkA=0, shrinkB=5)
                if (abs(best[1]) > 25 or abs(best[0]) > 25) else None)

nred = int((d.dfocus >= a.zone).sum())
ax.annotate(f"① 增量集中在{a.focus}：红区 {nred} 个品牌\n几乎全部靠{a.focus}冲量",
            xy=(CAP * .28, a.zone + 11), xytext=(CAP * .35, ax.get_ylim()[1] - 4),
            fontsize=11.5, color="#7B241C", va="top",
            bbox=dict(boxstyle="round,pad=0.5", fc="#FDF2F0", ec="#E6B0AA", lw=1.1),
            arrowprops=dict(arrowstyle="->", color=C.C_NOW, lw=1.5,
                            connectionstyle="arc3,rad=-0.12"))
rev = d.loc[d.dfocus.idxmin()]
ax.annotate(f"② {rev['name']} 反向操作：{a.focus}占比 {rev.dfocus:+.0f}pp、"
            f"总量 {rev.chg:+.0f}%",
            xy=(rev.xp, rev.dfocus), xytext=(CAP * .34, rev.dfocus - 8),
            fontsize=11.5, color="#145A32", va="center",
            bbox=dict(boxstyle="round,pad=0.5", fc="#F0F7F2", ec="#A9CFB8", lw=1.1),
            arrowprops=dict(arrowstyle="->", color=C.C_DN, lw=1.5,
                            connectionstyle="arc3,rad=0.18"))
if len(k):
    ax.annotate("③ 韩束位置", xy=(float(k.xp.iloc[0]), float(k.dfocus.iloc[0])),
                xytext=(CAP * .74, ax.get_ylim()[1] - 18), fontsize=11.5, color="#7A4B00",
                va="center", ha="center",
                bbox=dict(boxstyle="round,pad=0.5", fc="#FDF6E9", ec="#E8C48A", lw=1.3),
                arrowprops=dict(arrowstyle="->", color=C.C_KANS, lw=2,
                                connectionstyle="arc3,rad=0.12"))
ax.annotate("④ 灰色群 = 渠道结构基本没动的大多数，\n增幅跟随大盘",
            xy=(M["gmv_chg"] * .65, 2), xytext=(lo + (hi - lo) * .01, -36),
            fontsize=11.5, color="#5D6D7E", va="center",
            bbox=dict(boxstyle="round,pad=0.5", fc="#F4F6F7", ec="#CFD8DC", lw=1.1),
            arrowprops=dict(arrowstyle="->", color="#95A5A6", lw=1.4,
                            connectionstyle="arc3,rad=0.15"))
ax.legend(handles=[Patch(fc="#C8D0D1", label="结构未明显变化"),
                   Patch(fc=C.C_NOW, label="异动品牌"), Patch(fc=C.C_KANS, label="韩束 KANS")],
          loc="lower right", frameon=False, fontsize=11.5)
fig.suptitle(f"这张图回答：{a.cur_label} 谁在涨、涨的量是从哪个渠道来的", fontsize=16,
             fontweight="bold", x=0.005, ha="left", y=1.045)
fig.text(0.005, 1.005, f"横轴 = 总 GMV 环比｜纵轴 = {a.focus} GMV 占比变化｜气泡大小 = 本周 GMV"
                       f"｜样本：两周均在 Top200 且本周 GMV ≥ {a.min_gmv/1e4:.0f} 万美元的 "
                       f"{len(d)} 个品牌", fontsize=11.5, color="#777777", ha="left", va="bottom")
skip = "、".join(g for g, _ in B["skipped_groups"]) or "无"
C.foot(fig, f"口径：多店品牌已合并至品牌层；因有门店单周掉出 Top200 而未合并的品牌（{skip}）仍按店铺计。"
            f"异动判定：GMV 环比 ≥+100% 或 ≤-30%，或{a.focus}占比变化 ≥{a.zone:.0f}pp。", y=-0.045)
C.save(fig, a.out)
