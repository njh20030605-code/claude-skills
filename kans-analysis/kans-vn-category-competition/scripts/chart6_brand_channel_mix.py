# -*- coding: utf-8 -*-
"""
图6 · 指定品牌组的渠道占比结构横向对比（100% 堆叠 + GMV + 类目排名）
默认三组：确认中国品牌 / 疑似中国跨境（归属待核）/ 国际·本地对照组。
用 --group "组名=店铺1|店铺2;..." 可自定义。
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import common as C

DEFAULT_GROUPS = [
    ("确认中国品牌", ["珂拉琪", "Carslan.VN", "Flower Knows V N", C.KANS]),
    ("疑似中国跨境卖家（归属待核）", ["LUCENBASE COSMETIC.VN", "Mooekiss",
                            "AZTK", "URMINE VN STORE", "Socus Sea VN"]),
    ("国际 / 本地对照组", ["Cocoon Vietnam", "CeraVe Việt Nam",
                     "L'oreal Paris Việt Nam", "La Roche-Posay Việt Nam"]),
]

p = argparse.ArgumentParser()
p.add_argument("--cur", required=True)
p.add_argument("--pri", required=True)
p.add_argument("--rate", type=float, default=C.DEFAULT_RATE)
p.add_argument("--cur-label", default="本周")
p.add_argument("--pri-label", default="上周")
p.add_argument("--group", action="append", default=None,
               help='自定义分组："组名=店铺A|品牌B" 可重复传')
p.add_argument("--out", default="06_品牌渠道占比对比.png")
a = p.parse_args()
C.setup_font()

cur, pri = C.read_export(a.cur), C.read_export(a.pri)
B = C.build(cur, pri)
bd = B["brand"].set_index("key")
rank = {s: i + 1 for i, s in enumerate(cur.store)}

groups = DEFAULT_GROUPS
if a.group:
    groups = []
    for g in a.group:
        nm, _, items = g.partition("=")
        groups.append((nm.strip(), [x.strip() for x in items.split("|") if x.strip()]))

rows = [dict(kind="ref", label=f"大盘平均（{B['market']['n']} 家）",
             share=B["market"]["share1"], gmv=B["market"]["gmv1"], rk=None)]
for gname, keys in groups:
    tmp = []
    for k in keys:
        kk = k
        if kk not in bd.index:
            # 品牌名没合并成功（有门店单周掉榜）→ 退回到该品牌在榜的最大门店
            cand = [s for s in C.MULTI_STORE.get(k, []) if s in bd.index]
            if cand:
                kk = max(cand, key=lambda s: bd.loc[s, "gmv1"])
                print(f"[退回店铺层] {k} 未合并（有门店单周掉榜），改用 {kk}")
            else:
                print(f"[跳过] 未在本周榜内或键名不匹配：{k}")
                continue
        r = bd.loc[kk]
        tmp.append(dict(kind="bar", label=r["name"], gmv=r["gmv1"], rk=r["rank1"],
                        share=np.array([r[f"s1_{c}"] for c in C.CH])))
    if not tmp:
        continue
    rows.append(dict(kind="hdr", label=gname))
    rows += sorted(tmp, key=lambda r: -r["gmv"])

n = len(rows)
fig, ax = plt.subplots(figsize=(14.5, .50 * n + 1.5))
ypos, ylab = [], []
y = n
for r in rows:
    y -= 1
    if r["kind"] == "hdr":
        ax.text(-2, y, r["label"], fontsize=12, fontweight="bold", color="#4A4A4A",
                ha="right", va="center")
        continue
    isk = "韩束" in r["label"]
    isref = r["kind"] == "ref"
    left = 0
    for i in range(5):
        v = r["share"][i]
        ax.barh(y, v, left=left, height=.62 if not isref else .52, color=C.PAL[i], zorder=3,
                edgecolor="white", lw=1.2, alpha=.55 if isref else 1.0)
        if v >= 5.5:
            ax.text(left + v / 2, y, f"{v:.0f}", ha="center", va="center", fontsize=10.5,
                    color="white", fontweight="bold")
        left += v
    ax.text(102, y, f"{C.wan(r['gmv'], a.rate):,.0f} 万元", va="center", fontsize=11,
            fontweight="bold" if isk else "normal",
            color="#7A4B00" if isk else ("#888888" if isref else "#1A1A1A"))
    if r["rk"]:
        ax.text(131, y, f"第 {r['rk']} 名", va="center", fontsize=10,
                color="#7A4B00" if isk else "#999999")
    ypos.append(y); ylab.append(("★ " if isk else "") + r["label"])
    if isk:
        ax.barh(y, 100, height=.86, color=C.C_KANS, alpha=.16, zorder=1)

ax.set_yticks(ypos); ax.set_yticklabels(ylab, fontsize=11.5)
for t, l in zip(ax.get_yticklabels(), ylab):
    if l.startswith("★"):
        t.set_color("#7A4B00"); t.set_fontweight("bold")
    elif "大盘" in l:
        t.set_color("#888888")
ax.set_xlim(0, 150); ax.set_ylim(-.75, n - .45)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xticklabels(["0", "20", "40", "60", "80", "100%"], fontsize=10.5)
ax.tick_params(length=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_position(("data", -0.75))
ax.spines["bottom"].set_color("#DDDDDD")
for x in (20, 40, 60, 80, 100):
    ax.axvline(x, color="#F0F0F0", lw=.9, zorder=0)
ax.text(102, n - .72, f"{a.cur_label}总 GMV", fontsize=10.5, color="#999999", va="center",
        fontweight="bold")
ax.text(131, n - .72, "类目排名", fontsize=10.5, color="#999999", va="center", fontweight="bold")
ax.legend(handles=[Patch(color=C.PAL[i], label=C.NM[i]) for i in range(5)],
          loc="upper center", bbox_to_anchor=(.42, -.02 - .62 / n), ncol=5, frameon=False,
          fontsize=11.5)
fig.suptitle(f"各品牌渠道 GMV 占比结构对比（{a.cur_label}）", fontsize=16, fontweight="bold",
             x=0.005, ha="left", y=1.0 + .95 / n)
fig.text(0.005, 1.0 + .28 / n,
         "数字为该渠道占品牌五渠道 GMV 之和的百分比（<5.5% 未标注）；类目排名为店铺层本周 Top200 位次，"
         "多店品牌取最高位", fontsize=11, color="#777777", ha="left", va="bottom")
C.foot(fig, f"口径：多店铺品牌已合并至品牌层；带 ? 的品牌归属尚未核实，仅作结构参照。"
            f"汇率 1USD={a.rate}CNY。", y=-.03 - .95 / n)
C.save(fig, a.out)
