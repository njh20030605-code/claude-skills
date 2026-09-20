#!/usr/bin/env python3
"""检索「投机之路」存档。

用法:
  python3 scripts/search.py 套保 对冲          # 关键词(任意命中)
  python3 scripts/search.py 抄底 --full        # 输出全文
  python3 scripts/search.py --theme 套利
  python3 scripts/search.py --since 2026-01-01 --until 2026-06-30
  python3 scripts/search.py --id 138 --id 254
  python3 scripts/search.py --list-themes
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(HERE, "..", "references", "posts.json")

# 主题 -> 关键词，用于粗筛；精确归类见 references/methodology.md
THEMES = {
    "仓位风控": ["身价", "仓位", "现金", "回撤", "止损", "心疼", "复利", "风险偏好"],
    "择时抄底": ["抄底", "急跌", "折扣", "耐心", "蹲", "闪崩", "清算", "便宜货", "correction"],
    "做空": ["做空", "空了", "裸空", "squeeze", "庄币"],
    "杠杆": ["杠杆", "梭哈", "爆仓", "All In", "all in"],
    "套利": ["套利", "spread", "溢价", "资费", "刷量", "空投", "对冲", "套保", "ADL", "adl", "薅"],
    "订单簿": ["做市商", "订单簿", "滑点", "bid", "延迟", "MM", "limit"],
    "持仓退出": ["退出", "平仓", "Supertrend", "supertrend", "止盈", "清仓", "减仓"],
    "股票配置": ["美股", "A股", "沪深", "GOOG", "NET", "国债", "ETF", "PUT", "期权", "TLT"],
    "安全防御": ["安全", "被盗", "api", "API", "密码", "1password", "提现", "转账", "冻结", "绑架", "签证", "身份"],
    "影响力": ["影响力", "喊单", "推特", "炫耀", "采访", "shill", "带货", "粉丝"],
    "商业人生": ["商机", "创业", "代理商", "试错", "时光机", "AI", "claude", "读书", "消费"],
    "宏观行业": ["Hyperliquid", "币安", "牛市", "熊市", "监管", "地缘", "放水", "叙事", "泡沫"],
}


def load():
    with open(POSTS, encoding="utf-8") as f:
        return json.load(f)


def show(p, full=False):
    d = (p.get("datetime") or "")[:10]
    print(f"\n{'='*70}\n#{p['id']}  {d}  https://t.me/journey_of_someone/{p['id']}")
    t = p.get("text", "")
    print(t if full or len(t) <= 400 else t[:400] + " …（--full 看全文）")
    if p.get("media"):
        print(f"[媒体 x{len(p['media'])}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words", nargs="*", help="关键词，任意命中即返回")
    ap.add_argument("--theme")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--id", type=int, action="append")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--list-themes", action="store_true")
    a = ap.parse_args()

    if a.list_themes:
        for k, v in THEMES.items():
            print(f"{k}: {' '.join(v)}")
        return

    posts = load()

    if a.id:
        for p in posts:
            if p["id"] in a.id:
                show(p, full=True)
        return

    words = list(a.words)
    if a.theme:
        key = next((k for k in THEMES if a.theme in k), None)
        if not key:
            print(f"未知主题 {a.theme}；可用：{'、'.join(THEMES)}", file=sys.stderr)
            sys.exit(1)
        words += THEMES[key]

    hits = []
    for p in posts:
        d = (p.get("datetime") or "")[:10]
        if a.since and (not d or d < a.since):
            continue
        if a.until and (not d or d > a.until):
            continue
        t = p.get("text", "")
        if words and not any(re.search(re.escape(w), t, re.I) for w in words):
            continue
        hits.append(p)

    for p in hits:
        show(p, a.full)
    print(f"\n{'-'*70}\n共 {len(hits)} 条 / 存档 {len(posts)} 条")


if __name__ == "__main__":
    main()
