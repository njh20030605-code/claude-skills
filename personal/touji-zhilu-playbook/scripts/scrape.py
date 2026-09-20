#!/usr/bin/env python3
"""抓取 Telegram 公开频道 @journey_of_someone (投机之路) 全量帖子。"""
import json, re, subprocess, time
from bs4 import BeautifulSoup

CH = "journey_of_someone"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def fetch(url, tries=4):
    for i in range(tries):
        try:
            p = subprocess.run(
                ["curl", "-sS", "--max-time", "40", "-A", UA,
                 "-H", "Accept-Language: zh-CN,zh;q=0.9", url],
                capture_output=True, timeout=60)
            if p.returncode == 0 and p.stdout:
                return p.stdout.decode("utf-8", "replace")
            print(f"  retry {i+1} {url}: rc={p.returncode} {p.stderr[:200]}")
        except Exception as e:
            print(f"  retry {i+1} {url}: {e}")
        time.sleep(2 * (i + 1))
    return None


def body_of(msg):
    """取真正的正文：排除掉 a.tgme_widget_message_reply 引用块里的那份 text。"""
    for node in msg.select("div.tgme_widget_message_text"):
        if node.find_parent("a", class_="tgme_widget_message_reply"):
            continue
        return node
    return None


def text_of(node):
    if node is None:
        return ""
    for br in node.find_all("br"):
        br.replace_with("\n")
    return node.get_text()


def parse(html, out):
    soup = BeautifulSoup(html, "html.parser")
    ids = []
    for wrap in soup.select("div.tgme_widget_message_wrap"):
        msg = wrap.select_one("div.tgme_widget_message")
        if not msg or not msg.get("data-post"):
            continue
        mid = int(msg["data-post"].split("/")[1])
        ids.append(mid)
        if mid in out:
            continue
        body = body_of(msg)
        t = msg.select_one("time")
        # 转发/回复引用的原文
        reply = msg.select_one("a.tgme_widget_message_reply")
        # 反应
        reactions = {}
        for r in msg.select("span.tgme_widget_message_reaction"):
            emo = r.select_one("i.emoji, .emoji")
            cnt = r.select_one("span.tgme_widget_message_reaction_count, .tgme_widget_message_reaction_count")
            reactions[(emo.get_text() if emo else "?").strip()] = (cnt.get_text() if cnt else "").strip()
        media = []
        for a in msg.select("a.tgme_widget_message_photo_wrap"):
            st = a.get("style", "")
            m = re.search(r"url\('([^']+)'\)", st)
            if m:
                media.append({"type": "photo", "url": m.group(1)})
        for v in msg.select("video.tgme_widget_message_video"):
            media.append({"type": "video", "url": v.get("src", "")})
        if msg.select_one(".tgme_widget_message_document"):
            media.append({"type": "document", "url": ""})
        if msg.select_one(".tgme_widget_message_voice"):
            media.append({"type": "voice", "url": ""})
        views = msg.select_one("span.tgme_widget_message_views")
        out[mid] = {
            "id": mid,
            "url": f"https://t.me/{CH}/{mid}",
            "datetime": t.get("datetime") if t and t.get("datetime") else None,
            "text": text_of(body).strip(),
            "reply_quote": text_of(reply).strip() if reply else "",
            "media": media,
            "views": views.get_text().strip() if views else "",
            "reactions": reactions,
        }
    return ids


def main():
    out = {}
    html = fetch(f"https://t.me/s/{CH}")
    ids = parse(html, out)
    cursor = min(ids) if ids else None
    stall = 0
    while cursor and cursor > 1:
        url = f"https://t.me/s/{CH}?before={cursor}"
        html = fetch(url)
        if not html:
            break
        ids = parse(html, out)
        new_cursor = min(ids) if ids else None
        print(f"before={cursor} -> got {len(ids)}, total {len(out)}")
        if not new_cursor or new_cursor >= cursor:
            stall += 1
            if stall >= 2:
                break
            cursor = cursor - 20
        else:
            stall = 0
            cursor = new_cursor
        time.sleep(1.0)

    posts = [out[k] for k in sorted(out)]
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"\nDONE: {len(posts)} posts, id {posts[0]['id']}..{posts[-1]['id']}")
    missing = sorted(set(range(posts[0]['id'], posts[-1]['id'] + 1)) - set(out))
    print(f"missing ids ({len(missing)}): {missing[:60]}")


if __name__ == "__main__":
    main()
