# -*- coding: utf-8 -*-
import re
from pathlib import Path
D = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-17/平陆运河开通-运费省给了谁")
src = D / "润色稿-平陆运河的运费账.md"
txt = src.read_text(encoding="utf-8")
body = re.sub(r"^---\n.*?\n---\n", "", txt, count=1, flags=re.S)
fm = ("---\ntype: 终稿\ndate: 2026-09-17\ntopic: 平陆运河开通——省下 623 公里的运费归谁\n"
      "model: deai-review\n审核结论: 通过\n---\n")
(D / "终稿-平陆运河的运费账.md").write_text(fm + body, encoding="utf-8")
print("WROTE", (D / "终稿-平陆运河的运费账.md").name)
