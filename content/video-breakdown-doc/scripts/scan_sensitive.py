#!/usr/bin/env python3
"""对外版脱敏扫描：拉飞书文档全文，找出可能残留的内部数据。

用法：python3 scan_sensitive.py <docToken> [--profile personal]
命中项逐条人工判断：视频里的广告原话（如「我拿出1万单」）、官方规则、举例价位可以保留；
消耗金额、具体 ROI/转化率/完播率数值、素材 ID、内部系统名必须改掉。
"""
import json, re, subprocess, sys

doc = sys.argv[1]
profile = sys.argv[sys.argv.index('--profile') + 1] if '--profile' in sys.argv else None
cmd = ['lark-cli'] + (['--profile', profile] if profile else []) + ['docs', '+fetch', '--as', 'user', '--doc', doc]
c = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)['data']['document']['content']
t = re.sub(r'<source[^>]*/>', '', c)
t = re.sub(r'<whiteboard[^>]*>.*?</whiteboard>', '', t)
t = re.sub(r'<[^>]+>', ' ', t)
pats = {
    '百分比数值': r'\d+\.\d+\s*%',
    '金额（万）': r'\d+(\.\d+)?\s*万',
    'ROI 数值': r'ROI\s*[≥<>＜≤]?\s*\d\.\d',
    '小数（疑似 ROI）': r'(?<![\d.～~-])[1-9]\.\d\d(?![\d.]|\s*[～~-]\s*\d|\s*秒)',   # 不抓「5.75～12.75 秒」这类时间戳
    '元': r'\d+\s*元',
    '素材 ID': r'\b\d{8}\b',
    '内部系统名': r'XX管家|XX后台',  # 换成你们内部系统的名字
    'CPM/客单': r'(CPM|客单价?)\s*[约≈]?\s*\d',
}
n = 0
for name, p in pats.items():
    for m in re.finditer(p, t):
        n += 1
        print(f'[{name}]', t[max(0, m.start() - 40):m.end() + 25].replace('\n', ' '))
print(f'共 {n} 处命中（画板里的文字不在扫描范围内，画板要单独看导出图）')
