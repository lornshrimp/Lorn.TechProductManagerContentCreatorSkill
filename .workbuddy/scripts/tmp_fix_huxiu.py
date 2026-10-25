# -*- coding: utf-8 -*-
"""虎嗅精修 + 小红书"""
import re
from pathlib import Path
BSK = Path("C:/Users/lorns/AppData/Local/Temp/bsk_raw")
OUT = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14")
DATE = "2026-09-14"; CT = "2026-09-14 07:20"

def rd(p):
    p = Path(p); return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

s = re.sub(r"^A new bsk version is available.*\n?", "", rd(BSK / "huxiu.txt"), flags=re.M)
lines = [l.strip() for l in s.split("\n")]

def block_after(marker, n=30):
    try:
        i = lines.index(marker)
    except ValueError:
        return []
    out = []
    for l in lines[i+1:i+1+n]:
        if not l: continue
        if l in ("前沿科技","商业消费","车与出行","金融财经","国际热点","游戏娱乐","健康","书影音","医疗","观点","其他","原创","48小时热文","48小时周","24小时","查看更多","热点","资讯"): 
            continue
        if 8 <= len(l) <= 60: out.append(l)
    return out

h24 = block_after("24小时", 24)
h48 = block_after("48小时热文", 40)
b = "## 虎嗅24小时快讯\n\n| 序号 | 快讯 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(h24), 1):
    b += f"| {i} | {t} |\n"
b += "\n## 虎嗅48小时热文\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(h48), 1):
    b += f"| {i} | {t} |\n"
txt = f"---\ntitle: 虎嗅48h热文 · {DATE}\ndate: {DATE}\nsource: 虎嗅48h热文\ncollectTime: {CT}\n---\n\n{b}\n"
(OUT / "虎嗅48h热文.md").write_text(txt, encoding="utf-8")
print("WROTE 虎嗅", len(txt))
print(b[:2500])
