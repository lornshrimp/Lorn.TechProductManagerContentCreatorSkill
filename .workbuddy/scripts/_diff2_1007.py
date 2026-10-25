# -*- coding: utf-8 -*-
"""纯正文差异率（截断点固定为素材溯源/标题决策/质量自检/润色说明）"""
import sys, io, re, difflib
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
CUTS = ["## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 润色说明", "## 终审说明"]


def body(p):
    t = p.read_text(encoding='utf-8', errors='ignore')
    if t.startswith('---'):
        e = t.find('\n---', 3)
        t = t[e + 4:] if e != -1 else t
    t = re.sub(r'^#\s+.*$', '', t, flags=re.MULTILINE)
    cut = len(t)
    for mk in CUTS:
        i = t.find(mk)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]


a = BASE / sys.argv[1]
b = BASE / sys.argv[2]
ta, tb = body(a), body(b)
na = len(re.findall(r'[\u4e00-\u9fff]', ta))
nb = len(re.findall(r'[\u4e00-\u9fff]', tb))
sim = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False).ratio()
print(f"{a.name}: {na}")
print(f"{b.name}: {nb}")
print(f"similarity={sim:.4f} diff={1-sim:.2%}")
