# -*- coding: utf-8 -*-
"""图2 · 中国品牌梯队：两周 GMV / 环比 + 达人直播占比位移"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
import common as C

p = argparse.ArgumentParser()
p.add_argument("--cur", required=True)
p.add_argument("--pri", required=True)
p.add_argument("--rate", type=float, default=C.DEFAULT_RATE)
p.add_argument("--cur-label", default="本周")
p.add_argument("--pri-label", default="上周")
p.add_argument("--focus", default="达人直播", help="下半面板看哪个渠道的占比位移")
p.add_argument("--out", default="02_中国品牌梯队.png")
a = p.parse_args()
C.setup_font()

cur, pri = C.read_export(a.cur), C.read_export(a.pri)
B = C.build(cur, pri)
ch = C.CH[C.NM.index(a.focus)]
b = B["brand"].copy()
b["short"] = b["name"].str.replace(r"\s*\(\d+店合计\)", "", regex=True)
b = b[b["short"].isin(C.CN_TIER)].copy()
b["disp"] = np.where(b["stores"] > 1, b["short"] + "\n(" + b["stores"].astype(str) + "店合计)",
                     b["short"])
b = b.sort_values("gmv1", ascending=False).reset_index(drop=True)
if b.empty:
    raise SystemExit("梯队名单没匹配到品牌，检查 common.CN_TIER / CN_NAME")

fig, (ax, axb) = plt.subplots(2, 1, figsize=(1.55 * len(b) + 1.5, 7.6),
                              gridspec_kw={"height_ratios": [2.15, 1], "hspace": .30})
x = np.arange(len(b)); w = .36
top = C.wan(b[["gmv1", "gmv0"]].max().max(), a.rate) * 1.34
ax.bar(x - w / 2, C.wan(b.gmv0, a.rate), w, color=C.C_PRE, label=a.pri_label, zorder=3)
ax.bar(x + w / 2, C.wan(b.gmv1, a.rate), w,
       color=[C.C_KANS if s == "韩束" else C.C_NOW for s in b["short"]],
       label=a.cur_label, zorder=3)
for i, r in b.iterrows():
    ax.annotate(f"{C.wan(r.gmv0, a.rate):,.0f}", (i - w / 2, C.wan(r.gmv0, a.rate)),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10, color="#6B6B6B")
    ax.annotate(f"{C.wan(r.gmv1, a.rate):,.0f}", (i + w / 2, C.wan(r.gmv1, a.rate)),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=11,
                fontweight="bold", color="#7A4B00" if r["short"] == "韩束" else "#1A1A1A")
    ax.text(i, top * .90, f"{r.chg:+.0f}%", ha="center", fontsize=13, fontweight="bold",
            color=C.C_UP if r.chg > 0 else C.C_DN)
ax.text(-.80, top * .90, "GMV\n环比", ha="center", va="center", fontsize=10, color="#999999")
ax.set_ylim(0, top); ax.set_ylabel("总 GMV（万元）", fontsize=11)
ax.set_xticks(x); ax.set_xticklabels([]); ax.set_xlim(-1.15, len(b) - .35)
ax.grid(axis="y", color="#EFEFEF", lw=.9, zorder=0)
ax.legend(frameon=False, fontsize=11, loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.135))
ax.set_title("中国美妆品牌梯队：两周 GMV 与环比（单位 万元，韩束=橙色）",
             fontsize=14, fontweight="bold", loc="left", pad=12)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

dd = b[f"d_{ch}"].values
axb.bar(x, dd, .46, color=[C.C_UP if v > .5 else (C.C_DN if v < -.5 else "#BDBDBD") for v in dd],
        zorder=3)
for i, v in enumerate(dd):
    axb.annotate("基本持平" if abs(v) < .5 else f"{v:+.0f}pp", (i, v),
                 xytext=(0, 7 if v >= 0 else -17), textcoords="offset points", ha="center",
                 fontsize=11.5, fontweight="bold",
                 color=C.C_UP if v > .5 else (C.C_DN if v < -.5 else "#8A8A8A"))
axb.axhline(0, color="#555555", lw=1.1)
axb.set_ylim(min(dd.min() * 1.45, -12), max(dd.max() * 1.45, 12))
axb.set_ylabel(f"{a.focus}占比\n变化（pp）", fontsize=10.5)
axb.set_xticks(x)
axb.set_xticklabels([f"{r.disp}\n{r[f's0_{ch}']:.0f}% → {r[f's1_{ch}']:.0f}%"
                     for _, r in b.iterrows()], fontsize=11.5)
axb.set_xlim(-1.15, len(b) - .35)
axb.tick_params(length=0)
axb.grid(axis="y", color="#EFEFEF", lw=.9, zorder=0)
axb.set_title(f"下方标注为该品牌{a.focus} GMV 占比：{a.pri_label} → {a.cur_label}",
              fontsize=10.5, color="#777777", loc="left", pad=8)
for s in ("top", "right"):
    axb.spines[s].set_visible(False)

mg = "、".join(f"{g} {len(ss)}店" for g, ss in B["merged_groups"]
               if g in set(b["short"])) or "无"
C.foot(fig, f"口径：多店品牌已合并至品牌层（{mg}）；占比分母为五渠道之和。汇率 1USD={a.rate}CNY。")
C.save(fig, a.out)
