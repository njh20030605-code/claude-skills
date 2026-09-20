"""
common.py — 三张图共用的工具：中文字体、配色、数字格式、数据读取/解析。

数据读取支持两种来源：
  1) 干净 CSV（推荐，见 examples/）
  2) 平台原始导出 xlsx（KANS Campaign 导出 / TTMS Serums 导出），自动解析

所有脚本都从这里 import，保证三张图的字体、配色、口径一致。
"""
import os
import re
import glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# ----------------------------------------------------------------------
# 中文字体：自动探测，优先 Noto Sans CJK SC，找不到就退化到任意可用 CJK
# ----------------------------------------------------------------------
_CJK_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

def setup_cjk_font():
    """注册并设置中文字体，返回 (regular_name, BOLD_FontProperties)。"""
    reg_path = None
    blk_path = None
    for p in _CJK_CANDIDATES:
        if os.path.exists(p):
            fm.fontManager.addfont(p)
            if reg_path is None:
                reg_path = p
            if "Black" in p or "Bold" in p:
                blk_path = p
    if reg_path is None:
        # 最后兜底：在系统里搜任意带 CJK 的字体
        for f in fm.findSystemFonts():
            if re.search(r"(cjk|noto.*sc|wqy|hei|song)", f, re.I):
                fm.fontManager.addfont(f); reg_path = f; break
    if reg_path is None:
        raise RuntimeError("未找到中文字体，请安装 fonts-noto-cjk 或 wqy-zenhei")
    if blk_path is None:
        blk_path = reg_path
    plt.rcParams["font.family"] = fm.FontProperties(fname=reg_path).get_name()
    plt.rcParams["axes.unicode_minus"] = False
    return fm.FontProperties(fname=reg_path).get_name(), fm.FontProperties(fname=blk_path)

# ----------------------------------------------------------------------
# 统一配色
# ----------------------------------------------------------------------
PALETTE = {
    # 图1 周对比
    "week_cycle": ["#4A90D9", "#16A085", "#8E5BD0", "#E0772B"],  # 周1/周2/周3...
    "roi":        "#D9572B",
    "breakeven":  "#888888",
    # 图2 相关性
    "market":     "#2C7FB8",
    "kans":       "#C0392B",
    "ramp":       "#1A8A78",
    "fit_full":   "#23303D",
    "fit_grey":   "#8B96A3",
    "promo_band": "#FBEFC6",
    # 图3 大盘堆叠
    "live":       "#2D6B8F",
    "short":      "#E0A23C",
    "card":       "#C9D2DA",
    "total_line": "#23303D",
    "ann_blue":   "#2D6B8F",
    "ann_red":    "#C0392B",
    "ann_teal":   "#1A8A78",
    "ann_grey":   "#7C8896",
    "grid":       "#ECECEC",
}

# ----------------------------------------------------------------------
# 数字格式
# ----------------------------------------------------------------------
def fmt_usd(v):
    """美元金额：>=1000(千) 显示 $X.XXM，否则 $XXXK。入参单位为『千USD』。"""
    return f"${v/1000:.2f}M" if v >= 1000 else f"${v:.0f}K"

def fmt_rmb(v):
    return f"¥{v:,.0f}"

# ----------------------------------------------------------------------
# 数据读取
# ----------------------------------------------------------------------
def _read_table(path):
    import pandas as pd
    if path.lower().endswith((".xlsx", ".xlsm", ".xls")):
        return None  # 交给专用解析器
    return pd.read_csv(path)

def parse_kans_campaign_xlsx(path, start=None, end=None):
    """
    解析 KANS 直播间 Campaign 导出 xlsx（按表头定位列，列序变动也能用）。
    需要的表头：'启动时间'、'成本'、'总收入'。
    返回 DataFrame[date, spend_usd, gmv_usd]，按日聚合，已过滤无数据的排期占位行。
    """
    import openpyxl, pandas as pd
    from collections import defaultdict
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    hdr = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    def col(name):
        for i, h in enumerate(hdr):
            if h and name in str(h):
                return i + 1
        raise KeyError(f"列未找到: {name}")
    c_t, c_sp, c_gm = col("启动时间"), col("成本"), col("总收入")
    sp, gm = defaultdict(float), defaultdict(float)
    for r in range(2, ws.max_row + 1):
        t = ws.cell(r, c_t).value
        if not t:
            continue
        d = str(t)[:10]
        try:
            s = float(ws.cell(r, c_sp).value); g = float(ws.cell(r, c_gm).value)
        except (TypeError, ValueError):
            continue
        sp[d] += s; gm[d] += g
    rows = [(d, sp[d], gm[d]) for d in sorted(sp) if (sp[d] > 0 or gm[d] > 0)]
    df = pd.DataFrame(rows, columns=["date", "spend_usd", "gmv_usd"])
    df["date"] = df["date"].str[5:]  # 'YYYY-MM-DD' -> 'MM-DD'
    return _slice(df, start, end)

def parse_ttms_serums_xlsx(path, start=None, end=None):
    """
    解析 TTMS · Serums & Essences 导出 xlsx。
    需要的表头：'日期'、'短视频GMV'、'直播GMV'、'商品卡GMV'（单位千USD）。
    返回 DataFrame[date, short_k, live_k, card_k]，自动跳过『区间最大值』汇总行。
    """
    import openpyxl, pandas as pd
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    hdr = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    def col(*keys):
        for i, h in enumerate(hdr):
            if h and all(k in str(h) for k in keys):
                return i + 1
        raise KeyError(f"列未找到: {keys}")
    c_d = col("日期"); c_s = col("短视频"); c_l = col("直播"); c_c = col("商品卡")
    rows = []
    for r in range(2, ws.max_row + 1):
        d = ws.cell(r, c_d).value
        if not d or not re.match(r"^\d{1,2}-\d{1,2}", str(d).strip()):
            continue  # 跳过『区间最大值』等汇总行
        rows.append((str(d).strip(),
                     float(ws.cell(r, c_s).value),
                     float(ws.cell(r, c_l).value),
                     float(ws.cell(r, c_c).value)))
    df = pd.DataFrame(rows, columns=["date", "short_k", "live_k", "card_k"])
    return _slice(df, start, end)

def _slice(df, start, end):
    if start:
        df = df[df["date"] >= start]
    if end:
        df = df[df["date"] <= end]
    return df.sort_values("date").reset_index(drop=True)

def load_kans_daily(path, start=None, end=None):
    """读 KANS 日度数据。.csv 需含 date,spend_usd,gmv_usd；.xlsx 走 Campaign 解析器。"""
    import pandas as pd
    df = _read_table(path)
    if df is None:
        return parse_kans_campaign_xlsx(path, start, end)
    return _slice(df, start, end)

def load_market_daily(path, start=None, end=None):
    """读大盘日度数据。.csv 需含 date,short_k,live_k,card_k；.xlsx 走 TTMS 解析器。"""
    import pandas as pd
    df = _read_table(path)
    if df is None:
        return parse_ttms_serums_xlsx(path, start, end)
    return _slice(df, start, end)

def style_axes(ax, hide=("top", "right")):
    for s in hide:
        ax.spines[s].set_visible(False)
