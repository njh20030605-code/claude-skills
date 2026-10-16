#!/usr/bin/env python3
"""Top N 素材数据 → 统计 + 区间图 SVG（可直接 <whiteboard type="svg" path="@./bench.svg"> 插进飞书）。

用法：python3 svg_bench.py <rows.csv> <输出目录> [--index] [--title 韩束爆款数据 Benchmark] [--sample 样本说明]

rows.csv 列（每行一条素材，已按统一时间段取数，见 references/data-benchmark.md）：
  name,spend,roi,netroi,ctr,cvr,s3,finish
  （ctr/cvr/s3/finish 为百分数数值，如 2.80 表示 2.80%）
--index：对外脱敏版，所有数值换成指数（中位数 = 100），不出现真实数值。

输出：<目录>/bench.svg、<目录>/stats.json（P25/中位/P75/最值、与 ROI 的秩相关）。
「怎么用」那一列的文字需要按本批数据人工写进 stats.json 的 tips 后再跑一次（见 --tips）。
"""
import argparse, csv, html, json, os


def q(v):
    v = sorted(v); n = len(v)
    def p(x):
        k = (n - 1) * x; f = int(k); c = min(f + 1, n - 1)
        return v[f] + (v[c] - v[f]) * (k - f)
    return dict(min=v[0], p25=p(.25), med=p(.5), p75=p(.75), max=v[-1])


def rank(x):
    s = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
    for k, i in enumerate(s): r[i] = k + 1
    return r


def spearman(a, b):
    rx, ry = rank(a), rank(b); n = len(a); mx = sum(rx) / n; my = sum(ry) / n
    num = sum((p - mx) * (t - my) for p, t in zip(rx, ry))
    den = (sum((p - mx) ** 2 for p in rx) * sum((t - my) ** 2 for t in ry)) ** .5
    return round(num / den, 2)


METRICS = [('roi', 'ROI', '', '#6D5BD0'), ('netroi', '净成交 ROI', '', '#6D5BD0'), ('ctr', '点击率', '%', '#3E7BFA'),
           ('cvr', '转化率', '%', '#3E7BFA'), ('s3', '千川 3 秒完播率', '%', '#14A3A3'), ('finish', '完播率', '%', '#14A3A3')]
LIGHT = {'#6D5BD0': '#E3DEFA', '#3E7BFA': '#D6E4FF', '#14A3A3': '#CDEFEF'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv'); ap.add_argument('out')
    ap.add_argument('--index', action='store_true')
    ap.add_argument('--title', default='爆款数据 Benchmark')
    ap.add_argument('--sample', default='')
    ap.add_argument('--tips', help='JSON：{"roi": "及格 ≥ 2.3，优秀 ≥ 2.6", ...}')
    a = ap.parse_args()
    rows = [{k: (float(v) if k != 'name' else v) for k, v in r.items()} for r in csv.DictReader(open(a.csv, encoding='utf-8'))]
    os.makedirs(a.out, exist_ok=True)
    st = {k: q([r[k] for r in rows]) for k, *_ in METRICS}
    st['spend'] = q([r['spend'] for r in rows])
    corr = {k: spearman([r[k] for r in rows], [r['roi'] for r in rows]) for k in ['s3', 'ctr', 'cvr', 'finish']}
    tips = json.load(open(a.tips, encoding='utf-8')) if a.tips else {}
    json.dump(dict(stats=st, corr_with_roi=corr, n=len(rows)), open(f'{a.out}/stats.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    X0, X1 = 230, 700
    title = a.title + ('（指数）' if a.index else '')
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1110 572">',
           f'<text x="40" y="40" font-size="22" font-weight="bold" fill="#1F2329">{title}</text>',
           f'<text x="40" y="66" font-size="13" fill="#646A73">{a.sample}{"；数据已脱敏，各指标按中位数 = 100 换算" if a.index else ""}</text>',
           '<rect x="230" y="84" width="34" height="12" rx="3" fill="#C9C2F2"/><text x="270" y="95" font-size="12" fill="#646A73">中间 50%（P25～P75）</text>',
           f'<circle cx="420" cy="90" r="6" fill="#1F2329"/><text x="432" y="95" font-size="12" fill="#646A73">{"中位数 = 100" if a.index else "中位数"}</text>',
           '<text x="530" y="95" font-size="12" fill="#646A73">两端数字 = 最小值 / 最大值</text>',
           '<text x="772" y="95" font-size="13" font-weight="bold" fill="#1F2329">怎么用</text>']
    y = 130
    for k, name, unit, c in METRICS:
        s = st[k]
        vals = [s[x] for x in ('min', 'p25', 'med', 'p75', 'max')]
        if a.index:
            vals = [v / s['med'] * 100 for v in vals]
            fmt = lambda v: f'{v:.0f}'
        else:
            fmt = (lambda v: f'{v:.2f}') if unit == '' else (lambda v: f'{v:.1f}%')
        mn, p25, md, p75, mx = vals
        sc = lambda v: X0 + (v - mn) / (mx - mn) * (X1 - X0)
        out += [f'<text x="40" y="{y + 5}" font-size="15" font-weight="bold" fill="#1F2329">{name}</text>',
                f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="#DEE0E3" stroke-width="6" stroke-linecap="round"/>',
                f'<rect x="{sc(p25):.1f}" y="{y - 11}" width="{sc(p75) - sc(p25):.1f}" height="22" rx="6" fill="{LIGHT[c]}" stroke="{c}"/>',
                f'<circle cx="{sc(md):.1f}" cy="{y}" r="8" fill="{c}"/>',
                f'<text x="{sc(md):.1f}" y="{y - 18}" font-size="14" font-weight="bold" fill="{c}" text-anchor="middle">{fmt(md)}</text>',
                f'<text x="{X0 - 8}" y="{y + 5}" font-size="11" fill="#8F959E" text-anchor="end">{fmt(mn)}</text>',
                f'<text x="{X1 + 8}" y="{y + 5}" font-size="11" fill="#8F959E">{fmt(mx)}</text>',
                f'<text x="{sc(p25):.1f}" y="{y + 28}" font-size="11" fill="#646A73" text-anchor="middle">{fmt(p25)}</text>',
                f'<text x="{sc(p75):.1f}" y="{y + 28}" font-size="11" fill="#646A73" text-anchor="middle">{fmt(p75)}</text>',
                f'<text x="772" y="{y + 5}" font-size="13" fill="#1F2329">{html.escape(tips.get(k, ""), quote=False)}</text>']
        y += 62
    mxc = max(abs(v) for v in corr.values())
    out += [f'<rect x="40" y="{y - 10}" width="1030" height="64" rx="12" fill="#FFF7E8" stroke="#F5A623"/>',
            f'<text x="60" y="{y + 16}" font-size="14" font-weight="bold" fill="#8A5A00">{html.escape(tips.get("finding_title", "关键发现"), quote=False)}</text>',
            f'<text x="60" y="{y + 40}" font-size="13" fill="#1F2329">{html.escape(tips.get("finding", (f"在这批样本里，3 秒完播、点击率、转化率、完播率高低和 ROI 高低基本没有关系（秩相关都在 ±{mxc} 以内）：前端指标只用来判断冷启动能不能跑起来，不能拿来预测 ROI。" if mxc < 0.3 else f"有指标和 ROI 的秩相关达到 {mxc}，看 stats.json 的 corr_with_roi 后在 tips.json 里写 finding。")), quote=False)}</text>', '</svg>']
    open(f'{a.out}/bench.svg', 'w', encoding='utf-8').write('\n'.join(out))
    print(json.dumps(dict(corr_with_roi=corr, roi=st['roi']), ensure_ascii=False))


if __name__ == '__main__':
    main()
