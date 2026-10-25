# -*- coding: utf-8 -*-
"""2026-10-08 差异率实测：纯正文（截断于附属区）difflib 相似度 → 差异率 = 1 - 相似度"""
import sys, io, re, difflib
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MARKERS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图",
    "## 内容简介", "## 互动引导", "## SEO 关键词", "## 配图详情",
    "# 附属内容区域", "## 配图搜索替换指令", "## 参考来源",
    "## 润色说明", "## 发布建议", "[封面图提示词]", "[内容简介]", "[配图",
]


def body(path):
    t = Path(path).read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        e = t.find("\n---", 3)
        t = t[e + 4:] if e != -1 else t
    t = re.sub(r"^#\s+.*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"^\[→.*$", "", t, flags=re.MULTILINE)
    cut = len(t)
    for m in MARKERS:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return re.sub(r"\s+", "", t[:cut])


def sim(a, b):
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    A, B = body(a), body(b)
    s = sim(A, B)
    print(f"A={Path(a).name} len={len(A)}")
    print(f"B={Path(b).name} len={len(B)}")
    print(f"similarity={s:.4f}  diff={1-s:.4%}")
