#!/usr/bin/env python3
"""原话校验：「」只能放视频原话，概括/观众心理用“”。

作为库：
  from quotes import load_scripts, dequote, near_quotes
作为命令行：
  python3 quotes.py <scripts.json> <vid> <文本或XML文件>
  -> 列出 <文件> 里所有不在 vid 原话中的「」内容，以及“”里几乎就是原话的近似转述（应改回「原话」）。

屏幕文字（底部常驻小字、大字、贴纸、价格标签）只要在核对文件的文件头、「产品与机制」或时间轴「画面」列里
用「」记下来了，parse_review.py 会存进 scripts.json 的 screen 字段，这里当原文放行；没记下的会被列出来，
核对过确实是屏幕上的字就保留「」。
"""
import json, re, sys, difflib

PUNCT = r'[\s，。、,.！!？?；;：:「」“”"…—\-（）()·/]'


def norm(s):
    return re.sub(PUNCT, '', s)


def load_scripts(path):
    return json.load(open(path, encoding='utf-8'))


def lines_of(S, vid):
    return [l for s in S[vid]['segs'] for l in s['lines']]


def alltext(S, vid):
    return norm(''.join(lines_of(S, vid)))


def screen_of(S, vid):
    return [norm(x) for x in S[vid].get('screen', []) if norm(x)]


def dequote(text, S, vid):
    """把既不是口播原话、也不是核对文件记下的屏幕文字的「x」改成“x”，返回(新文本, 被改的列表)。"""
    full = alltext(S, vid)
    scr = screen_of(S, vid)
    bad = []

    def rep(m):
        x = m.group(1)
        nx = norm(x)
        if nx and (nx in full or any(nx in s for s in scr)):
            return m.group(0)
        bad.append(x)
        return '“' + x + '”'

    return re.sub(r'「([^「」]{1,120})」', rep, text), bad


def near_quotes(text, S, vid, threshold=0.6):
    """“x” 里和某句原话高度相似的（近似转述），建议换成「原话」。"""
    ls = lines_of(S, vid)
    pool = ls + [ls[i] + '，' + ls[i + 1] for i in range(len(ls) - 1)]
    out = []
    for x in re.findall(r'“([^”]+)”', text):
        best = max(pool, key=lambda l: difflib.SequenceMatcher(None, norm(x), norm(l)).ratio())
        r = difflib.SequenceMatcher(None, norm(x), norm(best)).ratio()
        if r >= threshold:
            out.append((x, best, round(r, 2)))
    return out


if __name__ == '__main__':
    S = load_scripts(sys.argv[1])
    vid = sys.argv[2]
    t = open(sys.argv[3], encoding='utf-8').read()
    t = re.sub(r'<[^>]+>', ' ', t)
    _, bad = dequote(t, S, vid)
    print('既不是口播原话、也不在核对文件屏幕文字里的「」（改“”或换原话）：')
    for b in bad:
        print('  -', b)
    print('“”里的近似原话（建议换成「原话」）：')
    for x, best, r in near_quotes(t, S, vid):
        print(f'  - “{x}” ≈ 「{best}」 ({r})')
