#!/usr/bin/env python3
"""把逐条核对文件（vNN_核对.md）解析成 scripts.json，供 build_table.py / quotes.py 使用。

用法：python3 parse_review.py <核对文件所在目录（可多层，递归找 v*_核对.md）> <输出 scripts.json>

核对文件格式见 references/review-template.md，关键是「## 完整话术（分层）」一节：
  段落标题：  ### 1. 段名（起～止 秒）   或   **一、段名（起–止 秒）**
  原话：      - 一句原话
  作用：      这段对用户在做什么：……
"""
import glob, json, os, re, sys


def section(txt, title):
    m = re.search(r'^## ' + title + r'.*?$(.*?)(?=^## |\Z)', txt, re.S | re.M)
    return m.group(1) if m else ''


def parse_script(s):
    segs, cur = [], None
    for line in s.splitlines():
        l = line.strip()
        h = re.match(r'^(?:###\s*\d+[.、]\s*|\*\*[一二三四五六七八九十]+、)(.+?)(?:\*\*)?$', l)
        if h:
            cur = {'title': h.group(1).strip().rstrip('*'), 'lines': [], 'notes': [], 'what': ''}
            segs.append(cur)
            continue
        if not cur:
            continue
        if l.startswith('- '):
            cur['lines'].append(l[2:].strip())
        elif l.startswith('这段对用户在做什么'):
            cur['what'] = re.sub(r'^这段对用户在做什么[:：]\s*', '', l)
        elif l and not l.startswith('---'):
            cur['notes'].append(l)
    return segs


def screen_texts(t):
    """核对文件里记录的屏幕文字（常驻小字、大字、贴纸、价格标签）：取文件头、「产品与机制」、
    以及「开头」「逐段时间轴」两张表「画面」列里的「…」。quotes.dequote 认它们是原文。"""
    head = [l for l in t.split('\n## ', 1)[0].splitlines()
            if not l.startswith('# ') and '原始文件名' not in l]      # 标题是自己起的名，文件名不是屏幕文字
    parts = ['\n'.join(head), section(t, '产品与机制')]
    for title in ('开头 0', '逐段时间轴'):
        for row in section(t, title).splitlines():
            cells = [c.strip() for c in row.strip().strip('|').split('|')]
            if len(cells) >= 3 and not set(cells[0]) <= set('-: '):
                parts.append(cells[1])
    out = []
    for x in re.findall(r'「([^「」]{1,120})」', '\n'.join(parts).replace('**', '')):
        if x not in out:
            out.append(x)
    return out


def main():
    root, out = sys.argv[1], sys.argv[2]
    res = {}
    for f in sorted(glob.glob(os.path.join(root, '**', 'v*_核对.md'), recursive=True)):
        v = re.match(r'(v\d+)', os.path.basename(f)).group(1)
        t = open(f, encoding='utf-8').read()
        res[v] = {'file': f, 'segs': parse_script(section(t, '完整话术')),
                  'one': section(t, '一句话核心打法').strip(), 'open': section(t, '开头 0').strip(),
                  'screen': screen_texts(t)}
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot = 0
    for v, d in res.items():
        n = sum(len(s['lines']) for s in d['segs'])
        tot += n
        miss = [s['title'][:12] for s in d['segs'] if not s['what']]
        print(f"{v}: {len(d['segs'])} 段 {n} 句，屏幕文字 {len(d['screen'])} 处" + (f" | 缺「作用」: {miss}" if miss else ''))
    print(f'合计 {len(res)} 条视频 {tot} 句原话')


if __name__ == '__main__':
    main()
