# -*- coding: utf-8 -*-
"""C 题正文最长段落与 H2 数（截断附属区）。"""
import re
from pathlib import Path

D = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-19/8月16-24岁失业率18.9%-统计口径这本账")
TRUNC = ["## 素材溯源", "## 质量自检报告", "## 视觉与配图", "## 配图搜索替换指令", "## SEO 关键词"]

for name in ["终稿-统计口径这本账.md", "头条-统计口径这本账.md", "微信-统计口径这本账.md", "知乎-统计口径这本账.md", "百家号-统计口径这本账.md", "CSDN-统计口径这本账.md"]:
    t = (D / name).read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        i = t.find("\n---", 3)
        t = t[i + 4:]
    h2 = len(re.findall(r"^##\s+", t, flags=re.M))
    cut = len(t)
    for m in TRUNC:
        idx = t.find(m)
        if idx != -1:
            cut = min(cut, idx)
    body = t[:cut]
    paras = [re.sub(r"\s+", "", p) for p in body.split("\n\n")]
    paras = [p for p in paras if p and not p.startswith("#")]
    longest = max((len(p) for p in paras), default=0)
    print(f"{name}: H2={h2} 最长段={longest}")
