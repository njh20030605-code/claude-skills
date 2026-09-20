# -*- coding: utf-8 -*-
"""
common.py —— 越南美妆类目竞争格局分析 · 公共模块

所有图表脚本从这里 import，保证字体、配色、口径、品牌归并规则完全一致。

核心口径（改动前先读 references/pitfalls.md）：
  1. 大盘 = 两周都在 Top200 的店铺交集，不是各周 Top200 全量。
  2. 渠道占比分母 = 五渠道之和，不是总 GMV（平台字段与总 GMV 不闭合）。
  3. 多店品牌只在「两周所有门店都在榜」时才合并，否则按店铺计。
"""
import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# ---------------------------------------------------------------- 字体
_CJK = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]


def setup_font():
    name = None
    for p in _CJK:
        if os.path.exists(p):
            fm.fontManager.addfont(p)
            if name is None:
                name = fm.FontProperties(fname=p).get_name()
    if name is None:
        for f in fm.findSystemFonts():
            if any(k in f.lower() for k in ("cjk", "wqy", "hei")):
                fm.fontManager.addfont(f)
                name = fm.FontProperties(fname=f).get_name()
                break
    plt.rcParams["font.family"] = name or "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 170
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["axes.edgecolor"] = "#CCCCCC"
    return name


# ---------------------------------------------------------------- 配色 / 常量
CH = ["aff_video", "self_video", "self_live", "aff_live", "shop"]
NM = ["达人视频", "店播短视频", "店铺自播", "达人直播", "商城"]
PAL = ["#4E79A7", "#A0CBE8", "#59A14F", "#C0392B", "#F1A340"]
C_NOW, C_PRE, C_KANS, C_MKT = "#C0392B", "#A6ACAF", "#E8A33D", "#4E79A7"
C_UP, C_DN = "#C0392B", "#1F7A45"      # 上升红 / 下降绿（中文财务习惯）
KANS = "Kans Official Vietnam"
DEFAULT_RATE = 6.75                     # 兜底汇率；正式出图务必用当日实时汇率

# 平台导出表头 → 内部字段
COLMAP = {
    "Store Name": "store",
    "GMV (USD)": "gmv",
    "Affiliate Video GMV(USD)": "aff_video",
    "Self-Account Video GMV(USD)": "self_video",
    "Self-Account Live GMV(USD)": "self_live",
    "Affiliate Live GMV(USD)": "aff_live",
    "Shop Tab GMV(USD)": "shop",
    "Self-Account Live AOV (Main Order)(USD)": "aov",
}


def read_export(path):
    """读平台导出（TSV/CSV/xlsx）。按表头名定位列，列序变了也能读。"""
    if str(path).lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        with open(path, encoding="utf-8-sig") as f:
            head = f.readline()
        sep = "\t" if head.count("\t") >= head.count(",") else ","
        df = pd.read_csv(path, sep=sep)
    df.columns = [str(c).strip() for c in df.columns]
    ren, miss = {}, []
    for raw, key in COLMAP.items():
        hit = [c for c in df.columns if c.replace(" ", "") == raw.replace(" ", "")]
        if hit:
            ren[hit[0]] = key
        elif key != "aov":
            miss.append(raw)
    if miss:
        raise SystemExit(f"缺少必需列：{miss}\n实际列：{list(df.columns)}")
    df = df.rename(columns=ren)[[v for v in ren.values()]]
    df["store"] = df["store"].astype(str).str.strip()
    for c in df.columns:
        if c != "store":
            df[c] = (df[c].astype(str).str.replace(",", "", regex=False)
                     .str.replace("$", "", regex=False).str.strip()
                     .replace({"": "0", "nan": "0", "-": "0"}).astype(float))
    if "aov" not in df.columns:
        df["aov"] = 0.0
    df = df[df["store"].ne("") & df["gmv"].gt(0)]
    return df.sort_values("gmv", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------- 品牌归并
# 只列「同一品牌在越南开了多个店铺」的情况。合并与否由 build() 按在榜情况决定。
MULTI_STORE = {
    "珂拉琪": ["COLORKEY LUMINOUS VIỆT NAM", "COLORKEY COSMETICS VIỆT NAM",
            "COLORKEY VIỆT NAM", "COLORKEY ROSÉ VIỆT NAM"],
    "联合利华": ["Unilever Beauty", "Unilever - Chăm Sóc Cá Nhân"],
    "宝洁": ["P&G Beauty Việt Nam - eMesa", "P&G Chăm Sóc Cá Nhân - eMesa"],
    "蜜丝婷": ["MISTINE BWG VIETNAM", "MISTINE BWG VN"],
    "MTN": ["MTN COSMETICS", "MTN Personal Care"],
    "Jasmeen": ["Jasmeen White & Fresh", "Jasmeen.VN"],
    "Mooekiss": ["Mooekiss Việt Nam", "Mooekiss VN"],
    "AZTK": ["AZTK VN", "AZTK VIETNAM"],
    "Dunté香水": ["Dunté Perfume 69", "Dunté Perfume Store", "Perfume Dunté"],
    "Blanc香水": ["Blanc Perfume", "Blanc Perfume II"],
    "乐敦": ["ROHTO SKINCARE", "Rohto Official by TNT"],
    "太阳星药业": ["saothaiduongpharma", "Sao Thái Dương Miền Nam"],
    "Salonkey": ["Salonkey", "SalonkeyPro"],
    "Cottonday": ["Cottonday SEA", "Cottonday Store"],
    "MILAI": ["MILAI Vietnam", "MIlai Nhật ký"],
    "Charme香水": ["NUOC HOA CHARME VINH HIEN", "Charme Perfume VN"],
    "Tú Beauté": ["Tú Beauté", "Tú Beauté - Dược Mỹ Phẩm"],
}

# 店铺 → 展示用中文名。带 ? = 归属未核实，出图/写结论时必须保留问号或单独分组。
# 完整规则见 references/brand_map.md
CN_NAME = {
    KANS: "韩束", "Carslan.VN": "卡姿兰", "Judydoll Vietnam": "橘朵",
    "Flower Knows V N": "花知晓", "Florasis Hoa Tây Tử": "花西子",
    "FOCALLURE SHOP": "菲鹿儿", "Lanbena.vn": "兰蓓娜", "MENOW Mall": "蜜诺MeNow",
    "Enchen.vn": "映趣Enchen", "Hexze Việt Nam": "赫兹Hexze", "WIS.VN": "WIS",
    "Ulike Việt Nam Store": "Ulike", "COCLEAR & FLYCO": "飞科FLYCO",
    "usmile Vietnam Shop": "笑容加usmile", "moodyofficialstore": "moody",
    "Chenglovehair": "Chenglovehair",
    "Unilever Beauty": "联合利华美妆", "Unilever - Chăm Sóc Cá Nhân": "联合利华个护",
    "P&G Beauty Việt Nam - eMesa": "宝洁美妆", "P&G Chăm Sóc Cá Nhân - eMesa": "宝洁个护",
    "COLORKEY LUMINOUS VIỆT NAM": "珂拉琪LUMINOUS", "COLORKEY COSMETICS VIỆT NAM": "珂拉琪COSMETICS",
    "COLORKEY VIỆT NAM": "珂拉琪VN", "COLORKEY ROSÉ VIỆT NAM": "珂拉琪ROSÉ",
    "DrCeutics Official Store": "DrCeutics", "MISTINE BWG VN": "蜜丝婷",
    "CeraVe Việt Nam": "适乐肤", "L'oreal Paris Việt Nam": "巴黎欧莱雅",
    "La Roche-Posay Việt Nam": "理肤泉", "Kiehl's Việt Nam": "科颜氏",
    "Obagi Vietnam": "欧邦琪", "Murad.vietnam": "慕拉德",
    "Anessa Official Store": "安热沙", "Estée Lauder Vietnam": "雅诗兰黛",
    "YSL Beauty Vietnam": "圣罗兰", "Lancome Vietnam": "兰蔻",
    "Maybelline New York": "美宝莲", "Garnier Vietnam": "卡尼尔",
    "NIVEA Việt Nam": "妮维雅", "Eucerin Việt Nam": "优色林",
    "Bioderma Vietnam": "贝德玛", "L'Occitane VN": "欧舒丹",
    "Kérastase Việt Nam": "卡诗", "SVR Việt Nam": "舒唯雅SVR",
    "Paula's Choice Việt Nam": "宝拉珍选", "KAO VIETNAM": "花王",
    "Sulwhasoo Vietnam": "雪花秀", "The Whoo Vietnam": "后",
    "Dr.G Việt Nam": "Dr.G", "3CE STYLENANDA VIETNAM": "3CE",
    "Romand Vietnam": "romand", "Torriden VN": "Torriden",
    "d'Alba piedmont VN": "d'Alba", "Caryophy Vietnam": "Caryophy",
    "MISTINE BWG VIETNAM": "蜜丝婷", "Dr.Pong Vietnam": "Dr.Pong",
    "Colgate - Palmolive VN": "高露洁棕榄", "Kotex Vietnam": "高洁丝",
    "L'Oréal Professionnel Việt Nam": "欧莱雅专业美发",
    "Wipro Việt Nam": "维布络", "Hasaki Vietnam Official": "Hasaki",
    "lixibox vietnam": "Lixibox", "HappySkin Vietnam": "HappySkin",
    "Guardian Store": "Guardian", "Tuyển chọn Long Châu": "Long Châu",
    "Nhà thuốc Nhân Dân số 1": "人民第一药房",
    "Dược Phẩm Hoa Linh": "花玲制药", "THORAKAO STORE": "Thorakao",
    "Sắc Ngọc Khang": "Sắc Ngọc Khang", "Cocoon Vietnam": "Cocoon",
    "Cỏ Mềm": "Cỏ Mềm", "XMEN GIAN HÀNG CHÍNH HÃNG": "X-Men",
    "Romano Việt Nam": "Romano", "The Originote Việt Nam": "The Originote",
    "Grace and Glow Việt Nam": "Grace and Glow",
    "Geek&Gorgeous Vietnam": "Geek&Gorgeous",
    "Blemil Việt Nam": "Blemil", "Simple Skincare Đơn Giản": "Simple",
    "TRESemmé Vietnam": "TRESemmé", "Make P:rem": "Make P:rem",
    "CNP Laboratory VN": "CNP", "AHC Vietnam": "AHC",
    "So Natural Việt Nam": "So Natural", "Tiam Viet Nam": "Tiam",
    # 以下归属待核（多为疑似中国跨境卖家），出图时保留 ?
    "LUCENBASE COSMETIC.VN": "Lucenbase?", "KOAI VN": "KOAI?",
    "Socus Sea VN": "Socus?", "URMINE VN STORE": "URMINE?",
    "Mooekiss Việt Nam": "Mooekiss?", "Yomani Mall Vietnam": "Yomani?",
    "LILYSTAR-VN": "Lilystar?", "LUNYS STORE": "Lunys?",
    "Lubylab Official Mall": "Lubylab?", "AZTK VN": "AZTK?",
    "Sellion VN": "Sellion?", "KEYSHU VIỆT NAM": "Keyshu?",
    "OSITREE VN": "Ositree?", "Teashell VN": "Teashell?",
    "Santalwisp-VN": "Santalwisp?", "JMCY Cosmetics VN": "JMCY?",
    "kingbabyvn": "Kingbaby?", "QUSTERE VN": "Qustere?",
    "EGUOO VIỆT NAM": "Eguoo?", "Censto Vietnam": "Censto?",
    "PINKTWO-VN": "PinkTwo?", "ROCKSWEET-VN": "Rocksweet?",
    "MISECR Vietnam": "Misecr?", "UILICY-Official": "UILICY?",
}

# 图2「中国品牌梯队」固定名单（归属已确认）。新品牌进 Top30 时手工加进来。
CN_TIER = ["珂拉琪", "卡姿兰", "花知晓", "韩束", "橘朵", "菲鹿儿", "花西子", "兰蓓娜"]


def label(key):
    return CN_NAME.get(key, key)


# ---------------------------------------------------------------- 口径构建
def build(cur, pri, merge=True):
    """
    返回 dict：
      cur/pri        : 原始两周（店铺层，按 GMV 降序，含 rank 列）
      inter          : 两周都在榜的店铺交集（店铺层，可比口径）
      brand          : 品牌层（多店已合并，仅合并两周全在榜的组），含 chg / share / dshare
      market         : 大盘汇总（基于 inter）
      merged_groups  : 实际合并了哪些品牌
      skipped_groups : 因单周掉榜而未合并的品牌（截断偏差，写结论要提）
    """
    for d in (cur, pri):
        d["rank"] = np.arange(1, len(d) + 1)
    inter = cur.merge(pri, on="store", suffixes=("_1", "_0"))

    s1 = np.array([inter[c + "_1"].sum() for c in CH], float)
    s0 = np.array([inter[c + "_0"].sum() for c in CH], float)
    market = dict(
        n=len(inter),
        gmv1=inter["gmv_1"].sum(), gmv0=inter["gmv_0"].sum(),
        gmv_chg=(inter["gmv_1"].sum() / inter["gmv_0"].sum() - 1) * 100,   # 总GMV口径
        ch1=s1, ch0=s0,
        share1=s1 / s1.sum() * 100, share0=s0 / s0.sum() * 100,
        ch_chg=(s1 / s0 - 1) * 100,
        chsum_chg=(s1.sum() / s0.sum() - 1) * 100,                        # 五渠道合计口径
        thr1=cur["gmv"].min(), thr0=pri["gmv"].min(),
        new_in=len(set(cur.store) - set(pri.store)),
        dropped=len(set(pri.store) - set(cur.store)),
    )

    c1, c0 = cur.set_index("store"), pri.set_index("store")
    merged_groups, skipped, rows, seen = [], [], [], set()
    owner = {}
    if merge:
        for g, ss in MULTI_STORE.items():
            if all(s in c1.index and s in c0.index for s in ss):
                merged_groups.append((g, ss))
                for s in ss:
                    owner[s] = g
            elif sum(s in c1.index for s in ss) + sum(s in c0.index for s in ss) > 2:
                skipped.append((g, [s for s in ss if s in c1.index or s in c0.index]))

    for s in inter["store"]:
        key = owner.get(s, s)
        if key in seen:
            continue
        seen.add(key)
        ss = dict(merged_groups).get(key, [s])
        a1 = np.array([c1.loc[ss, c].sum() for c in CH], float)
        a0 = np.array([c0.loc[ss, c].sum() for c in CH], float)
        g1, g0 = c1.loc[ss, "gmv"].sum(), c0.loc[ss, "gmv"].sum()
        nm = label(key) if key not in dict(merged_groups) else f"{key} ({len(ss)}店合计)"
        rows.append(dict(
            key=key, name=nm, stores=len(ss),
            rank1=int(c1.loc[ss, "rank"].min()), rank0=int(c0.loc[ss, "rank"].min()),
            gmv1=g1, gmv0=g0, chg=(g1 / g0 - 1) * 100,
            aov1=float(c1.loc[ss, "aov"].mean()), aov0=float(c0.loc[ss, "aov"].mean()),
            **{f"s1_{c}": v for c, v in zip(CH, a1 / a1.sum() * 100)},
            **{f"s0_{c}": v for c, v in zip(CH, a0 / a0.sum() * 100)},
            **{f"g1_{c}": v for c, v in zip(CH, a1)},
            **{f"g0_{c}": v for c, v in zip(CH, a0)},
        ))
    brand = pd.DataFrame(rows)
    for c in CH:
        brand[f"d_{c}"] = brand[f"s1_{c}"] - brand[f"s0_{c}"]
        brand[f"chg_{c}"] = np.where(brand[f"g0_{c}"] > 0,
                                     brand[f"g1_{c}"] / brand[f"g0_{c}"].replace(0, np.nan) - 1,
                                     np.nan) * 100
    brand = brand.sort_values("gmv1", ascending=False).reset_index(drop=True)
    return dict(cur=cur, pri=pri, inter=inter, brand=brand, market=market,
                merged_groups=merged_groups, skipped_groups=skipped)


def channel_percentile(inter, channel, value, base_min=5000):
    """某渠道增幅在「有基数店铺」中的分位。用来判断跑输大盘是不是加权口径造成的假信号。"""
    d = inter[inter[channel + "_0"] > base_min]
    g = d[channel + "_1"] / d[channel + "_0"] - 1
    return dict(n=len(d), median=g.median() * 100, mean=g.mean() * 100,
                pct=(g < value / 100).mean() * 100)


def wan(usd, rate):
    """美元 → 万元人民币"""
    return usd * rate / 1e4


def foot(fig, txt, y=-0.03, size=9):
    fig.text(0.005, y, txt, fontsize=size, color="#888888", ha="left", va="top")


def save(fig, out):
    fig.savefig(out)
    plt.close(fig)
    print("→", out)
