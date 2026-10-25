# -*- coding: utf-8 -*-
"""计算三题平台稿实测数据（字数/占终稿比/与终稿相似度/两两最高）用于合规自检表"""
import sys, io, importlib.util, itertools
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

TOPICS = [
    ("老干妈用AI一年54亿-拣椒工从600人减至48人", "终稿-54亿的营收-552个消失的岗位-老干妈这笔账怎么记.md"),
    ("茶百道涉嫌操纵IPO被香港证监会停牌", "终稿-一只股票的需求可以是写出来的-茶百道停牌这件事.md"),
    ("北京社保缴费基数下限7270元vs法定最低工资2540元", "终稿-两把尺子量同一个人-2540元的最低工资与7270元的社保基数.md"),
]
for topic, fn in TOPICS:
    d = ROOT / "drafts/2026-10-14" / topic
    fin = d / fn
    t = chk.count_body_chars(fin)
    print("=" * 60)
    print(topic, "终稿", t)
    sims = {}
    for pf in sorted([f for f in d.glob("*.md") if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]):
        n = chk.count_body_chars(pf)
        s = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(fin))
        pfx = next((p for p in chk.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
        sims[pf.name] = (n, s, chk.PLATFORM_MIN_RATIO.get(pfx, 0), pfx)
        print(f"  {pfx[:-1]:<5} {n:>5}字 {n*100//t:>3}% 与终稿 {s:.4f} 下限{chk.PLATFORM_MIN_RATIO.get(pfx,0):.0%}")
    best = (None, 0.0)
    for a, b in itertools.combinations(sorted(sims), 2):
        s = chk.text_similarity(chk.extract_body_text(d / a), chk.extract_body_text(d / b))
        if s > best[1]:
            best = (f"{a[:3]} vs {b[:3]}", s)
    print("  两两最高:", best[0], f"{best[1]:.4f}")
