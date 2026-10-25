# -*- coding: utf-8 -*-
"""由 润色稿 生成 终稿（deai-review 通过）：替换 frontmatter 为终稿规范（含 genre/title）"""
import io, sys, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
BASE = ROOT / "drafts/2026-10-14"

ITEMS = [
    ("老干妈用AI一年54亿-拣椒工从600人减至48人",
     "润色稿-54亿的营收-552个消失的岗位-老干妈这笔账怎么记.md",
     "54亿的营收，552个消失的岗位：老干妈这笔账怎么记"),
    ("茶百道涉嫌操纵IPO被香港证监会停牌",
     "润色稿-一只股票的需求可以是写出来的-茶百道停牌这件事.md",
     "一只股票的「需求」可以是写出来的：茶百道停牌这件事"),
    ("北京社保缴费基数下限7270元vs法定最低工资2540元",
     "润色稿-两把尺子量同一个人-2540元的最低工资与7270元的社保基数.md",
     "两把尺子量同一个人：2540元的最低工资与7270元的社保基数"),
]

for topic, src, title in ITEMS:
    d = BASE / topic
    t = (d / src).read_text(encoding="utf-8")
    # 剥离旧 frontmatter
    assert t.startswith("---"), src
    end = t.find("\n---", 3)
    body = t[end + 4:].lstrip("\n")
    fm = (f"---\ntype: 终稿\ndate: 2026-10-14\ntopic: {topic}\ngenre: 深度分析体\n"
          f"title: {title}\nmodel: deai-review\n---\n\n")
    out = d / src.replace("润色稿-", "终稿-")
    out.write_text(fm + body, encoding="utf-8")
    print("WROTE", out.name, len(fm + body))
