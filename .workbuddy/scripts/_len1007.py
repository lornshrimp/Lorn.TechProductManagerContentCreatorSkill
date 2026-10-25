# -*- coding: utf-8 -*-
"""字数/相似度实测工具（复用校验脚本口径）"""
import sys, io, os, re, json, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", BASE / ".workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

args = sys.argv[1:]
if not args:
    print("usage: _len1007.py <file...>")
    sys.exit(0)

for a in args:
    p = Path(a)
    if not p.is_absolute():
        p = BASE / a
    if not p.exists():
        print(f"MISSING {p}")
        continue
    n = m.count_body_chars(p)
    h2 = len(re.findall(r"^## ", m._raw_body(p), re.MULTILINE))
    print(f"{n:5d} chars | H2={h2} | {p.name}")
