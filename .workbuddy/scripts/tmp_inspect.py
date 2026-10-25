# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
RAW = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14/_raw")

j = json.loads((RAW/"baidu_hot.json").read_text(encoding="utf-8", errors="ignore"))
print("TOPKEYS", list(j.keys()))
d = j.get("data", {})
print("DATAKEYS", list(d.keys()))
cards = d.get("cards", [])
print("NCARDS", len(cards))
for i, c in enumerate(cards[:3]):
    print("--- card", i, list(c.keys()), c.get("component"), "content_len", len(c.get("content", [])))
    for item in c.get("content", [])[:2]:
        print("    ITEMKEYS", list(item.keys()))
        print("    ", json.dumps(item, ensure_ascii=False)[:400])

print("\n\n=== pingwest sample ===")
h = (RAW/"pingwest.html").read_text(encoding="utf-8", errors="ignore")
print(h[:1500])
print("\n\n=== infoq keys ===")
hi = (RAW/"infoq.html").read_text(encoding="utf-8", errors="ignore")
print(hi[:800])
print("has __NEXT_DATA__:", "__NEXT_DATA__" in hi)
print(re.findall(r'"title":"([^"]{5,60})"', hi)[:20])
