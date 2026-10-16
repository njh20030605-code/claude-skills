#!/usr/bin/env python3
"""生成「逐条拆解」表格 XML（飞书 docx XML），5 列：素材（含视频）| 时长 | 钩子（0～5 秒）| 完整话术拆解 | 结构与亮点。

用法：python3 build_table.py <scripts.json> <rows.json> <输出.xml>

rows.json 是一个列表，每条：
{
  "vid": "v01",
  "name": "红蛮腰 399 明星千川混剪「这样打开」",          # 素材名（不写画面上没标注的人名）
  "duration": "77 秒",
  "video": {"path": "v/01-xxx.mp4"}  或  {"token": "已上传附件token", "name": "01-xxx.mp4"},
  "hook_pic": "温峥嵘（画面标注「明星@温峥嵘」）捧着红蛮腰面霜……",   # 0～5 秒画面
  "hook_lines": ["你们是不是还在这样打开韩束的红蛮腰，……"],          # 0～5 秒原话（必须是原话）
  "highlight": "先用「……」……"                                     # 结构与亮点，「」只放原话
}
video.path 相对于执行 lark-cli 时的工作目录（写 @./ 前缀由脚本加）。

自动处理：段落标题去掉「」、时间写法统一成「～」；「作用」和「亮点」里不是原话的「」改成“”；
hook_lines 不是原话会报错退出。输出末尾打印每条被改动的引号，人工过一眼。
"""
import html, json, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from quotes import alltext, dequote, near_quotes, norm

esc = lambda s: html.escape(s, quote=False)
H = lambda t: f'<th background-color="light-gray"><p>{t}</p></th>'


def tnorm(t):
    return re.sub(r'(\d)\s*[–-]\s*(\d)', r'\1～\2', t)


def script_cell(S, v):
    out, changed = [], []
    for i, s in enumerate(S[v]['segs'], 1):
        title = re.sub(r'[「」]', '', tnorm(s['title']))
        out.append(f'<p><b>{i}. {esc(title)}</b></p>')
        out.append('<ul>' + ''.join(f'<li>{esc(re.sub(r"[，。]$", "", l))}</li>' for l in s['lines']) + '</ul>')
        for n in s['notes']:
            out.append(f'<p><span text-color="gray">{esc(n)}</span></p>')
        w, bad = dequote(s['what'], S, v)
        changed += bad
        out.append(f'<p><span text-color="gray">作用：{esc(w)}</span></p>')
    return ''.join(out), changed


def video_xml(vd):
    if 'token' in vd:
        return f'<figure view-type="Preview"><source token="{vd["token"]}" name="{esc(vd["name"])}"/></figure>'
    name = vd.get('name') or vd['path'].rsplit('/', 1)[-1]
    return f'<figure view-type="Preview"><source path="@./{vd["path"]}" name="{esc(name)}"/></figure>'


def main():
    S = json.load(open(sys.argv[1], encoding='utf-8'))
    rows = json.load(open(sys.argv[2], encoding='utf-8'))
    trs, report = [], {}
    for r in rows:
        v = r['vid']
        full = alltext(S, v)
        for l in r['hook_lines']:
            core = re.sub(r'（[^）]*）$', '', l)
            if norm(core) not in full:
                sys.exit(f'{v} 钩子原话对不上口播：{l}（屏幕文字请写进 hook_pic）')
        sc, ch1 = script_cell(S, v)
        hl, ch2 = dequote(r['highlight'], S, v)
        report[v] = dict(作用改引号=ch1, 亮点改引号=ch2, 近似原话=near_quotes(hl, S, v))
        hook = f'<p><b>画面：</b>{esc(r["hook_pic"])}</p><p><b>原话：</b>' + ''.join(f'「{esc(l)}」' for l in r['hook_lines']) + '</p>'
        c1 = f'<p>{esc(r["name"])}</p>{video_xml(r["video"])}'
        trs.append(f'<tr><td>{c1}</td><td><p>{esc(r["duration"])}</p></td><td>{hook}</td><td>{sc}</td><td><p>{esc(hl)}</p></td></tr>')
    xml = ('<table><colgroup><col width="160"/><col width="56"/><col width="190"/><col width="390"/><col width="210"/></colgroup>'
           '<thead><tr>' + ''.join(H(t) for t in ['素材', '时长', '钩子（0～5 秒）', '完整话术拆解', '结构与亮点']) +
           '</tr></thead><tbody>' + ''.join(trs) + '</tbody></table>')
    open(sys.argv[3], 'w', encoding='utf-8').write(xml)
    print(f'写出 {sys.argv[3]}（{len(xml)} 字符，{len(rows)} 行）')
    for v, d in report.items():
        if any(d.values()):
            print(v, json.dumps(d, ensure_ascii=False))


if __name__ == '__main__':
    main()
