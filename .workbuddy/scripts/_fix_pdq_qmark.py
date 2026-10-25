# -*- coding: utf-8 -*-
"""09-14 胖东来 CSDN 备选标题补问号："……怎么念" → "……怎么念？"（先打印出现位置供核对）"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
f = ROOT / "drafts" / "2026-09-14" / "胖东来四年合同-把招工写成招生的用工账本" / "标题方案.md"
lines = f.read_text(encoding="utf-8").split("\n")
out = []
n = 0
for i, ln in enumerate(lines, 1):
    if "怎么念" in ln:
        out.append(f"[L{i}] 原: {ln.strip()[:110]}")
        if not re.search(r"怎么念\s*？", ln):
            lines[i - 1] = ln.replace("怎么念", "怎么念？")
            n += 1
if n:
    f.write_text("\n".join(lines), encoding="utf-8")
out.append(f"\n补问号 {n} 处")
print("PYOK", n)
(ROOT / ".workbuddy" / "_胖东来备选补问号.txt").write_text("\n".join(out), encoding="utf-8")
