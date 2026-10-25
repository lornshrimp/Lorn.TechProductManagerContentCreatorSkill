# -*- coding: utf-8 -*-
import runpy
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
ns = runpy.run_path(str(ROOT/".workbuddy"/"scripts"/"规范校验.py"), run_name="_m")
cbc = ns["count_body_chars"]
p = ROOT/"research"/"美团抽成太多-25元外卖的三方账"/"研究报告.md"
print("count_body_chars =", cbc(p))
import re
t = p.read_text(encoding="utf-8")
print("raw zh =", len(re.findall(r"[\u4e00-\u9fff]", t)))
print("h2 =", len(re.findall(r"^##\s+", t, re.M)))
