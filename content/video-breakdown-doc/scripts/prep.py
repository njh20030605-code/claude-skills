#!/usr/bin/env python3
"""素材预处理：压缩改名 + 抽音频 + 抽帧 + 拼逐秒总览图 + 拼 0.5 秒字幕条。

用法：
  python3 prep.py --out <工作目录> v01=/path/原片1.mp4 v02=/path/原片2.mp4 ...
  可选 --names names.json  （{"v01": "01-红蛮腰399明星千川混剪-这样打开", ...}，用于上传文档的干净文件名，
                            原文件名里常带编导/剪辑同事姓名，必须换掉）

产出（每条视频 vNN）：
  <out>/v/<干净名>.mp4          540p 压缩版（上传飞书用，单条一般 3–14MB）
  <out>/wav/vNN.wav             16k 单声道（给 transcribe_zh.py）
  <out>/vNN/fr/f_XXX.jpg        2 fps 抽帧，宽 360
  <out>/vNN/sheet_XXX.jpg       1 fps 总览图，每张 8 帧，左上角标秒数（逐张 Read 看完）
  <out>/vNN/sub_XXX.jpg         0.5 秒一格的字幕区条带（读烧录字幕原话用）
  <out>/manifest.json           时长、分辨率、文件路径
"""
import argparse, json, os, subprocess, glob, sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except Exception:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"命令失败: {' '.join(cmd)}\n{r.stderr[-500:]}")
    return r.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height",
               "-of", "json", path])
    d = json.loads(out)
    st = [s for s in d.get("streams", []) if s.get("width")]
    return float(d["format"]["duration"]), (st[0]["width"], st[0]["height"]) if st else (None, None)


def sheets(frdir, outdir, per=8, cols=4):
    fs = sorted(glob.glob(f"{frdir}/f_*.jpg"))
    one = fs[::2]  # 2fps -> 1fps
    f = font(26)
    out = []
    for k in range(0, len(one), per):
        ims = [Image.open(p) for p in one[k:k + per]]
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (w * cols, h * rows), "white")
        d = ImageDraw.Draw(sh)
        for j, im in enumerate(ims):
            x, y = (j % cols) * w, (j // cols) * h
            sh.paste(im, (x, y))
            d.rectangle([x, y, x + 78, y + 36], fill="black")
            d.text((x + 6, y + 2), f"{k + j}s", fill="yellow", font=f)
        p = f"{outdir}/sheet_{k:03d}.jpg"
        sh.save(p, quality=85)
        out.append(p)
    return out


def subtitle_strips(frdir, outdir, top=0.58, bottom=0.84, cols=4, rows=10):
    fs = sorted(glob.glob(f"{frdir}/f_*.jpg"))
    f = font(20)
    strips = []
    for i, p in enumerate(fs):
        im = Image.open(p)
        w, h = im.size
        b = im.crop((0, int(h * top), w, int(h * bottom)))
        d = ImageDraw.Draw(b)
        d.rectangle([0, 0, 62, 26], fill="black")
        d.text((4, 1), f"{i * 0.5:.1f}", fill="yellow", font=f)
        strips.append(b)
    if not strips:
        return []
    bw, bh = strips[0].size
    per = cols * rows
    out = []
    for k in range(0, len(strips), per):
        sh = Image.new("RGB", (bw * cols, bh * rows), "white")
        for j, b in enumerate(strips[k:k + per]):
            sh.paste(b, ((j % cols) * bw, (j // cols) * bh))
        p = f"{outdir}/sub_{k:03d}.jpg"
        sh.save(p, quality=85)
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", help="vid -> 干净文件名（不含扩展名）的 JSON")
    ap.add_argument("--sub-top", type=float, default=0.58, help="字幕区上沿（占画面高度比例）")
    ap.add_argument("--sub-bottom", type=float, default=0.84)
    ap.add_argument("--skip-compress", action="store_true")
    ap.add_argument("items", nargs="+", help="vNN=/path/to/video.mp4")
    a = ap.parse_args()
    names = json.load(open(a.names, encoding="utf-8")) if a.names else {}
    os.makedirs(f"{a.out}/v", exist_ok=True)
    os.makedirs(f"{a.out}/wav", exist_ok=True)
    manifest = {}
    for it in a.items:
        vid, src = it.split("=", 1)
        dur, (w, h) = probe(src)
        clean = names.get(vid, vid)
        vdir = f"{a.out}/{vid}"
        os.makedirs(f"{vdir}/fr", exist_ok=True)
        if not a.skip_compress:
            run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "scale=540:-2", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "30", "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart",
                 f"{a.out}/v/{clean}.mp4"])
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
             f"{a.out}/wav/{vid}.wav"])
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "fps=2,scale=360:-2", f"{vdir}/fr/f_%03d.jpg"])
        sh = sheets(f"{vdir}/fr", vdir)
        sb = subtitle_strips(f"{vdir}/fr", vdir, a.sub_top, a.sub_bottom)
        manifest[vid] = dict(src=src, clean_name=clean, duration=round(dur, 1), size=[w, h],
                             upload=f"{a.out}/v/{clean}.mp4", sheets=sh, subtitle_strips=sb)
        print(f"{vid}: {dur:.1f}s {w}x{h} | {len(sh)} 张总览图, {len(sb)} 张字幕条 -> {clean}.mp4")
    json.dump(manifest, open(f"{a.out}/manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
