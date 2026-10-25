# -*- coding: utf-8 -*-
"""诊断：头条稿各段与微信/知乎各段的最大相似度，定位重合处。"""
import difflib
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
D = BASE / "drafts" / "2026-09-19" / "8月16-24岁失业率18.9%-统计口径这本账"


def paras(name):
    t = (D / name).read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        i = t.find("\n---", 3)
        t = t[i + 4:]
    t = re.sub(r"^#\s+.*$", "", t, flags=re.M)
    for m in ["## 视觉与配图", "## 配图搜索替换指令", "## SEO 关键词"]:
        idx = t.find(m)
        if idx != -1:
            t = t[:idx]
    return [re.sub(r"\s+", "", p) for p in t.split("\n\n") if re.sub(r"\s+", "", p)]


def sim(a, b):
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


tt = paras("头条-统计口径这本账.md")
wx = paras("微信-统计口径这本账.md")
zh = paras("知乎-统计口径这本账.md")
others = wx + zh

print("=== 头条各段 vs 微信/知乎 最大相似度 ===")
for i, p in enumerate(tt):
    best, bj = 0.0, -1
    for j, q in enumerate(others):
        s = sim(p, q)
        if s > best:
            best, bj = s, j
    mark = "  <<<" if best >= 0.5 and len(p) >= 12 else ""
    print(f"[{i:02d}] len={len(p):4d} max={best:.0%}{mark}  {p[:46]}")
