#!/usr/bin/env python3
"""Google 表导出的 xlsx → 每个 sheet 一个 JSON（二维数组，原始值）+ 原样 CSV 备份。

用法: python3 gsheet_xlsx_to_json.py <源.xlsx> <输出目录>

为什么用 xlsx：xlsx 给原始值（0.08 / 315.789），gviz/CSV 给显示值（8% / 316），
两种混用做比对会产生几千行假变更；gviz 还会静默截断（Red serum 1031 行只拉到 133 行）。
导出地址（用户已登录的浏览器里打开）:
  https://docs.google.com/spreadsheets/d/<ID>/export?format=xlsx
"""
import sys, os, json, csv, datetime, openpyxl

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(out, '原始sheet备份'), exist_ok=True)

def norm(v):
    if isinstance(v, (datetime.datetime, datetime.date)):
        return v.isoformat()
    return v

wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
for i, ws in enumerate(wb.worksheets):
    rows = [[norm(c) for c in r] for r in ws.iter_rows(values_only=True)]
    while rows and all(c in (None, '') for c in rows[-1]):
        rows.pop()
    safe = ws.title.replace('/', '_')
    json.dump(rows, open(os.path.join(out, f'{i:02d}_{safe}.json'), 'w'), ensure_ascii=False)
    with open(os.path.join(out, '原始sheet备份', f'{i:02d}_{safe}.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerows(rows)
    print(f'{i:02d}  {ws.title:<40} {len(rows):>6} 行  表头: {[c for c in (rows[0] if rows else []) if c][:12]}')
