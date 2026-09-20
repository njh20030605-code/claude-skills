# -*- coding: utf-8 -*-
"""Step9 · 「④ UV价值 分维度」sheet 生成器 —— 每期必做

UV 是全套报告里跨章节复用最多的指标，但四处分母不同：
    概览表 / 日度底表 → GMV-MAX 口径（Gross revenue ÷ 广告直播观看）
    流量结构 5 段     → CLP 口径（Attributed GMV ÷ CLP Views）
    主播表 / 时段表   → 主播表口径（GMV Host ÷ Views）
    入口表           → Traffic-Source 口径（成交GMV ÷ 观看）
三者数值不可跨口径比（8月W2 实测 1.698 / 2.107 / 1.700），同一张表不许混用。

🔴 加权 UV 必须 Σ GMV ÷ Σ Views，不能对各行 UV 取算术平均。
🔴 用户问「UV 有变化吗」时，总量环比往往看不出东西（本期只 −1.1%），
   必须给 分入口 + 分时段 + 分主播 三层拆解。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import PERIOD, W1L, W2L, OUT
import openpyxl, pandas as pd, numpy as np
from openpyxl.styles import Font, PatternFill
from style import *

# ============ 每期填这里（上期值从上期底表/报告取，本期从当期原始文件算） ============
TOTALS = [  # (口径名, 上期UV, 本期UV, 备注)
    ('CLP 口径（Attributed GMV ÷ CLP Views）',            None, None, '流量结构章节用这个'),
    ('GMV-MAX 口径（Gross revenue ÷ 广告直播观看）',        None, None, '概览表/日度底表用这个'),
    ('主播表口径（GMV Host ÷ Views）',                     None, None, '主播/时段表用这个'),
    ('★ 对平销周锚点（GMV-MAX 口径）',                      None, None, '上期含大促时必加这行'),
]
ENTRY  = []   # (入口, 上期UV, 本期UV, 备注)  ← 从 entry.csv + 上期 Step9 sheet② 取
PERIODS= []   # (班次, 上期UV, 本期UV, 备注)  ← 从 period.csv 取
HOSTS  = []   # (主播(时长h), 上期UV, 本期UV, 备注) ← 从 host_pk.csv 取，按本期时长降序

def wuv(gmv_series, views_series):
    """加权 UV = Σ GMV ÷ Σ Views —— 不要对各行 UV 取算术平均"""
    return gmv_series.sum() / views_series.sum()

def wuv_from_uv(gmv_wan_series, uv_series):
    """只有 GMV(万) 与 UV 时：Views = GMV元 ÷ UV，再求和"""
    views = (gmv_wan_series * 1e4 / uv_series).sum()
    return gmv_wan_series.sum() * 1e4 / views

def build(path=None):
    path = path or f'{OUT}/KANS_VN_{PERIOD}_Step9_流量结构.xlsx'
    wb = openpyxl.load_workbook(path) if os.path.exists(path) else openpyxl.Workbook()
    if '④ UV价值 分维度' in wb.sheetnames:
        del wb['④ UV价值 分维度']
    ws = wb.create_sheet('④ UV价值 分维度')
    title(ws, 1, f'UV价值（GMV ÷ 观看）· 分维度｜本期 {W2L} vs 上期 {W1L}', 5)
    ws.cell(row=2, column=1, value='UV价值 = GMV元 ÷ Views。三个总量口径分母不同，数值不可跨口径比，只看各自的环比方向。')
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=5)
    ws.cell(row=2, column=1).font = Font(size=9, italic=True)
    r = [3]
    def sec(t):
        ws.cell(row=r[0], column=1, value=t).font = Font(bold=True, color='C00000')
        ws.merge_cells(start_row=r[0], start_column=1, end_row=r[0], end_column=5); r[0] += 1
        for i, h in enumerate(['维度', '上期', '本期', '环比', '备注'], 1):
            ws.cell(row=r[0], column=i, value=h)
        hdr(ws, r[0], 5); r[0] += 1
    def row(n, a, b, note=''):
        ws.cell(row=r[0], column=1, value=n)
        if a is not None: ws.cell(row=r[0], column=2, value=a).number_format = '0.000'
        ws.cell(row=r[0], column=3, value=b).number_format = '0.000'
        if a:
            c = ws.cell(row=r[0], column=4, value=b/a-1); c.number_format = '+0.0%;-0.0%'; pct_color(c, b/a-1)
        else:
            ws.cell(row=r[0], column=4, value='新增')
        ws.cell(row=r[0], column=5, value=note)
        for j in range(1, 6): ws.cell(row=r[0], column=j).border = BORDER
        r[0] += 1
    for lbl, data in [('① 总量 · 三个口径', TOTALS), ('② 分入口（成交GMV ÷ 观看）', ENTRY),
                      ('③ 分时段（主播表口径）', PERIODS), ('④ 分主播（主播表口径，按本期时长降序）', HOSTS)]:
        if not data: continue
        sec(lbl)
        for t in data: row(*t)
        r[0] += 1
    note_block(ws, r[0], [
        '【读法】总量环比往往看不出东西，信息量在分维度：哪个主播 / 哪个班次 / 哪个入口在拉、哪个在拖。',
        '【别跨口径比数值】CLP / GMV-MAX / 主播表三个分母不同，同一张表里不要混用；只看各自环比方向。',
        '【加权 UV】= Σ GMV ÷ Σ Views，不是对各行 UV 取算术平均。',
        '【UV ≡ Watch GPM ÷ 1000】5 段图里两行都要放，UV 行标签写明同源。',
    ], 5)
    widths(ws, [40, 12, 12, 11, 52])
    wb.save(path)
    print('saved', path)

if __name__ == '__main__':
    build()
