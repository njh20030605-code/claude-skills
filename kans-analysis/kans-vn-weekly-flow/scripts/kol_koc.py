# -*- coding: utf-8 -*-
"""affiliate_orders → 按商品ID 算 KOL / KOC 占比（两期）

输入（放 OUT 目录）：
  affiliate_cur.csv   本期 affiliate_orders 导出（联盟中心 › 订单 › 导出）
  affiliate_pri.csv   上期同一份导出
  kol_list.txt        付费达人清单，一行一个用户名（原始粘贴即可，本脚本会清洗）

🔴 口径铁律：
  1. affiliate_orders 是【达人视频渠道】成交，与 GMV-MAX 商品卡 / 直播 campaign 都不是一套，
     **绝对不能相加**。放进 GMV-MAX 表时只能作为「同商品ID 的达人结构」贴在旁边。
  2. 金额用「支付金额」÷ VND 折 RMB；**必须剔除 订单状态 = 客户未付款**
     （本期 606 行 / 上期 18 行，两期比例差很大，不剔会把结构算歪）。
  3. 合计与品线小计的 KOL 占比 = **按达人 GMV 加权**，不是各行简单平均。
  4. 清单是【当前累计签约名单】，套两期时上期 KOL 占比会被高估（新签达人在上期还没付费）。
     必须报两期匹配率，匹配率接近才说明占比可比 —— 8月W2 实测本期 46.0% / 上期 46.2%，通过。
  5. 某商品两期都无达人订单时 **留空，不要写 0%**（0% 表示有订单但全是 KOC）。
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import VND, OUT
import pandas as pd

# 广告计划 → 商品ID（每期核对一次；新计划上线要补）
PLAN2PID = {
    'MKT-白精华-0708':      '1731561143212017689',   # KANS serum trắng sáng da（白系精华）
    'MKT-素颜霜-0708':      '1731728613455398937',   # Kem Nâng Tông（素颜霜）
    'MKT-红精华-0708':      '1731559750857099289',   # Serum Chống Lão Hóa（红系抗老精华）
    'OL-白精华single-0715': '1734336273358619673',
    'MKT-红洁面-0708':      '1731558826539714585',   # Sữa Rửa Mặt Đỏ（红洁面）
    'MKT-红面霜-0803':      None,                    # 本期无达人视频订单
    'OL-红精华single-0722': '1734336201423553561',
}
LINE = {'白系': ['MKT-白精华-0708','MKT-素颜霜-0708','OL-白精华single-0715'],
        '红系': ['MKT-红精华-0708','MKT-红洁面-0708','MKT-红面霜-0803','OL-红精华single-0722']}


def load_kol(path):
    """清洗付费达人清单：去引号 / 去行内换行残留 / 去行尾附注 / 小写去重"""
    toks = []
    for line in open(path, encoding='utf-8').read().split('\n'):
        t = line.replace('"', '').replace('\t', ' ').strip()
        if not t:
            continue
        t = t.split(' ')[0].strip()      # 去掉行尾附注（如粘进来的 TikTok 链接文字）
        if t:
            toks.append(t.lower())
    return set(toks), len(toks)


def load_orders(path):
    d = pd.read_csv(path, dtype=str, low_memory=False)
    d.columns = [c.strip() for c in d.columns]
    d['amt'] = pd.to_numeric(d['支付金额'], errors='coerce').fillna(0) / VND
    d['u'] = d['达人用户名'].astype(str).str.strip().str.lower()
    return d[d['订单状态'] != '客户未付款'].copy()      # 铁律 2


def run():
    KOL, n_raw = load_kol(f'{OUT}/kol_list.txt')
    print(f'付费达人清单：原始 {n_raw} 条 → 去重 {len(KOL)} 个')
    per = {}
    for lbl, f in [('上期', 'affiliate_pri.csv'), ('本期', 'affiliate_cur.csv')]:
        d = load_orders(f'{OUT}/{f}')
        d['k'] = d.u.isin(KOL)
        allu = set(d.u)
        hit = allu & KOL
        print(f'{lbl}: {len(d)} 行 | 出单达人 {len(allu)} | 命中 {len(hit)} ({len(hit)/len(allu):.1%}) '
              f'| 达人GMV {d.amt.sum():,.0f} 元 | KOL {d[d.k].amt.sum()/d.amt.sum():.1%}')
        r = {}
        for plan, pid in PLAN2PID.items():
            if pid is None:
                r[plan] = (0.0, None); continue      # 铁律 5：留空不写 0
            x = d[d['商品 ID'] == pid]
            t = x.amt.sum()
            r[plan] = (t, (x[x.k].amt.sum() / t) if t else None)
        per[lbl] = r
    print(f'\n{"广告计划":22s}{"上期达人GMV":>12s}{"上期KOL":>9s}{"本期达人GMV":>12s}{"本期KOL":>9s}{"KOL变化":>10s}')
    for plan in PLAN2PID:
        (pt, pk), (ct, ck) = per['上期'][plan], per['本期'][plan]
        if pk is None and ck is None:
            print(f'{plan:22s}  —— 两期均无达人视频订单（留空，不写 0%）'); continue
        d_ = f'{(ck-pk)*100:+.1f}pp' if (pk is not None and ck is not None) else '—'
        print(f'{plan:22s}{pt:>12,.0f}{pk:>9.1%}{ct:>12,.0f}{ck:>9.1%}{d_:>10s}')
    print()
    for lb, plans in list(LINE.items()) + [('全部', list(PLAN2PID))]:
        def w(period):
            g = sum(per[period][p][0] for p in plans)
            k = sum((per[period][p][1] or 0) * per[period][p][0] for p in plans)
            return g, (k / g if g else None)          # 铁律 3：GMV 加权
        (pg, pk), (cg, ck) = w('上期'), w('本期')
        print(f'{lb:4s} 达人GMV {pg:>9,.0f} → {cg:>9,.0f} ({cg/pg-1:+6.1%})   '
              f'KOL占比 {pk:.1%} → {ck:.1%} ({(ck-pk)*100:+.1f}pp)')
    return per


if __name__ == '__main__':
    run()
