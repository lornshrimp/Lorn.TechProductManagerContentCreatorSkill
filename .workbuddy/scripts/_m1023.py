# -*- coding: utf-8 -*-
"""差异率/字数/保真/相似度/锚文本 一体脚本（改 DATE/TOPIC 即复用）"""
import io, sys, re, difflib, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
DATE = "2026-10-23"

spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def raw(p):
    t = p.read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        e = t.find("\n---", 3)
        t = t[e + 4:] if e != -1 else t
    t = re.sub(r"^#\s+.*$", "", t, flags=re.MULTILINE)
    cut = len(t)
    for m in chk.BODY_TRUNCATE_MARKERS + ["[封面图提示词]", "[内容简介]", "[配图"]:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]


def diffrate(a, b):
    A = re.sub(r"\s+", "", a)
    B = re.sub(r"\s+", "", b)
    sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
    blocks = [o for o in sm.get_opcodes() if o[0] != "equal" and (o[2] - o[1] > 0 or o[4] - o[3] > 0)]
    chars = sum(max(o[2] - o[1], o[4] - o[3]) for o in blocks)
    return chars / max(len(A), 1) * 100, len(blocks)


for d in sorted((ROOT / "drafts" / DATE).iterdir()):
    if not d.is_dir():
        continue
    print("\n" + "=" * 60)
    print("###", d.name)
    draft = next(d.glob("草稿-*.md"), None)
    pol = next(d.glob("润色稿-*.md"), None)
    fin = next(d.glob("终稿-*.md"), None)
    for label, f in (("草稿", draft), ("润色", pol), ("终稿", fin)):
        if f:
            print(f"  {label}: {chk.count_body_chars(f)} 字")
    if draft and pol:
        r, nb = diffrate(raw(draft), raw(pol))
        print(f"  草稿→润色 差异率 {r:.2f}%  变更块 {nb}")
    if fin:
        base = chk.count_body_chars(fin)
        print(f"  终稿基准 {base}")
        pfs = sorted([f for f in d.glob("*.md") if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)])
        texts = {}
        for pf in pfs:
            n = chk.count_body_chars(pf)
            ratio = n * 100 / base if base else 0
            sim = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(fin))
            texts[pf.name] = chk.extract_body_text(pf)
            print(f"    {pf.name}: {n} 字 保真 {ratio:.1f}% 与终稿 {sim:.2%}")
        names = sorted(texts)
        mx = 0
        pair = ""
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                s = chk.text_similarity(texts[names[i]], texts[names[j]])
                if s > mx:
                    mx, pair = s, f"{names[i]} × {names[j]}"
        print(f"  平台两两最高 {mx:.2%} ({pair})")
        for pf in pfs:
            iss = chk.check_anchor_quality(pf)
            for i in iss:
                print("   ", i.strip())
print("\nDONE")
