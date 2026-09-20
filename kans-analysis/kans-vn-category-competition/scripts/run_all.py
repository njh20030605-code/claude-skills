# -*- coding: utf-8 -*-
"""
run_all.py —— 一条命令跑完：指标汇总 → 6 张图 → xlsx

python run_all.py --cur cur.tsv --pri pri.tsv --rate 6.7476 \
    --cur-label "本周 08.03-08.09" --pri-label "上周 07.27-08.02" \
    --outdir ./out

指标结果同时打印到屏幕并写入 <outdir>/metrics.txt。
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHARTS = [
    ("chart1_channel_structure.py", "01_渠道结构对比.png"),
    ("chart2_cn_brand_tier.py", "02_中国品牌梯队.png"),
    ("chart3_anomaly_scatter.py", "03_异动定位散点.png"),
    ("chart4_kans_channels.py", "04_KANS渠道结构.png"),
    ("chart5_top_rank.py", "05_TopN排名与GMV.png"),
    ("chart6_brand_channel_mix.py", "06_品牌渠道占比对比.png"),
]

p = argparse.ArgumentParser()
p.add_argument("--cur", required=True)
p.add_argument("--pri", required=True)
p.add_argument("--rate", type=float, required=True, help="当日实时汇率，必填")
p.add_argument("--rate-note", default="")
p.add_argument("--cur-label", default="本周")
p.add_argument("--pri-label", default="上周")
p.add_argument("--focus", default="达人直播")
p.add_argument("--outdir", default=".")
p.add_argument("--skip-xlsx", action="store_true")
p.add_argument("--only", default="", help="只跑某几张图，如 --only 1,3,6")
a = p.parse_args()
os.makedirs(a.outdir, exist_ok=True)
base = ["--cur", a.cur, "--pri", a.pri, "--rate", str(a.rate),
        "--cur-label", a.cur_label, "--pri-label", a.pri_label]


def run(script, extra, capture=None):
    cmd = [sys.executable, os.path.join(HERE, script)] + base + extra
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode:
        sys.stderr.write(r.stderr)
        raise SystemExit(f"{script} 失败")
    if capture:
        with open(capture, "w", encoding="utf-8") as f:
            f.write(r.stdout)


print("=" * 78 + "\n指标汇总\n" + "=" * 78)
run("metrics.py", [], capture=os.path.join(a.outdir, "metrics.txt"))

only = {int(x) for x in a.only.split(",") if x.strip()} if a.only else set(range(1, 7))
for i, (script, name) in enumerate(CHARTS, start=1):
    if i not in only:
        continue
    extra = ["--out", os.path.join(a.outdir, name)]
    if script.startswith(("chart2", "chart3")):
        extra += ["--focus", a.focus]
    run(script, extra)

if not a.skip_xlsx:
    run("build_xlsx.py", ["--rate-note", a.rate_note,
                          "--out", os.path.join(a.outdir, "两周对比_CNY.xlsx")])
    rc = "/mnt/skills/public/xlsx/scripts/recalc.py"
    if os.path.exists(rc):
        subprocess.run([sys.executable, rc, os.path.join(a.outdir, "两周对比_CNY.xlsx"), "180"])

print("\n完成。产物在", a.outdir)
