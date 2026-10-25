# -*- coding: utf-8 -*-
"""汇总三题的实测数据：字数、与终稿相似度、平台两两矩阵。"""
import importlib.util, pathlib, sys

sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("v", r".workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

TOPICS = [
    ("灵活就业超2亿人与社保基数上移-劳动保障覆盖率的账本", "终稿-劳动保障覆盖率的账本.md"),
    ("广汽收购一汽合资股权-合资时代退出的定价权", "终稿-合资时代退出的定价权.md"),
    ("卫龙162吨魔芋粉口岸拦截-食品安全的前置闸门", "终稿-食品安全的前置闸门.md"),
]
PFX = ["知乎", "微信", "百家号", "CSDN", "头条"]

for name, fin_name in TOPICS:
    d = pathlib.Path(r"drafts/2026-09-15") / name
    fin = d / fin_name
    fn = m.count_body_chars(fin)
    ft = m.extract_body_text(fin)
    print("=====", name)
    print("终稿", fn)
    rows = []
    for p in PFX:
        fs = [f for f in d.glob(p + "-*.md")]
        if not fs:
            print("  MISSING", p)
            continue
        f = fs[0]
        n = m.count_body_chars(f)
        sim = m.text_similarity(m.extract_body_text(f), ft)
        rows.append((p, f, n, sim, n / fn))
    for p, f, n, sim, ratio in rows:
        print(f"  {p:4s} {n:5d}  保真 {ratio*100:5.1f}%  与终稿相似 {sim*100:5.1f}%")
    print("  --- pairwise ---")
    mx = 0
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            s = m.text_similarity(m.extract_body_text(rows[i][1]), m.extract_body_text(rows[j][1]))
            mx = max(mx, s)
            print(f"    {rows[i][0]:4s} x {rows[j][0]:4s} {s*100:5.1f}%")
    print("  max pairwise:", round(mx * 100, 1), "%")
