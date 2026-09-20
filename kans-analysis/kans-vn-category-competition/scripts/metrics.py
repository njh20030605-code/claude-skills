# -*- coding: utf-8 -*-
"""
metrics.py —— 一次性算出写结论需要的全部数字，按 references/analysis_playbook.md 的顺序打印。
先跑这个，再写分析，避免临时口算和口径漂移。
"""
import argparse
import numpy as np
import pandas as pd
import common as C

p = argparse.ArgumentParser()
p.add_argument("--cur", required=True)
p.add_argument("--pri", required=True)
p.add_argument("--rate", type=float, default=C.DEFAULT_RATE)
p.add_argument("--cur-label", default="本周")
p.add_argument("--pri-label", default="上周")
a = p.parse_args()

cur, pri = C.read_export(a.cur), C.read_export(a.pri)
B = C.build(cur, pri)
M, bd = B["market"], B["brand"]
W = lambda v: C.wan(v, a.rate)


def h(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


h("0 · 数据体检（口径陷阱先看这里）")
print(f"{a.cur_label} 店铺数 {len(cur)}，入榜门槛 {cur.gmv.min():,.0f} USD")
print(f"{a.pri_label} 店铺数 {len(pri)}，入榜门槛 {pri.gmv.min():,.0f} USD")
print(f"两周交集 {M['n']} 家；本周新进 {M['new_in']} 家；上周在榜本周掉出 {M['dropped']} 家")
cov1 = np.array([cur[c] for c in C.CH]).sum() / cur.gmv.sum() * 100
cov0 = np.array([pri[c] for c in C.CH]).sum() / pri.gmv.sum() * 100
print(f"五渠道之和 / 总GMV 覆盖率：{a.cur_label} {cov1:.1f}%，{a.pri_label} {cov0:.1f}%"
      f"（不等于 100% 说明字段口径有重叠，占比分母必须用五渠道之和）")
print(f"已合并的多店品牌：{[g for g, _ in B['merged_groups']] or '无'}")
print(f"未合并（有门店单周掉榜，合并会产生截断偏差）：{[g for g, _ in B['skipped_groups']] or '无'}")

h("1 · 大盘定调")
print(f"总 GMV 口径环比      {M['gmv_chg']:+.1f}%   ← 与「品牌总GMV环比」对比时用这个")
print(f"五渠道合计口径环比    {M['chsum_chg']:+.1f}%   ← 只在讨论渠道结构时用")
print(f"总 GMV {W(M['gmv0']):,.0f} 万元 → {W(M['gmv1']):,.0f} 万元")
print(f"\n{'渠道':<8}{'本周占比':>9}{'上周占比':>9}{'变化pp':>9}{'环比':>10}{'本周金额(万元)':>14}")
for i, nm in enumerate(C.NM):
    print(f"{nm:<8}{M['share1'][i]:>8.1f}%{M['share0'][i]:>8.1f}%"
          f"{M['share1'][i]-M['share0'][i]:>+9.1f}{M['ch_chg'][i]:>+9.1f}%{W(M['ch1'][i]):>14,.0f}")

h("2 · KANS 表现")
k = bd[bd.name.str.contains("韩束")]
if k.empty:
    print("KANS 不在两周交集内，检查店铺名是否变化")
else:
    k = k.iloc[0]
    print(f"总 GMV {W(k.gmv0):,.1f} → {W(k.gmv1):,.1f} 万元（{k.chg:+.1f}%），"
          f"跑赢大盘 {k.chg - M['gmv_chg']:+.1f}pp")
    print(f"类目排名 {k.rank0} → {k.rank1}")
    print(f"自播客单价 {k.aov0:.0f} → {k.aov1:.0f} USD（整数字段，±1≈±4-5%，小幅变动不解读）")
    if k.aov1 and k.aov0:
        o1, o0 = k[f"g1_{C.CH[2]}"] / k.aov1, k[f"g0_{C.CH[2]}"] / k.aov0
        print(f"自播推算主单量 {o0:,.0f} → {o1:,.0f}（{o1/o0-1:+.1%}）→ 增长来自单量还是客单一目了然")
    print(f"\n{'渠道':<8}{'环比':>9}{'大盘':>9}{'对比':>12}{'占比变化pp':>12}")
    for i, c in enumerate(C.CH):
        gap = k[f"chg_{c}"] - M["ch_chg"][i]
        print(f"{C.NM[i]:<8}{k[f'chg_{c}']:>+8.1f}%{M['ch_chg'][i]:>+8.1f}%"
              f"{('跑赢 %+.0fpp' % gap) if gap > 0 else ('跑输 %.0fpp' % abs(gap)):>12}"
              f"{k[f'd_{c}']:>+12.1f}")
    print("\n【占比下降 ≠ 该渠道缩了】若总 GMV 增速 > 该渠道增速，占比必然被稀释，先看金额环比再下结论。")
    print("\n跑输渠道的二次校验（加权 vs 中位数）：")
    for i, c in enumerate(C.CH):
        if k[f"chg_{c}"] < M["ch_chg"][i]:
            r = C.channel_percentile(B["inter"], c, k[f"chg_{c}"])
            print(f"  {C.NM[i]}：KANS {k[f'chg_{c}']:+.1f}% ｜ 大盘加权 {M['ch_chg'][i]:+.1f}% ｜ "
                  f"店铺中位数 {r['median']:+.1f}%（n={r['n']}）｜ KANS 位于第 {r['pct']:.0f} 百分位")
            inc = B["inter"][c + "_1"] - B["inter"][c + "_0"]
            top = inc.nlargest(10).sum() / inc.sum() * 100
            print(f"    该渠道增量前 10 家店铺贡献 {top:.1f}%"
                  f"{'→ 加权值被少数大店拉高，跑输可能是假信号' if top > 40 else ''}")

h("3 · 中国品牌梯队")
b = bd.copy()
b["short"] = b["name"].str.replace(r"\s*\(\d+店合计\)", "", regex=True)
t = b[b["short"].isin(C.CN_TIER)]
print(f"{'品牌':<10}{'本周(万元)':>11}{'环比':>9}{'排名':>10}" +
      "".join(f"{n+'占比':>11}" for n in C.NM))
for _, r in t.iterrows():
    print(f"{r['short']:<10}{W(r.gmv1):>11,.0f}{r.chg:>+8.0f}%{r.rank0:>5}→{r.rank1:<4}" +
          "".join(f"{r[f's1_{c}']:>10.0f}%" for c in C.CH))

h("4 · 异动品牌")
print("增幅榜（上周基数 > 2 万美元）：")
for _, r in b[b.gmv0 > 20000].nlargest(8, "chg").iterrows():
    top = max(C.CH, key=lambda c: r[f"d_{c}"])
    print(f"  {r['name']:<22}{r.chg:>+7.0f}%  本周 {W(r.gmv1):>7,.0f} 万元  "
          f"主要位移：{C.NM[C.CH.index(top)]} {r[f'd_{top}']:+.0f}pp")
print("降幅榜：")
for _, r in b.nsmallest(6, "chg").iterrows():
    print(f"  {r['name']:<22}{r.chg:>+7.0f}%  本周 {W(r.gmv1):>7,.0f} 万元")
print("\n结构位移榜（本周 GMV ≥ 10 万美元，按绝对位移排序）：")
big = b[b.gmv1 >= 100000].copy()
for c, nm in zip(C.CH, C.NM):
    s = big.reindex(big[f"d_{c}"].abs().sort_values(ascending=False).index).head(4)
    print(f"  {nm}：" + "；".join(f"{r['name']} {r[f'd_{c}']:+.0f}pp" for _, r in s.iterrows()))

h("5 · 待补数据提示")
print("本表只有结果数据，看不出对手「怎么做到的」。每周固定追问：")
print("  P0 增长最快的对手，其主力渠道的供给结构（达人数量 / 头部集中度 / 是否专场）")
print("  P0 逆势但保住量的对手，资源转去了哪个渠道")
print("  P0 我们与对手的达人重叠度（决定报价会不会被抬高）")
print("  P1 KANS 自播每小时 GMV、开播时长、场次（判断 +x% 是效率还是堆时长）")
print("  P1 KANS 主力渠道的佣金/坑位成本与真实 ROI")
print("  P1 一个不含大促的干净基线周")
