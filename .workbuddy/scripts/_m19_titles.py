# -*- coding: utf-8 -*-
import re
from pathlib import Path

BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
TOPICS = {
    "A": ("住建部房地产进入存量时代-现房销售改的是哪本账", "现房销售改的是哪本账"),
    "B": ("人民币兑美元升破6.7-汇率升值的两本账", "汇率升值的两本账"),
    "C": ("8月16-24岁失业率18.9%-统计口径这本账", "统计口径这本账"),
}
PLATS = ["知乎", "微信", "百家号", "CSDN", "头条"]

for label, (d, suf) in TOPICS.items():
    dd = BASE / "drafts" / "2026-09-19" / d
    fin = dd / f"终稿-{suf}.md"
    txt = fin.read_text(encoding="utf-8")
    m = re.search(r"^#\s+(.+)$", txt, re.M)
    print(f"[{label}] 终稿标题: {m.group(1) if m else '?'}")
    for p in PLATS:
        t = (dd / f"{p}-{suf}.md").read_text(encoding="utf-8")
        mt = re.search(r'^title:\s*"?(.+?)"?\s*$', t, re.M)
        print(f"    {p}: {mt.group(1) if mt else '?'}")
