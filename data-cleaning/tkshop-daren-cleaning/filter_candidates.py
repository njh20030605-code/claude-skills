#!/usr/bin/env python3
"""对清洗后的 tkshop达人信息 做达人初筛。"""

import argparse
import re

import pandas as pd

PLACEHOLDER = {'-', '--', '', 'nan', 'None'}


def to_num(cell):
    """把 '8497' / '524700+' / '1.99' 这类转成数字；'-' 等占位符 -> None。
    开区间 '524700+' 按其下界参与比较（下界已满足阈值就必然满足）。"""
    if pd.isna(cell):
        return None
    s = str(cell).strip().replace(',', '')
    if s in PLACEHOLDER:
        return None
    m = re.search(r'\d+(?:\.\d+)?', s)
    return float(m.group()) if m else None


def filter_candidates(df, min_orders=100, min_price=131800,
                      max_male=60, min_video_share=50, min_skincare=50):
    n = to_num
    orders = df['近一个月成交件数'].apply(n)
    price = df['客单价(₫)'].apply(n)
    male = df['男生占比'].apply(n)
    video = df['视频'].apply(n)
    live = df['直播'].apply(n).fillna(0)
    skincare = df['美妆个护占比'].apply(n)

    mask = (
        orders.ge(min_orders).fillna(False)
        & price.ge(min_price).fillna(False)
        & male.le(max_male).fillna(False)
        & video.ge(min_video_share).fillna(False)
        & (video.fillna(-1) > live)
        & skincare.gt(min_skincare).fillna(False)
    )

    # 逐条件命中数，便于核查漏斗
    report = {
        f'近一个月成交件数 ≥ {min_orders}': int(orders.ge(min_orders).fillna(False).sum()),
        f'客单价 ≥ {min_price}': int(price.ge(min_price).fillna(False).sum()),
        f'男生占比 ≤ {max_male}%': int(male.le(max_male).fillna(False).sum()),
        f'视频GMV占比 ≥ {min_video_share}% 且 > 直播': int(
            (video.ge(min_video_share).fillna(False) & (video.fillna(-1) > live)).sum()),
        f'美妆个护占比 > {min_skincare}%': int(skincare.gt(min_skincare).fillna(False).sum()),
    }
    return df[mask].reset_index(drop=True), report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--drop-cols', nargs='*', default=['平均视频播放量.1(次)'])
    ap.add_argument('--min-orders', type=int, default=100)
    ap.add_argument('--min-price', type=float, default=131800)
    ap.add_argument('--max-male', type=float, default=60)
    ap.add_argument('--min-video-share', type=float, default=50)
    ap.add_argument('--min-skincare', type=float, default=50)
    args = ap.parse_args()

    df = pd.read_excel(args.input)
    before = len(df)

    for c in args.drop_cols:
        if c in df.columns:
            df = df.drop(columns=c)
            print(f'已删除列: {c}')

    out, report = filter_candidates(
        df, args.min_orders, args.min_price, args.max_male,
        args.min_video_share, args.min_skincare)

    print('\n单条件命中数:')
    for k, v in report.items():
        print(f'  {k:38s} {v:4d} / {before}')
    print(f'\n全部条件同时满足: {len(out)} / {before}')

    out.to_excel(args.output, index=False, sheet_name='初筛达人')
    print(f'已保存 {args.output}，{len(out)} 行，{len(out.columns)} 列')


if __name__ == '__main__':
    main()
