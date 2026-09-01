# -*- coding: utf-8 -*-
"""平台稿合规预检：字数/保真比例/两两相似度/与终稿相似度
用法: python tmp_platsim.py <选题目录>
"""
import re, sys, difflib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tmp_wc import count_body_chars, BODY_TRUNCATE_MARKERS

RATIO = {"知乎-": 0.90, "微信-": 0.85, "百家号-": 0.70, "CSDN-": 0.70, "头条-": 0.70}
H2MIN = {"知乎-": 4, "微信-": 4, "百家号-": 3, "CSDN-": 4, "头条-": 3}

EXTRA = ["[封面图提示词]", "[内容简介]", "[配图"]


def body(path: Path) -> str:
    t = path.read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e != -1:
            t = t[e + 4:]
    t = re.sub(r"^#\s+.*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"^\[→.*$", "", t, flags=re.MULTILINE)
    cut = len(t)
    for m in BODY_TRUNCATE_MARKERS + EXTRA:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return re.sub(r"\s+", "", t[:cut])


def h2(path: Path) -> int:
    t = path.read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e != -1:
            t = t[e + 4:]
    cut = len(t)
    for m in BODY_TRUNCATE_MARKERS + EXTRA:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return len(re.findall(r"^##(?!#)\s+", t[:cut], flags=re.MULTILINE))


d = Path(sys.argv[1])
finals = sorted(d.glob("终稿-*.md"))
fn = finals[0] if finals else None
fc = count_body_chars(fn) if fn else 0
fb = body(fn) if fn else ""
print("终稿: %s  字数=%d" % (fn.name if fn else "（缺失）", fc))
print("-" * 72)

plats = [f for f in sorted(d.glob("*.md"))
         if any(f.name.startswith(p) for p in RATIO)]
for p in plats:
    pfx = next((k for k in RATIO if p.name.startswith(k)), "")
    n = count_body_chars(p)
    h = h2(p)
    need = int(fc * RATIO[pfx])
    ok_n = "✅" if n >= need else "❌"
    ok_h = "✅" if h >= H2MIN[pfx] else "❌"
    sim = difflib.SequenceMatcher(a=body(p), b=fb, autojunk=False).ratio()
    ok_s = "✅" if sim < 0.99 else "❌"
    print("%-34s %5d字 (需≥%d) %s  H2=%d(需≥%d) %s  与终稿相似度=%.1f%% %s"
          % (p.name, n, need, ok_n, h, H2MIN[pfx], ok_h, sim * 100, ok_s))

print("-" * 72)
names = [p.name for p in plats]
worst = 0
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = d / names[i], d / names[j]
        s = difflib.SequenceMatcher(a=body(a), b=body(b), autojunk=False).ratio()
        worst = max(worst, s)
        flag = "❌" if s >= 0.85 else "✅"
        print("%-30s vs %-30s %.1f%% %s" % (names[i][:28], names[j][:28], s * 100, flag))
print("-" * 72)
print("最高两两相似度: %.1f%%  -> %s" % (worst * 100, "✅ 达标" if worst < 0.85 else "❌ 需差异化改写"))
