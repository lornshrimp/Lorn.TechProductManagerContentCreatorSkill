# -*- coding: utf-8 -*-
import sys, re, difflib, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16/约谈在线酒店预订平台-竞争秩序账本")
a = chk.extract_body_text(d/"草稿-约谈在线酒店预订平台.md")
b = chk.extract_body_text(d/"润色稿-约谈在线酒店预订平台.md")
sim = difflib.SequenceMatcher(a=a,b=b,autojunk=False).ratio()
print(f"draft={len(a)} polish={len(b)} similarity={sim*100:.2f}% diff={(1-sim)*100:.2f}%")
