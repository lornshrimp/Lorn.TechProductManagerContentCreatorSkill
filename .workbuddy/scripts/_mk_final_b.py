# -*- coding: utf-8 -*-
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"
t = (D/"润色稿-限量这本账.md").read_text(encoding="utf-8")
t = t.replace("type: 润色稿", "type: 终稿").replace("model: deai-polish", "model: deai-review")
(D/"终稿-限量这本账.md").write_text(t, encoding="utf-8")
print("written", len(t))
