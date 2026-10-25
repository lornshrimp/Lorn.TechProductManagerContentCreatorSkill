# -*- coding: utf-8 -*-
import re, sys, runpy, io
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
# 直接复用 规范校验.count_body_chars
ns = runpy.run_path(str(ROOT/".workbuddy"/"scripts"/"规范校验.py"), run_name="_cbc_mod")
cbc = ns["count_body_chars"]
D = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"
out=[]
for n in ["草稿-限量这本账.md","润色稿-限量这本账.md"]:
    out.append(f"{n}: {cbc(D/n)}")
Path(str(ROOT/".workbuddy"/"_cbc_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print("done")
