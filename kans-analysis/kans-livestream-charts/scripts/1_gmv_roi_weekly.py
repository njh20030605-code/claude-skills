"""
图1 · 直播间 每日 GMV 与 ROI（按周对比）
========================================
柱 = 每日 GMV（USD 折 RMB），不同周用不同颜色区分；
线 = 每日 ROI（右轴），含退款后盈亏线；左上角每周小结框 + 环比。

输入：自播日度数据，必需列 date(MM-DD), spend_usd, gmv_usd
  - CSV：examples/kans_daily.csv（示例数据：换成你自己的导出）
  - 或直播间 Campaign 原始 xlsx（按 common.XLSX_HEADERS 表头自动解析）

用法：
  python 1_gmv_roi_weekly.py --input <csv或xlsx> --out <png> \
      [--start 06-08] [--end 06-21] [--rate 6.8] [--breakeven 4.1] [--brand 你的品牌]

汇率 / 盈亏线 / 品牌名默认值在 common.PARAMS 里，命令行参数可覆盖。
口径：ROI = gmv_usd / spend_usd（毛口径，平台展示口径）；GMV(RMB)=gmv_usd*rate。
按周切分：从 --start 起每 7 天一周（第一周/第二周/…）。
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import common as C


def build(df, out, rate=None, breakeven=None,
          title=None, fx_usd_rmb=True, shop_label=None, year=None):
    P = C.PARAMS
    rate = P["usd_rate"] if rate is None else rate
    breakeven = P["breakeven"] if breakeven is None else breakeven
    shop_label = shop_label or P["shop_label"]
    year = year or P["year"]
    reg, BLK = C.setup_cjk_font()
    df = df.reset_index(drop=True)
    n = len(df)
    labels = df["date"].tolist()
    gmv = df["gmv_usd"].to_numpy(float) * (rate if fx_usd_rmb else 1.0)
    spend = df["spend_usd"].to_numpy(float)
    roi = np.where(spend > 0, df["gmv_usd"].to_numpy(float) / np.where(spend == 0, 1, spend), 0)
    x = np.arange(n)
    week = (x // 7)
    n_weeks = int(week.max()) + 1
    cyc = C.PALETTE["week_cycle"]
    bar_colors = [cyc[w % len(cyc)] for w in week]

    fig, ax = plt.subplots(figsize=(max(13, n * 1.18), 8.4), dpi=170)
    ax2 = ax.twinx()

    # 每周背景色块
    for w in range(n_weeks):
        idx = np.where(week == w)[0]
        ax.axvspan(idx[0] - 0.5, idx[-1] + 0.5, color=cyc[w % len(cyc)], alpha=0.05, zorder=0)
    # 周分隔虚线
    for w in range(1, n_weeks):
        boundary = np.where(week == w)[0][0] - 0.5
        ax.axvline(boundary, color="#555555", ls="--", lw=1.6, alpha=0.7, zorder=4)

    ax.bar(x, gmv, 0.62, color=bar_colors, zorder=3, edgecolor="white", linewidth=0.5)
    ymax = gmv.max() * 1.18
    for xi, v, w in zip(x, gmv, week):
        ax.text(xi, v + ymax * 0.011, C.fmt_rmb(v) if fx_usd_rmb else f"${v:,.0f}",
                ha="center", va="bottom", fontsize=10.5,
                color=cyc[w % len(cyc)], fontweight="bold")

    # ROI 线 + 避让标签
    ax2.plot(x, roi, color=C.PALETTE["roi"], lw=2.6, ls=(0, (6, 3)), zorder=5)
    ax2.scatter(x, roi, color=C.PALETTE["roi"], marker="D", s=70, zorder=6,
                edgecolor="white", linewidth=0.8)
    roi_top = max(6.6, roi.max() * 1.25)
    for xi, v, g in zip(x, roi, gmv):
        mvis = v / roi_top * ymax
        gap = mvis - g
        dy = -17 if (gap > ymax * 0.087 or gap < 0) else 18
        ax2.annotate(f"{v:.2f}", (xi, v), xytext=(0, dy), textcoords="offset points",
                     ha="center", va="center", fontsize=10, color=C.PALETTE["roi"],
                     bbox=dict(boxstyle="round,pad=0.25", fc="white",
                               ec=C.PALETTE["roi"], lw=1.1))

    if breakeven:
        ax2.axhline(breakeven, color=C.PALETTE["breakeven"], ls=":", lw=1.4, zorder=2)
        ax2.text(n - 0.55, breakeven + roi_top * 0.011, f"退款后盈亏线 {breakeven}",
                 ha="right", va="bottom", fontsize=10, color="#666666")

    # 周区间括号 + 小结框
    def agg(idx):
        g = df["gmv_usd"].to_numpy(float)[idx].sum()
        s = spend[idx].sum()
        return g * (rate if fx_usd_rmb else 1.0), (g / s if s else 0)
    week_stats = []
    ytop = ymax
    for w in range(n_weeks):
        idx = np.where(week == w)[0]
        col = cyc[w % len(cyc)]
        yb = ytop * 1.005
        ax.annotate("", xy=(idx[0], yb), xytext=(idx[-1], yb),
                    arrowprops=dict(arrowstyle="-", color=col, lw=2.2), annotation_clip=False)
        d0, d1 = labels[idx[0]], labels[idx[-1]]
        ax.text((idx[0] + idx[-1]) / 2, yb + ytop * 0.015, f"第{w+1}周  {d0}–{d1}",
                ha="center", va="bottom", fontsize=12.5, color=col,
                fontproperties=BLK, clip_on=False)
        week_stats.append((w, col, d0, d1) + agg(idx))

    # 小结框（≤3 周才画，避免拥挤）
    if n_weeks <= 3:
        for k, (w, col, d0, d1, g, r) in enumerate(week_stats):
            txt = f"第{w+1}周 {d0}–{d1}\n周GMV  {C.fmt_rmb(g) if fx_usd_rmb else f'${g:,.0f}'}\n周ROI  {r:.2f}"
            ax.text(0.012 + k * 0.143, 0.97, txt, transform=ax.transAxes, ha="left", va="top",
                    fontsize=10.5, color="#333333",
                    bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=col, lw=1.6), linespacing=1.5)
        if n_weeks >= 2:
            g1, r1 = week_stats[0][4], week_stats[0][5]
            g2, r2 = week_stats[1][4], week_stats[1][5]
            wow = f"环比 WoW\nGMV  {(g2/g1-1)*100:+.1f}%\nROI  {r2-r1:+.2f}"
            ax.text(0.012 + n_weeks * 0.143, 0.97, wow, transform=ax.transAxes, ha="left", va="top",
                    fontsize=10.5, color="#333333",
                    bbox=dict(boxstyle="round,pad=0.5", fc="#FFF6EC", ec=C.PALETTE["roi"], lw=1.6),
                    linespacing=1.5)

    ax.set_ylim(0, ymax); ax2.set_ylim(0, roi_top); ax.set_xlim(-0.7, n - 0.35)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("GMV（人民币 ¥）" if fx_usd_rmb else "GMV（USD）", fontsize=12.5)
    ax2.set_ylabel("ROI", fontsize=12.5, color=C.PALETTE["roi"])
    ax2.tick_params(axis="y", colors=C.PALETTE["roi"])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.grid(axis="y", color=C.PALETTE["grid"], lw=0.8, zorder=0)
    C.style_axes(ax, ("top",)); C.style_axes(ax2, ("top",))

    handles = [Patch(fc=cyc[w % len(cyc)], label=f"GMV 第{w+1}周") for w in range(n_weeks)]
    handles.append(Line2D([0], [0], color=C.PALETTE["roi"], lw=2.6, ls=(0, (6, 3)),
                          marker="D", mec="white", label="ROI"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.62, 1.0),
              ncol=len(handles), frameon=False, fontsize=11)

    if title is None:
        rng = f"{labels[0]} ~ {labels[-1]}"
        title = f"{shop_label} 每日 GMV 与 ROI（{year}-{rng} · 1USD={rate}RMB）" if fx_usd_rmb \
            else f"{shop_label} 每日 GMV 与 ROI（{year}-{rng}）"
    fig.suptitle(title, fontsize=16.5, fontproperties=BLK, y=0.99)
    plt.subplots_adjust(top=0.88, bottom=0.07, left=0.062, right=0.94)
    fig.savefig(out, dpi=170, facecolor="white", bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="CSV(date,spend_usd,gmv_usd) 或 Campaign 原始 xlsx")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    ap.add_argument("--start", help="起始日 MM-DD（周从这天起每 7 天切一段）"); ap.add_argument("--end")
    ap.add_argument("--rate", type=float, default=None, help=f"1 USD = ? RMB，默认 common.PARAMS usd_rate={C.PARAMS['usd_rate']}")
    ap.add_argument("--breakeven", type=float, default=None, help=f"退款后盈亏线 ROI，默认 {C.PARAMS['breakeven']}；传 0 不画")
    ap.add_argument("--no-rmb", action="store_true", help="保持 USD，不折人民币")
    ap.add_argument("--brand", default=None, help=f"标题里的店铺/品牌名，默认 '{C.PARAMS['shop_label']}'")
    ap.add_argument("--year", default=None, help=f"标题里的年份，默认 {C.PARAMS['year']}")
    ap.add_argument("--title", help="完全自定义标题（覆盖自动标题）")
    a = ap.parse_args()
    df = C.load_kans_daily(a.input, a.start, a.end)
    build(df, a.out, rate=a.rate, breakeven=a.breakeven,
          title=a.title, fx_usd_rmb=not a.no_rmb, shop_label=a.brand, year=a.year)
