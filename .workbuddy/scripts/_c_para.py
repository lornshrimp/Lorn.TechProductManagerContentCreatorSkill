# -*- coding: utf-8 -*-
"""段落规整度实测：正文段落中文字符数标准差"""
import sys, re, statistics
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]


def paras(path):
    t = Path(path).read_text(encoding="utf-8")
    t = re.sub(r"^---\n.*?\n---\n", "", t, flags=re.S)
    t = t.split("## 素材溯源表")[0]
    t = re.sub(r"^#\s+.*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"^##\s+.*$", "", t, flags=re.MULTILINE)
    ps = [p.strip() for p in t.split("\n\n") if p.strip()]
    return [len(re.findall(r"[\u4e00-\u9fff]", p)) for p in ps]


out = []
for f in sys.argv[1:]:
    ls = paras(f)
    out.append(f"{Path(f).name}: 段数={len(ls)} 段长标准差={statistics.pstdev(ls):.2f} 最长段={max(ls)} 最短段={min(ls)}")
txt = "\n".join(out)
(BASE / ".workbuddy" / "_c_para.txt").write_text(txt, encoding="utf-8")
print(txt)
