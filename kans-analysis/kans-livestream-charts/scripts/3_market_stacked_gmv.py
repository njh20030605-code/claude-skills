"""
图3 · Serums & Essences 品类大盘 GMV 趋势
==========================================
堆叠柱（直播 / 短视频 / 商品卡）+ 总GMV 大盘线 + 大促/事件标注。

输入：大盘日度（date, short_k, live_k, card_k）单位千USD
  - CSV：examples/market_daily.csv
  - 或 TTMS Serums 原始 xlsx（自动解析）

用法：
  python 3_market_stacked_gmv.py --input <csv/xlsx> --out <png> [--start][--end]
事件标注默认复刻今天那张（6.6 爆发 / 6.7 急跌 / 6.18 二次高峰 / 日常基本盘），
要改可在 EVENTS 里调，或后续做成 --annotations json。
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import common as C

# 事件标注：date 命中则画箭头标注；text 多行用 \n
EVENTS = [
    dict(date="06-06", text="6.5–6.6 大促爆发\n峰值 {peak} · 直播占 {live_share:.0%}",
         color="ann_blue", tx=-3, ty=140, rad=-0.15, big=True),
    dict(date="06-07", text="大促次日急跌 {dod:+.0%}\n回落至 {total}",
         color="ann_red", tx=2.4, ty=300, rad=0.2),
    dict(date="06-18", text="6.18 二次拉量高峰\n{total} · 直播占 {live_share:.0%}",
         color="ann_teal", tx=-2.4, ty=225, rad=-0.2),
]
BASELINE_NOTE = dict(at="06-12", y=560, text="促间日常基本盘  ≈ $340–460K 区间震荡")


def build(df, out, title=None):
    reg, BLK = C.setup_cjk_font()
    df = df.reset_index(drop=True)
    n = len(df)
    labels = df["date"].tolist()
    short = df["short_k"].to_numpy(float)
    live = df["live_k"].to_numpy(float)
    card = df["card_k"].to_numpy(float)
    total = short + live + card
    x = np.arange(n)
    P = C.PALETTE

    fig, ax = plt.subplots(figsize=(max(14, n * 0.9), 9.3), dpi=160)
    w = 0.62
    ax.bar(x, live, w, color=P["live"], zorder=3)
    ax.bar(x, short, w, bottom=live, color=P["short"], zorder=3)
    ax.bar(x, card, w, bottom=live + short, color=P["card"], zorder=3)
    ax.plot(x, total, color=P["total_line"], lw=2.4, zorder=5)
    ax.scatter(x, total, color=P["total_line"], s=46, zorder=6, edgecolor="white", linewidth=1.0)
    for xi, v in zip(x, total):
        ax.text(xi, v + total.max() * 0.024, C.fmt_usd(v), ha="center", va="bottom",
                fontsize=10.5, color=P["total_line"], fontweight="bold")

    idx_of = {d: i for i, d in enumerate(labels)}
    for ev in EVENTS:
        if ev["date"] not in idx_of:
            continue
        i = idx_of[ev["date"]]
        prev = total[i - 1] if i > 0 else total[i]
        ctx = dict(peak=C.fmt_usd(total[i]), total=C.fmt_usd(total[i]),
                   live_share=live[i] / total[i], dod=total[i] / prev - 1)
        txt = ev["text"].format(**ctx)
        ax.annotate(txt, xy=(i, total[i]),
                    xytext=(i + ev["tx"], total[i] + ev["ty"]),
                    fontsize=13.5 if ev.get("big") else 12.5,
                    color=P[ev["color"]], fontproperties=BLK, ha="center", va="bottom",
                    arrowprops=dict(arrowstyle="->", color=P[ev["color"]], lw=1.7,
                                    connectionstyle=f"arc3,rad={ev['rad']}"))
    if BASELINE_NOTE["at"] in idx_of:
        ax.text(idx_of[BASELINE_NOTE["at"]], BASELINE_NOTE["y"], BASELINE_NOTE["text"],
                fontsize=11.5, color=P["ann_grey"], ha="center", va="center")

    ymax = max(1320, total.max() * 1.2)
    ax.set_ylim(0, ymax); ax.set_xlim(-0.7, n - 0.3)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
    step = 200
    ax.set_yticks(range(0, int(ymax) + 1, step))
    ax.set_yticklabels([f"${v}K" for v in range(0, int(ymax) + 1, step)], fontsize=10.5)
    ax.set_ylabel("GMV (USD)", fontsize=12.5)
    ax.grid(axis="y", color=P["grid"], lw=1.0, zorder=0)
    C.style_axes(ax)
    ax.spines["left"].set_color("#CCCCCC"); ax.spines["bottom"].set_color("#CCCCCC")

    leg = [Line2D([0], [0], color=P["total_line"], lw=2.4, marker="o", mec="white", label="总 GMV（大盘）"),
           Patch(fc=P["short"], label="短视频 GMV"),
           Patch(fc=P["live"], label="直播 GMV"),
           Patch(fc=P["card"], label="商品卡及其他")]
    ax.legend(handles=leg, loc="upper right", bbox_to_anchor=(0.995, 0.99),
              ncol=2, frameon=False, fontsize=12, handlelength=1.6,
              columnspacing=2.4, labelspacing=0.9)

    fig.text(0.065, 0.965, "Serums & Essences 品类大盘 GMV 趋势",
             fontsize=23, fontproperties=BLK, color="#1B2733", va="top")
    fig.text(0.066, 0.918, f"TikTok Shop · 2026.{labels[0].replace('-','.')} – {labels[-1].replace('-','.')} · 单位 USD",
             fontsize=13.5, color=P["ann_grey"], va="top")
    fig.text(0.065, 0.028,
             "数据来源：TTMS    │    品类：Serums & Essences    │    GMV 按区间最大值取数    │    "
             "货币单位：USD    │    总GMV = 短视频 + 直播 + 商品卡及其他",
             fontsize=10.5, color=P["ann_grey"], va="bottom")
    plt.subplots_adjust(top=0.85, bottom=0.085, left=0.065, right=0.985)
    fig.savefig(out, dpi=160, facecolor="white", bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--title")
    a = ap.parse_args()
    df = C.load_market_daily(a.input, a.start, a.end)
    build(df, a.out, title=a.title)
