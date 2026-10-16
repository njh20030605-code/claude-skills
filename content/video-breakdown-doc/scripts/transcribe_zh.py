#!/usr/bin/env python3
"""中文口播转写（faster-whisper large-v3，CPU int8）。只用来对时间和补无字幕段落，原话以烧录字幕为准。

用法：~/.venvs/whisper/bin/python transcribe_zh.py <工作目录>
读取 <工作目录>/wav/*.wav，输出 <工作目录>/wav/vNN.json（[{start,end,text}]）。

坑：
- 必须开 vad_filter=True、condition_on_previous_text=False。关掉 VAD 时整段带背景音乐的视频
  只识别出两三句，还会幻觉出「请不吝点赞订阅转发」这类句子。
- PyAV 版本不兼容，用 wave+numpy 直接喂数组，别改成传文件路径。
- 别对短片段单独重转，幻觉更严重；以整段结果为准。
- 一条 80 秒视频在 CPU 上约 1 分钟，多条时用 run_in_background。
"""
import glob, json, os, sys, time, wave
import numpy as np
from faster_whisper import WhisperModel

W = sys.argv[1]
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=12)
for w in sorted(glob.glob(f"{W}/wav/*.wav")):
    vid = os.path.basename(w)[:-4]
    out = f"{W}/wav/{vid}.json"
    if os.path.exists(out):
        continue
    t = time.time()
    wf = wave.open(w)
    a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    segs, info = m.transcribe(a, language="zh", vad_filter=True, beam_size=5, condition_on_previous_text=False,
                              initial_prompt="以下是简体中文的抖音护肤品带货口播。")
    res = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    last = res[-1]["end"] if res else 0
    print(f"{vid}: {len(res)} 段，转写到 {last:.1f} 秒，用时 {round(time.time() - t)} 秒", flush=True)
