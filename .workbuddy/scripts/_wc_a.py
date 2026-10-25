# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16/约谈在线酒店预订平台-竞争秩序账本")
for f in sorted(d.glob("*.md")):
    print(f.name, chk.count_body_chars(f))
