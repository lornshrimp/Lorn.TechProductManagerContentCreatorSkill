# -*- coding: utf-8 -*-
"""2026-10-15 字数/结构实测（复用 规范校验.py 口径）"""
import sys, io, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

targets = sys.argv[1:]
for t in targets:
    p = Path(t)
    if not p.is_absolute():
        p = ROOT / t
    if not p.exists():
        print(f"MISSING {p}")
        continue
    n = chk.count_body_chars(p)
    txt = p.read_text(encoding='utf-8', errors='ignore')
    body = chk._raw_body(p)
    paras = [x.strip() for x in body.split("\n\n") if x.strip()]
    import re
    longest = max((len(re.findall(r"[\u4e00-\u9fff]", x)) for x in paras), default=0)
    h2 = len(re.findall(r"^## ", body, re.MULTILINE))
    print(f"{p.name}\tchars={n}\tH2={h2}\tmaxpara={longest}")
