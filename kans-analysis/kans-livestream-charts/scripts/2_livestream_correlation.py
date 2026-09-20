"""
图2 · 自有品牌直播 GMV vs 大盘直播 GMV · 相关性验证
==================================================
左 Panel A：两条指数化曲线（量纲归一），看走势是否共振；阴影标大促。
右 Panel B：散点 + 回归，标注 Pearson / 剔除大促 / Spearman。

输入：
  --kans   自播日度，必需列 date(MM-DD), spend_usd, gmv_usd —— 取 gmv_usd 作自有品牌直播GMV
  --market 大盘日度，必需列 date(MM-DD), short_k, live_k, card_k —— 只取 live_k（大盘直播GMV，千USD）
两表按 date 取交集对齐。
*重要*：只用大盘『直播』列(live_k)，不要用总盘。

用法：
  python 2_livestream_correlation.py --kans <csv/xlsx> --market <csv/xlsx> --out <png> \
      [--start 06-01] [--end 06-20] \
      [--promo 06-06 06-18] [--ramp 06-17 06-19] \
      [--index-base window_mean|first_day] [--brand 你的品牌]

大促日 / 拉量日 / 品牌名 / 数据源名默认值在 common.PARAMS 里，命令行参数可覆盖；
传 `--promo` 后面不带日期 = 本期没有大促。

方法论备注（见 SKILL.md）：
  - 相关系数对线性缩放完全免疫——换分母/换币种(USD/VND)都不影响 r。
  - 指数化(÷均值×100)只是把两条不同量级的线画到一张图上的视觉手段；
    它『不能跨窗口比绝对高度』，因为均值会随时间段变。要跨图叠看就用 --index-base first_day。
  - 真正的结论看 Panel B 的 r / 回归，那一层与口径无关。
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import common as C


def _index(arr, base):
    if base == "first_day":
        return arr / arr[0] * 100
    return arr / arr.mean() * 100  # window_mean (默认)


def build(dk, dm, out, promo_dates=None, ramp_dates=None, index_base="window_mean", title=None,
          brand=None, year=None):
    P0 = C.PARAMS
    promo_dates = P0["promo_dates"] if promo_dates is None else promo_dates
    ramp_dates = P0["ramp_dates"] if ramp_dates is None else ramp_dates
    brand = brand or P0["brand"]
    year = year or P0["year"]
    reg, BLK = C.setup_cjk_font()
    m = dk.merge(dm, on="date", how="inner").sort_values("date").reset_index(drop=True)
    dates = m["date"].tolist()
    kans = m["gmv_usd"].to_numpy(float)       # 自有品牌 直播GMV (USD)
    mkt = m["live_k"].to_numpy(float)         # 大盘 直播GMV (千USD) —— 只用直播列
    x = np.arange(len(m))

    promo = [i for i, d in enumerate(dates) if d in set(promo_dates)]
    ramp = [i for i, d in enumerate(dates) if d in set(ramp_dates)]
    normal = [i for i in range(len(m)) if i not in promo]            # 非大促（含自播）
    nrm_circ = [i for i in range(len(m)) if i not in promo + ramp]   # 普通平销日

    r_full = np.corrcoef(mkt, kans)[0, 1]
    r_ex, p_ex = stats.pearsonr(mkt[normal], kans[normal]) if len(normal) > 2 else (np.nan, np.nan)
    sp, _ = stats.spearmanr(mkt, kans)
    af, bf = np.polyfit(mkt, kans, 1)
    an, bn = np.polyfit(mkt[normal], kans[normal], 1)

    P = C.PALETTE
    fig = plt.figure(figsize=(20, 9.2), dpi=155)
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.18, 1], wspace=0.16,
                           left=0.052, right=0.985, top=0.80, bottom=0.13)
    axA = fig.add_subplot(gs[0]); axB = fig.add_subplot(gs[1])

    # ---- Panel A ----
    mkt_i = _index(mkt, index_base); kans_i = _index(kans, index_base)
    # 大促/自播阴影
    for grp, alpha in [(promo, 0.85), (ramp, 0.5)]:
        for i in grp:
            axA.axvspan(i - 0.45, i + 0.45, color=P["promo_band"], alpha=alpha, zorder=0)
    base100 = 100
    axA.axhline(base100, color=P["fit_grey"], ls="--", lw=1.3, zorder=1)
    axA.plot(x, mkt_i, color=P["market"], lw=2.6, marker="o", ms=8, mec="white", mew=1.1,
             zorder=4, label="大盘 直播GMV（指数）")
    axA.plot(x, kans_i, color=P["kans"], lw=2.6, marker="s", ms=7.5, mec="white", mew=1.1,
             zorder=5, label=f"{brand} 直播GMV（指数）")
    axA.set_xticks(x); axA.set_xticklabels(dates, fontsize=9.5)
    axA.set_ylabel(f"指数（各自{'首日' if index_base=='first_day' else f'{len(m)}日均值'} = 100）", fontsize=12)
    axA.grid(axis="y", color=P["grid"], lw=0.9, zorder=0)
    C.style_axes(axA)
    axA.legend(loc="upper right", frameon=False, fontsize=12, bbox_to_anchor=(0.995, 0.99))
    axA.text(0, 1.045, "A · 趋势共振对比（量纲归一）", transform=axA.transAxes,
             fontsize=15, fontproperties=BLK, color="#1B2733")

    # ---- Panel B ----
    xs = np.linspace(mkt.min() * 0.9, mkt.max() * 1.04, 50)
    axB.plot(xs, af * xs + bf, color=P["fit_full"], lw=2.0, zorder=3)
    axB.plot(xs, an * xs + bn, color=P["fit_grey"], lw=1.8, ls=(0, (6, 4)), zorder=3)
    axB.scatter(mkt[nrm_circ], kans[nrm_circ], s=95, color=P["market"], zorder=5,
                edgecolor="white", lw=1, label="平销日")
    if ramp:
        axB.scatter(mkt[ramp], kans[ramp], s=170, color=P["ramp"], marker="^", zorder=6,
                    edgecolor="white", lw=1.2, label=f"{brand} 自播拉量")
    if promo:
        axB.scatter(mkt[promo], kans[promo], s=240, color=P["kans"], marker="*", zorder=6,
                    edgecolor="white", lw=1.0, label="平台大促")
    box = (f"全样本   Pearson r = {r_full:.2f}   (R²={r_full**2:.2f})\n"
           f"剔除大促   r = {r_ex:.2f}   (p={p_ex:.2f}，{'不显著' if p_ex>0.05 else '显著'})\n"
           f"Spearman 秩相关 = {sp:.2f}")
    axB.text(0.36, 0.97, box, transform=axB.transAxes, ha="left", va="top", fontsize=11.5,
             color="#23303D", linespacing=1.7,
             bbox=dict(boxstyle="round,pad=0.6", fc="white", ec="#C9D2DA", lw=1.3))
    axB.set_xlabel("大盘 直播GMV (USD, 千)", fontsize=12)
    axB.set_ylabel(f"{brand} 直播GMV (USD)", fontsize=12)
    axB.grid(True, color=P["grid"], lw=0.9, zorder=0)
    C.style_axes(axB)
    axB.legend(loc="lower right", frameon=False, fontsize=11, labelspacing=0.8)
    axB.text(0, 1.045, "B · 散点与回归", transform=axB.transAxes,
             fontsize=15, fontproperties=BLK, color="#1B2733")

    if title is None:
        title = f"{brand} 直播 GMV vs 大盘直播 GMV · 相关性验证（{year}.{dates[0].replace('-','.')}–{dates[-1].replace('-','.')}）"
    fig.text(0.052, 0.945, title, fontsize=22, fontproperties=BLK, color="#1B2733", va="bottom")
    base_txt = "各自首日 = 100" if index_base == "first_day" else f"各自 ÷ {len(m)} 日均值 × 100"
    fig.text(0.052, 0.035,
             f"数据来源：{brand} {P0['self_source']} 总收入（USD）  +  {P0['market_source']} · {P0['category']} 直播GMV（USD, 区间最大值）"
             f"    │    相关系数对量纲无关    │    指数 = {base_txt}",
             fontsize=10.5, color=P["ann_grey"], va="bottom")
    fig.savefig(out, dpi=155, facecolor="white", bbox_inches="tight")
    print("saved", out)
    print(f"  r_full={r_full:.3f}  r_ex={r_ex:.3f}  p_ex={p_ex:.3f}  spearman={sp:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kans", required=True, help="自播日度 CSV(date,spend_usd,gmv_usd) 或 Campaign xlsx")
    ap.add_argument("--market", required=True, help="大盘日度 CSV(date,short_k,live_k,card_k) 或类目导出 xlsx")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--promo", nargs="*", default=None,
                    help=f"平台大促日 MM-DD 列表，默认 common.PARAMS {C.PARAMS['promo_dates']}；只写 --promo 表示无大促")
    ap.add_argument("--ramp", nargs="*", default=None,
                    help=f"自播拉量日 MM-DD 列表，默认 common.PARAMS {C.PARAMS['ramp_dates']}")
    ap.add_argument("--index-base", choices=["window_mean", "first_day"], default="window_mean")
    ap.add_argument("--brand", default=None, help=f"图例里的品牌名，默认 '{C.PARAMS['brand']}'")
    ap.add_argument("--year", default=None, help=f"标题里的年份，默认 {C.PARAMS['year']}")
    ap.add_argument("--title")
    a = ap.parse_args()
    dk = C.load_kans_daily(a.kans, a.start, a.end)
    dm = C.load_market_daily(a.market, a.start, a.end)
    build(dk, dm, a.out, a.promo, a.ramp, index_base=a.index_base, title=a.title,
          brand=a.brand, year=a.year)
