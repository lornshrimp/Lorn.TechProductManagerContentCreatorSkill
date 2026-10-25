# -*- coding: utf-8 -*-
"""正文差异率 + 字数实测"""
import sys, io, re, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", BASE / ".workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def body(p):
    t = p.read_text(encoding='utf-8', errors='ignore')
    if t.startswith('---'):
        e = t.find('\n---', 3)
        t = t[e + 4:] if e != -1 else t
    t = re.sub(r'^#\s+.*$', '', t, flags=re.MULTILINE)
    for mk in m.BODY_TRUNCATE_MARKERS:
        i = t.find(mk)
        if i != -1:
            t = t[:i]
            break
    return t


a = BASE / sys.argv[1]
b = BASE / sys.argv[2]
ta, tb = body(a), body(b)
na = len(re.findall(r'[\u4e00-\u9fff]', ta))
nb = len(re.findall(r'[\u4e00-\u9fff]', tb))
sim = m.text_similarity(ta, tb)
print(f"{a.name}: {na} chars")
print(f"{b.name}: {nb} chars")
print(f"similarity={sim:.4f}  diff={1-sim:.4%}")
print("BOTH_OK" if (na >= 2500 and nb >= 2500 and (1 - sim) >= 0.05) else "CHECK")
