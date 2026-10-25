# -*- coding: utf-8 -*-
"""2026-09-19 三题终稿/平台稿字数与保真比终测。"""
import sys, difflib
from pathlib import Path

BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
sys.path.insert(0, str(BASE / ".workbuddy" / "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("chk", BASE / ".workbuddy" / "scripts" / "规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

count_body_chars = chk.count_body_chars
extract_body_text = chk.extract_body_text

TOPICS = {
    "A-住建部存量时代": ("住建部房地产进入存量时代-现房销售改的是哪本账", "现房销售改的是哪本账"),
    "B-人民币升破6.7": ("人民币兑美元升破6.7-汇率升值的两本账", "汇率升值的两本账"),
    "C-失业率18.9%": ("8月16-24岁失业率18.9%-统计口径这本账", "统计口径这本账"),
}
PLATS = {"知乎": "知乎", "微信": "微信", "百家号": "百家号", "CSDN": "CSDN", "头条": "头条"}


def sim(a, b):
    A = "".join(extract_body_text(a).split())
    B = "".join(extract_body_text(b).split())
    return difflib.SequenceMatcher(None, A, B, autojunk=False).ratio()


for label, (d, suf) in TOPICS.items():
    dd = BASE / "drafts" / "2026-09-19" / d
    final = dd / f"终稿-{suf}.md"
    fw = count_body_chars(final)
    print(f"=== {label} 终稿={fw} ===")
    plats = {}
    for p, pre in PLATS.items():
        f = dd / f"{pre}-{suf}.md"
        w = count_body_chars(f)
        plats[p] = f
        print(f"  {p}: {w}字 保真={w/fw*100:.1f}%  vs终稿={sim(f,final)*100:.1f}%")
    keys = list(plats)
    mx = 0; pair = ""
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            r = sim(plats[keys[i]], plats[keys[j]]) * 100
            if r > mx:
                mx = r; pair = f"{keys[i]}x{keys[j]}"
    print(f"  平台两两最高: {mx:.1f}% ({pair})")
