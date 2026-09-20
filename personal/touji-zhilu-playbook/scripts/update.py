#!/usr/bin/env python3
"""增量更新「投机之路」存档：抓新帖 -> 合并 posts.json -> 重写 archive.md，只打印新增。"""
import json, os, re, sys, time
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scrape import CH, fetch, parse, body_of, text_of  # noqa: E402

REF = os.path.join(HERE, "..", "references")
POSTS = os.path.join(REF, "posts.json")
ARCHIVE = os.path.join(REF, "archive.md")


def probe_single(mid):
    """相册组图 / 服务消息不会出现在 /s/ 翻页里，单独用 embed 页补。"""
    html = fetch(f"https://t.me/{CH}/{mid}?embed=1&mode=tme")
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    msg = soup.select_one("div.tgme_widget_message")
    if not msg or "tgme_widget_message_error" in html[:4000]:
        return None
    t = msg.select_one("time")
    media = []
    for a in msg.select("a.tgme_widget_message_photo_wrap"):
        m = re.search(r"url\('([^']+)'\)", a.get("style", ""))
        if m:
            media.append({"type": "photo", "url": m.group(1)})
    for v in msg.select("video.tgme_widget_message_video"):
        media.append({"type": "video", "url": v.get("src", "")})
    txt = text_of(body_of(msg)).strip()
    if not txt and not media:
        return None
    return {"id": mid, "url": f"https://t.me/{CH}/{mid}",
            "datetime": t.get("datetime") if t and t.get("datetime") else None,
            "text": txt, "reply_quote": "", "media": media,
            "views": "", "reactions": {}, "_via": "embed"}


def main():
    old = {p["id"]: p for p in json.load(open(POSTS, encoding="utf-8"))}
    last = max(old)
    print(f"本地存档 {len(old)} 条，最新 #{last}")

    fresh = {}
    parse(fetch(f"https://t.me/s/{CH}"), fresh)
    cursor = min(fresh) if fresh else None
    # 一直往回翻到已存档的最新 id 为止
    while cursor and cursor > last:
        ids = []
        html = fetch(f"https://t.me/s/{CH}?before={cursor}")
        if html:
            ids = parse(html, fresh)
        nxt = min(ids) if ids else None
        if not nxt or nxt >= cursor:
            break
        cursor = nxt
        time.sleep(1.0)

    new = {k: v for k, v in fresh.items() if k > last}
    # 补翻页里没出现的 id
    if new:
        for mid in range(last + 1, max(new) + 1):
            if mid in new:
                continue
            p = probe_single(mid)
            if p:
                new[mid] = p
            time.sleep(0.5)

    if not new:
        print("没有新帖。")
        return

    old.update(new)
    posts, seen = [], {}
    for k in sorted(old):
        x = old[k]
        t = x["text"].strip()
        if t and t in seen:            # 相册组图的重复 caption
            seen[t]["media"] += x["media"]
            continue
        if t:
            seen[t] = x
        posts.append(x)

    json.dump(posts, open(POSTS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(ARCHIVE, "w", encoding="utf-8") as f:
        f.write("# 投机之路 @journey_of_someone 全量存档\n\n")
        for x in posts:
            f.write(f"\n\n---\n## #{x['id']}  {x['datetime'] or ''}  {x['url']}\n")
            if x.get("reply_quote"):
                f.write(f"> 引用: {x['reply_quote'][:120]}\n\n")
            f.write(x["text"] or "(无正文)")
            if x["media"]:
                f.write(f"\n\n[媒体 x{len(x['media'])}]")

    print(f"新增 {len(new)} 条，存档共 {len(posts)} 条。新内容：")
    for k in sorted(new):
        d = (new[k].get("datetime") or "")[:10]
        print(f"\n--- #{k} {d}\n{new[k]['text'][:500]}")
    print("\n记得更新 SKILL.md 顶部的区间与条数。")


if __name__ == "__main__":
    main()
