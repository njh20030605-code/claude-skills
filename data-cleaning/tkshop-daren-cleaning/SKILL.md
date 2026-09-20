---
name: tkshop-daren-cleaning
description: "清洗/合并 TikTok Shop「tkshop达人信息」.xls 导出：K₫/M₫/万 单位换算、客单价区间取中位数、拆出直播视频占比与类目/性别/年龄占比、按达人名称去重合并；并支持按成交量/客单价/男女比/视频占比/护肤占比做达人初筛。"
---

## 触发条件（description 有 200 字符上限，触发词放这里）

任何满足以下之一的请求都走这个 skill：

- 上传或提到 `xxxx-xx-xx_tkshop达人信息.xls` / `tkshop达人信息` 这类文件
- 「清洗一下数据」「照上次那样洗」「把这几张表合并」「按达人昵称去重」
- 「初筛」「筛达人」「不符合的行直接删掉」「输出符合条件的」「M列删掉」
- 提到 K₫ / M₫ / Tr₫ / 万 这类越南、中文数量简写要转纯数字
- 提到要把「每个销售渠道的GMV」「粉丝性别占比」「粉丝年龄区间占比」这类
  多行百分比字段拆成独立列

## What this skill is for

The user periodically uploads TikTok Shop (tkshop) 达人 (influencer) export files named like
`2026-07-14_tkshop达人信息.xls`. These raw exports have messy Vietnamese/Chinese-locale
formatting: currency shorthand (K₫/M₫/Tr₫), view-count shorthand (万), and several fields that
pack multiple percentages into one multi-line text cell. This skill defines the exact cleaning
rules that were worked out (and debugged) with the user across several real files, so future
files get the same treatment without re-deriving the rules or re-making the same mistakes.

A reference implementation is bundled below as `clean_tkshop.py` — write it out and run it
rather than reimplementing the logic from scratch, since it already encodes fixes for real bugs
that were found in this data (see the "real bug" notes inside the script).

## Step 0: figure out which mode the user wants

There are two distinct things the user asks for, and they are NOT interchangeable — always
confirm (or infer from clear phrasing) which one is meant:

1. **合并去重 (`merge_dedupe`)** — merge two or more raw exports (possibly spanning several
   dates) into one table, dropping duplicate 达人名称 and keeping only the most recent
   date's row for each name. This is what "把这几张表合并，按达人昵称去重" means.
2. **原样清洗 (`keep_all`)** — just clean units/extract columns, don't drop or dedupe
   anything, even if names repeat inside the file. This is what "不用删除达人" /
   "按规则清洗，不去重" means. Use this as the default when the user gives you a single new
   file and doesn't ask for merging or de-duplication.

Get this wrong and you either silently discard rows the user wanted kept, or hand back
duplicates they wanted removed — so if the phrasing is genuinely ambiguous, ask rather than
guess.

## Step 0.5: reading the raw .xls

Some of these exports make `pandas.read_excel` (via `xlrd`) fail with:

```
UnicodeDecodeError: 'utf-16-le' codec can't decode bytes in position 0-1: unexpected end of data
```

This is not a corrupted file — `xlrd` just can't parse that particular file's shared-string
table. Convert it with LibreOffice first, then read the resulting `.xlsx`:

```bash
soffice --headless --convert-to xlsx --outdir <dir> <file.xls>
```

The bundled script already does this fallback automatically — you don't need to special-case it
yourself, just be aware of why it's there if you see that error.

## Step 1: run the cleaning script

Write the script below to a file (e.g. `clean_tkshop.py`) and run it with the appropriate mode.

```python
#!/usr/bin/env python3
"""
清洗 / 合并 tkshop达人信息 xls 导出文件。

用法:
  # 合并去重: 把多份导出文件（不同日期）合并成一张表，按"达人名称"去重，
  # 同名保留数据日期最新的一条；名称是占位符("-"/"--"/空)的行不参与去重。
  python clean_tkshop.py --mode merge_dedupe \
      --inputs 2026-07-14.xls 2026-07-15.xls 2026-07-16.xls \
      --output merged_dedup.xlsx

  # 原样清洗: 不合并、不去重，单个（或多个）文件原样清洗（哪怕文件内部有重复昵称也全部保留）。
  python clean_tkshop.py --mode keep_all \
      --inputs 2026-07-29.xls --output cleaned_20260729.xlsx

每个 --inputs 文件名里若包含形如 2026-07-14 的日期，会自动作为该文件的"数据日期"；
否则用 --date 手动指定（多文件时必须能从文件名解析出日期，否则报错）。
"""

import argparse
import re
import subprocess
from pathlib import Path

import pandas as pd

DATE_RE = re.compile(r'(20\d{2}-\d{2}-\d{2})')

WAN_COLS = ['平均视频播放量', '平均视频播放量.1', '视频数', '平均直播播放量']
CURRENCY_COLS = ['客单价', '近3个月的每个挂车视频的30天出单GMV数据']

RENAME_MAP = {
    '平均视频播放量': '平均视频播放量(次)',
    '平均视频播放量.1': '平均视频播放量.1(次)',
    '视频数': '视频数(个)',
    '平均直播播放量': '平均直播播放量(次)',
    '客单价': '客单价(₫)',
    '近3个月的每个挂车视频的30天出单GMV数据': '近3个月的每个挂车视频的30天出单GMV数据(₫)',
}

BEAUTY_LABELS = {'美妆个护', 'Beauty & Personal Care'}
MALE_LABELS = {'男性', 'Male'}
LIVE_LABELS = {'直播数据', 'LIVE'}
VIDEO_LABELS = {'视频数据', 'Video'}

PLACEHOLDER = {'-', '--', '', 'nan'}


# --------------------------------------------------------------------------
# 读取（部分 tkshop 导出的 .xls 会让 xlrd 报
# "UnicodeDecodeError: 'utf-16-le' codec can't decode ..."。
# 这不是文件真的坏了，是该文件的共享字符串表编码让 xlrd 处理不了，
# 用 LibreOffice 转成 .xlsx 就能正常读。）
# --------------------------------------------------------------------------
def read_tkshop_xls(path: Path) -> pd.DataFrame:
    try:
        return pd.read_excel(path)
    except Exception as e:
        if 'utf-16-le' not in str(e) and 'utf_16_le' not in str(e):
            raise
        converted = path.with_suffix('.xlsx')
        subprocess.run(
            ['soffice', '--headless', '--convert-to', 'xlsx',
             '--outdir', str(path.parent), str(path)],
            check=True, capture_output=True,
        )
        return pd.read_excel(converted)


def date_from_filename(path: Path):
    m = DATE_RE.search(path.name)
    return m.group(1) if m else None


# --------------------------------------------------------------------------
# 数值/单位清洗
# --------------------------------------------------------------------------
def round_clean(val: float):
    val = round(val, 4)
    if abs(val - round(val)) < 1e-6:
        return int(round(val))
    return round(val, 2)


def clean_wan_number(cell):
    """处理 平均视频播放量 / 平均直播播放量 / 视频数 里的 '万'（=10000）。
    小数点是标准的英文小数点（如 '10.81 万'）。'-'/'--' 视为缺失值，不是 0。"""
    if pd.isna(cell):
        return None
    s = str(cell).strip()
    if s in PLACEHOLDER:
        return None
    if '万' in s:
        val = float(s.replace('万', '').strip()) * 10000
    else:
        val = float(s)
    return round_clean(val)


_CURRENCY_TOKEN = re.compile(r'(\d+(?:,\d+)?)\s*(Tr|K|M)?\s*₫')
_CURRENCY_MULT = {'K': 1000, 'M': 1_000_000, 'Tr': 1_000_000, None: 1}


def clean_currency_cell(cell):
    """处理 客单价 / GMV数据 里的 K₫(千)/M₫(百万)/Tr₫(越南语"百万")。
    越南语数字格式里逗号是小数点（'1,8Tr ₫' = 1,800,000），不是千分位，
    所以是把逗号替换成小数点，不是去掉逗号。

    单元格可能是单值 / 闭区间("100K₫-500K₫") / 开区间("525300+")：
    - 闭区间 -> 换成区间中位数 (a+b)/2 的纯数字，这才是"换成纯数字"的真正意图，
      不是只留下区间下限。
    - 开区间（以 '+' 结尾）没有上界算不出中位数，只去掉单位、保留 '+'。
    - 单值原样转换成纯数字。

    从字符串里抠两个数字时，正则绝对不能允许数字前面带一个可选的 '-'
    （比如 r'-?\d+'），因为区间分隔符本身就是 '-'——"100000-500000" 这种字符串,
    一个贪心的 -? 会把它读成 "100000" 和 "-500000"，第二个数字变成负数，
    中位数直接算错（这是真实踩过的坑，务必避免）。
    """
    if pd.isna(cell):
        return None
    s = str(cell).strip()
    if s in PLACEHOLDER:
        return None

    def repl(m):
        num_str, unit = m.group(1), m.group(2)
        val = float(num_str.replace(',', '.')) * _CURRENCY_MULT.get(unit, 1)
        return str(round_clean(val))

    new_s = _CURRENCY_TOKEN.sub(repl, s).replace(' ', '')

    if new_s.endswith('+'):
        return new_s  # 开区间，保留原样（已去掉单位）

    nums = re.findall(r'\d+(?:\.\d+)?', new_s)  # 不允许负号！见上面的说明
    if len(nums) == 2:
        a, b = float(nums[0]), float(nums[1])
        return round_clean((a + b) / 2)
    if len(nums) == 1 and re.fullmatch(r'-?\d+(\.\d+)?', new_s):
        return round_clean(float(new_s))
    return new_s  # 无法识别的格式，原样返回，别静默丢数据


def clean_units(df: pd.DataFrame) -> pd.DataFrame:
    for c in WAN_COLS:
        if c in df.columns:
            df[c] = df[c].apply(clean_wan_number)
    for c in CURRENCY_COLS:
        if c in df.columns:
            df[c] = df[c].apply(clean_currency_cell)
    return df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns})


# --------------------------------------------------------------------------
# 从"label:value%\nlabel2:value2%..."格式的字段里提取子字段
# 注意同一个字段在不同批次的导出里，标签可能是中文也可能是英文
# （比如渠道字段里出现过 'LIVE'/'Video' 而不是 '直播数据'/'视频数据'，
#  类目字段里出现过 'Beauty & Personal Care' 而不是 '美妆个护'，
#  性别字段里出现过 'Male'/'Female'），两边都要认，不然会把大量有效数据
# 误判成缺失（这也是真实踩过的坑：曾经因为只认中文标签，红精华候选数被少算了近三成）。
# --------------------------------------------------------------------------
def parse_kv_lines(s):
    if pd.isna(s):
        return []
    s = str(s).strip()
    if s in PLACEHOLDER:
        return []
    out = []
    for line in re.split(r'[\n\r]+', s):
        line = line.strip()
        if not line or ':' not in line:
            continue
        label, val = line.split(':', 1)
        label = label.strip()
        val = val.strip().rstrip('%')
        try:
            val = float(val)
        except ValueError:
            continue
        out.append((label, val))
    return out


def _get(pairs, pred):
    for label, val in pairs:
        if pred(label):
            return val
    return None


def _age_prefix(prefix):
    def f(label):
        return label.replace(' ', '').replace('岁', '').startswith(prefix)
    return f


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    if '每个销售渠道的GMV' in df.columns:
        pairs = df['每个销售渠道的GMV'].apply(parse_kv_lines)
        idx = df.columns.get_loc('每个销售渠道的GMV') + 1
        df.insert(idx, '直播', pairs.apply(lambda p: _get(p, lambda l: l in LIVE_LABELS)))
        df.insert(idx + 1, '视频', pairs.apply(lambda p: _get(p, lambda l: l in VIDEO_LABELS)))

    if '按商品类目查看GMV占比' in df.columns:
        pairs = df['按商品类目查看GMV占比'].apply(parse_kv_lines)
        idx = df.columns.get_loc('按商品类目查看GMV占比') + 1
        df.insert(idx, '美妆个护占比', pairs.apply(lambda p: _get(p, lambda l: l in BEAUTY_LABELS)))

    if '粉丝性别占比' in df.columns:
        pairs = df['粉丝性别占比'].apply(parse_kv_lines)
        idx = df.columns.get_loc('粉丝性别占比') + 1
        df.insert(idx, '男生占比', pairs.apply(lambda p: _get(p, lambda l: l in MALE_LABELS)))

    if '粉丝年龄区间占比' in df.columns:
        pairs = df['粉丝年龄区间占比'].apply(parse_kv_lines)
        idx = df.columns.get_loc('粉丝年龄区间占比') + 1
        df.insert(idx, '18 - 24 岁占比', pairs.apply(lambda p: _get(p, _age_prefix('18'))))
        df.insert(idx + 1, '25 - 34 岁占比', pairs.apply(lambda p: _get(p, _age_prefix('25'))))

    # 有些导出天然就没有重复的"平均视频播放量.1"这一列；补一个空列，
    # 让每天清洗出来的表结构保持一致，方便以后堆叠/对比。
    if '平均视频播放量.1(次)' not in df.columns and '视频数(个)' in df.columns:
        idx = df.columns.get_loc('视频数(个)') + 1
        df.insert(idx, '平均视频播放量.1(次)', pd.NA)

    return df


# --------------------------------------------------------------------------
# 合并去重
# --------------------------------------------------------------------------
def dedupe_by_name(df: pd.DataFrame, name_col='达人名称') -> pd.DataFrame:
    """按昵称去重，同名保留"数据日期"最新的一条；昵称是占位符的行不参与去重
    （它们不是真的同一个人，只是导出里没抓到昵称）。"""
    is_placeholder = df[name_col].astype(str).str.strip().isin(PLACEHOLDER)
    placeholder_rows = df[is_placeholder]
    real_rows = df[~is_placeholder]
    if '数据日期' in df.columns:
        real_rows = real_rows.assign(_日期排序=pd.to_datetime(real_rows['数据日期']))
        real_rows = real_rows.sort_values('_日期排序', kind='stable').drop(columns='_日期排序')
    real_dedup = real_rows.drop_duplicates(subset=name_col, keep='last')
    return pd.concat([real_dedup, placeholder_rows]).sort_index().reset_index(drop=True)


def load_raw(path_str: str, forced_date):
    path = Path(path_str)
    df = read_tkshop_xls(path)
    d = forced_date or date_from_filename(path)
    if d is None:
        raise ValueError(
            f"无法从文件名 {path.name} 解析出日期，且没有用 --date 指定，"
            "请用 --date 2026-07-20 手动指定这份文件的数据日期"
        )
    if '数据日期' not in df.columns:
        df.insert(0, '数据日期', d)
    return df


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--inputs', nargs='+', required=True, help='一个或多个原始 tkshop达人信息 .xls/.xlsx 文件')
    ap.add_argument('--mode', choices=['merge_dedupe', 'keep_all'], required=True)
    ap.add_argument('--date', help='手动指定数据日期（当文件名里解析不出日期时用）')
    ap.add_argument('--output', required=True, help='输出 xlsx 路径')
    args = ap.parse_args()

    raw_dfs = [load_raw(p, args.date) for p in args.inputs]

    if args.mode == 'merge_dedupe':
        merged = pd.concat(raw_dfs, ignore_index=True, sort=False)
        merged = dedupe_by_name(merged)
        result = clean_units(merged)
        result = add_derived_columns(result)
    else:  # keep_all
        merged = pd.concat(raw_dfs, ignore_index=True, sort=False) if len(raw_dfs) > 1 else raw_dfs[0]
        result = clean_units(merged)
        result = add_derived_columns(result)

    result.to_excel(args.output, index=False, sheet_name='达人信息')
    print(f'已保存 {args.output}，共 {len(result)} 行，{len(result.columns)} 列')


if __name__ == '__main__':
    main()
```

This has been tested against real files and reproduces byte-for-byte the same results as the
manual step-by-step process it was extracted from (2346-row merge_dedupe, 208-row keep_all —
both matched exactly).

## Step 1.5: M 列 / `平均视频播放量.1`

`clean_units` 会补一个全空的 `平均视频播放量.1(次)` 占位列来对齐主表结构。在清洗后的输出里它落在
**M 列**。用户在做初筛时通常会要求"M 列整列删掉"——因为对这批 tkshop 导出来说这列恒为空，没有信息量。
所以：

- **只清洗**（不做初筛）时：保留该列，结构对齐优先。
- **做初筛输出候选池**时：默认删掉该列（`filter_candidates.py --drop-cols` 的默认值已经是它）。

不要把它和真正有数据的 `平均视频播放量(次)`（G 列）搞混。

## Step 1.6（可选）: 初筛达人候选池

清洗完之后用户常接一句"初筛 / 不符合的行直接删掉 / 输出符合条件的"。用同目录的
`filter_candidates.py`：

```bash
python filter_candidates.py \
    --input cleaned_20260805.xlsx \
    --output 初筛_20260805.xlsx
```

**2026-08 版本当前在用的阈值**（即脚本默认值）：

| 条件 | 字段 | 判定 |
|---|---|---|
| 近一个月成交 100+ | `近一个月成交件数` | ≥ 100 |
| 客单价 131,8K ₫ 以上 | `客单价(₫)` | ≥ 131800（含等于） |
| 男生比例不超过 60% | `男生占比` | ≤ 60 |
| 以视频出单为主 | `视频` / `直播` | 视频 ≥ 50 **且** 视频 > 直播 |
| 护肤产品超过 50% | `美妆个护占比` | > 50（严格大于） |

阈值都是命令行参数，随时可改：`--min-orders / --min-price / --max-male /
--min-video-share / --min-skincare`。**阈值是业务决策，会变**——用户下次提初筛时，
如果他给了新数字就用新数字，如果他只说"照上次的筛"再用上表的默认值。

实现上几个必须守住的点（都是这份数据的真实坑）：

1. **占位符不是 0。** `近一个月成交件数` 在清洗后仍是字符串列，`-`/`--` 必须判为缺失并
   **不通过**筛选，绝不能 `fillna(0)` 然后当成"成交 0 件"混进比较。
2. **开区间要按下界比。** 清洗后客单价可能是 `'524700+'` 这种字符串（开区间保留了 `+`）。
   取里面的数字当下界比较即可——下界已过阈值就必然过。直接 `astype(float)` 会抛异常。
3. **`直播` 为空 ≠ 直播占比高。** 大量达人渠道构成只有"视频数据 + 商品卡"，没有直播行，
   所以 `直播` 是 NaN。做"视频 > 直播"比较时要把 `直播` 的 NaN 当 0，否则 NaN 比较返回
   False，会把一批纯视频达人（正是最符合条件的那批）误杀。
4. **每个条件的单独命中数要打印出来。** 五个条件叠加后通过率会掉得很快（727 → 336 这种量级），
   把单条件漏斗打出来，用户才能判断是哪个阈值卡得太紧，而不是怀疑脚本坏了。

## Step 2: report back to the user

After running, always tell the user:
- Row count in vs. out
- Any extra columns the source file had that aren't part of the standard schema (e.g. some
  exports include `Email`/`Zalo` contact columns) — keep them in place rather than dropping them
- Whether the output's column structure matches the existing master table, since these get
  stacked/compared over time and a structural mismatch (e.g. a source file missing
  `平均视频播放量.1`) is worth flagging even though the script already patches it with an empty
  column

## Known raw-export column schema

The raw files' columns (order can vary slightly, some exports omit `平均视频播放量.1` or add
`Email`/`Zalo`):

`主页链接, 达人名称, [Email, Zalo,] 近一个月成交件数, 平均视频播放量, 近3个月的每个挂车视频的30天出单GMV数据, 互动量, 达人信息, 客单价, 视频数, [平均视频播放量.1,] 视频平均互动率, 直播数, 平均直播播放量, 每个销售渠道的GMV, 按商品类目查看GMV占比, 粉丝性别占比, 粉丝年龄区间占比`

After cleaning, the output adds/renames: `平均视频播放量(次)`, `视频数(个)`, `平均视频播放量.1(次)`,
`平均直播播放量(次)`, `客单价(₫)`, `近3个月的每个挂车视频的30天出单GMV数据(₫)`, plus the derived
`直播`, `视频`, `美妆个护占比`, `男生占比`, `18 - 24 岁占比`, `25 - 34 岁占比` columns inserted
right after their respective source columns.

## Things this skill deliberately does NOT do

初筛（Step 1.6）现在已经收进来了，但**红精华 / 白精华的分池**没有——那是在初筛候选池之上再按
产品线做的二次拆分，用的是另一套会变的业务阈值。用户提到"红精华候选""白精华候选"时，
当成新需求处理，先跟他确认当前阈值，别沿用旧的。
