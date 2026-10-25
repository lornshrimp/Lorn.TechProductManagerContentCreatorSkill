# -*- coding: utf-8 -*-
import runpy, re
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
ns = runpy.run_path(str(ROOT/".workbuddy"/"scripts"/"规范校验.py"), run_name="_m")
cbc = ns["count_body_chars"]; trunc = ns["BODY_TRUNCATE_MARKERS"]
D = ROOT/"drafts"/"2026-09-25"/"美团抽成太多-25元外卖的三方账"
for name in ["草稿-三方账.md"]:
    p = D/name
    t = p.read_text(encoding="utf-8")
    body = t
    for m in trunc:
        i = body.find(m)
        if i != -1: body = body[:i]; break
    h2 = len(re.findall(r"^##\s+", body, re.M))
    paras = [x.strip() for x in body.split("\n\n") if x.strip() and not x.strip().startswith("#")]
    longs = [(i, len(re.findall(r"[\u4e00-\u9fff]", x))) for i, x in enumerate(paras, 1) if len(re.findall(r"[\u4e00-\u9fff]", x)) > 300]
    print(f"{name}: count_body_chars={cbc(p)} H2={h2} 超长段={len(longs)} {longs}")
