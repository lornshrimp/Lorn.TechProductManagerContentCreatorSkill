# -*- coding: utf-8 -*-
"""2026-10-24 度量：字数 / 平台保真 / 与终稿相似度 / 平台两两相似度 / H2 / 最长段"""
import io, sys, re, difflib, itertools, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts")))
import importlib.util
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-10-24")
PLAT = ["知乎-", "微信-", "百家号-", "CSDN-", "头条-"]
RATIO = {"知乎-": 0.90, "微信-": 0.85, "百家号-": 0.70, "CSDN-": 0.70, "头条-": 0.70}

for d in sorted(ROOT.iterdir()):
    if not d.is_dir():
        continue
    print("=" * 70)
    print(d.name)
    files = {}
    for f in sorted(d.glob("*.md")):
        files[f.name] = f
    final = next((f for n, f in files.items() if n.startswith("终稿-")), None)
    for n, f in files.items():
        c = chk.count_body_chars(f)
        # H2 in body
        txt = f.read_text(encoding="utf-8", errors="ignore")
        start = 0
        if txt.startswith("---"):
            e = txt.find("\n---", 3)
            start = e + 4 if e != -1 else 0
        m = re.search(r"^# .*$", txt[start:], re.MULTILINE)
        if m:
            start += m.end()
        tail = re.search(r"\n## 素材溯源|\n## 质量自检|\n## 配图搜索替换指令|\n## 配图详情|\n## 视觉与配图|\n## 标题决策说明", txt[start:])
        body = txt[start:start + tail.start()] if tail else txt[start:]
        h2 = len(re.findall(r"^## ", body, re.MULTILINE))
        maxp = 0
        for blk in re.split(r"\n\s*\n", body):
            b = blk.strip()
            if not b or b.startswith(("#", "|", ">", "-", "*", "[")):
                continue
            maxp = max(maxp, len(re.findall(r"[\u4e00-\u9fff]", b)))
        print(f"  {n:42s} {c:5d}  H2={h2:2d}  maxPara={maxp}")
    if final:
        fc = chk.count_body_chars(final)
        ft = chk.extract_body_text(final)
        plats = {}
        for n, f in files.items():
            pfx = next((p for p in PLAT if n.startswith(p)), None)
            if not pfx:
                continue
            pc = chk.count_body_chars(f)
            sim = chk.text_similarity(chk.extract_body_text(f), ft)
            ratio = pc / fc if fc else 0
            ok = "OK " if ratio >= RATIO[pfx] else "LOW"
            print(f"    {pfx:5s} {pc:5d} 保真 {ratio*100:6.2f}% 需≥{RATIO[pfx]*100:.0f}% {ok}  与终稿 {sim*100:5.2f}%")
            plats[n] = chk.extract_body_text(f)
        names = sorted(plats)
        mx = 0
        pair = None
        for a, b in itertools.combinations(names, 2):
            s = chk.text_similarity(plats[a], plats[b])
            if s > mx:
                mx, pair = s, (a, b)
        if pair:
            flag = "OK" if mx < 0.85 else "OVER"
            print(f"    平台两两最高 {mx*100:.2f}% ({pair[0]} vs {pair[1]}) {flag}")
        # anchor checks
        for n, f in files.items():
            if any(n.startswith(p) for p in PLAT):
                iss = chk.check_anchor_quality(f)
                if iss:
                    print(f"    ANCHOR {n}: {iss}")
