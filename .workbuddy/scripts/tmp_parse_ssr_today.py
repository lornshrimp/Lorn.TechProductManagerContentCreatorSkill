import re
from pathlib import Path

BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-15/_raw")


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def dump(name, rows):
    (BASE / name).write_text("\n".join(rows), encoding="utf-8")
    print(name, len(rows))


# ---- IT之家 ----
h = (BASE / "ithome_home.html").read_text(encoding="utf-8", errors="ignore")
seen, rows = set(), []
for m in re.finditer(r'<a[^>]+href="(https://www\.ithome\.com/0/\d+/\d+\.htm)"[^>]*>(.*?)</a>', h, re.S):
    t = clean(m.group(2))
    if 10 < len(t) < 70 and t not in seen:
        seen.add(t)
        rows.append(f"{len(rows)+1}##{t}")
    if len(rows) >= 30:
        break
dump("ithome.txt", rows)

# ---- 澎湃 ----
h = (BASE / "thepaper_home.html").read_text(encoding="utf-8", errors="ignore")
seen, rows = set(), []
for m in re.finditer(r'<a[^>]+href="(https://www\.thepaper\.cn/newsDetail_forward_\d+)"[^>]*>(.*?)</a>', h, re.S):
    t = clean(m.group(2))
    if 8 < len(t) < 70 and t not in seen:
        seen.add(t)
        rows.append(f"{len(rows)+1}##{t}")
    if len(rows) >= 30:
        break
dump("thepaper.txt", rows)

# ---- 网易 ----
h = (BASE / "163_home.html").read_text(encoding="utf-8", errors="ignore")
seen, rows = set(), []
for m in re.finditer(r'<a[^>]+href="(https://www\.163\.com/(?:news|dy)/article/[^"]+)"[^>]*>(.*?)</a>', h, re.S):
    t = clean(m.group(2))
    if 8 < len(t) < 70 and t not in seen:
        seen.add(t)
        rows.append(f"{len(rows)+1}##{t}")
    if len(rows) >= 30:
        break
dump("163news.txt", rows)

# ---- 品玩 ----
h = (BASE / "pingwest_home.html").read_text(encoding="utf-8", errors="ignore")
seen, rows = set(), []
for m in re.finditer(r'<a[^>]+href="(/a/\d+)"[^>]*>(.*?)</a>', h, re.S):
    t = clean(m.group(2))
    if 8 < len(t) < 80 and t not in seen:
        seen.add(t)
        rows.append(f"{len(rows)+1}##{t}")
    if len(rows) >= 25:
        break
dump("pingwest.txt", rows)

# ---- InfoQ ----
h = (BASE / "infoq_home.html").read_text(encoding="utf-8", errors="ignore")
seen, rows = set(), []
for m in re.finditer(r'href="(/article/[^"]+)"[^>]*>(.*?)</a>', h, re.S):
    t = clean(m.group(2))
    if 10 < len(t) < 80 and t not in seen:
        seen.add(t)
        rows.append(f"{len(rows)+1}##{t}")
    if len(rows) >= 30:
        break
dump("infoq.txt", rows)
