# -*- coding: utf-8 -*-
"""批量体检：保真比 + 与终稿相似度 + 平台两两相似度。"""
import sys, difflib, importlib.util, itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gb", HERE / "规范校验.py")
gb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gb)

d = Path(sys.argv[1])
final = next(d.glob("终稿-*.md"))
plats = [p for p in sorted(d.glob("*.md"))
         if p.name.split("-")[0] in ("知乎", "微信", "百家号", "CSDN", "头条")]
wf = gb.count_body_chars(final)
print(f"[终稿] {wf}")
for p in plats:
    w = gb.count_body_chars(p)
    s = difflib.SequenceMatcher(None, gb.extract_body_text(final),
                                gb.extract_body_text(p), autojunk=False).ratio()
    print(f"{p.name.split('-')[0]:<6} {w:>5}  保真 {w/wf*100:5.1f}%  相似 {s*100:5.1f}%")
print("--- 两两 ---")
mx = ("", 0.0)
for a, b in itertools.combinations(plats, 2):
    s = difflib.SequenceMatcher(None, gb.extract_body_text(a),
                                gb.extract_body_text(b), autojunk=False).ratio()
    tag = "!!!" if s >= 0.85 else "ok"
    if s > mx[1]:
        mx = (f"{a.name.split('-')[0]}x{b.name.split('-')[0]}", s)
    print(f"{a.name.split('-')[0]:<6}x {b.name.split('-')[0]:<6} {s*100:5.1f}%  {tag}")
print("最高:", f"{mx[0]} {mx[1]*100:.1f}%")
