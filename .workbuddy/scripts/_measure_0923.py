# -*- coding: utf-8 -*-
"""0923 实测脚本：复用规范校验.py 的函数，逐题实测字数/相似度/保真比/差异率。"""
import importlib.util
import io
import sys
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
SPEC = ROOT / ".workbuddy" / "scripts" / "规范校验.py"
spec = importlib.util.spec_from_file_location("guifan", str(SPEC))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

DATE = sys.argv[1] if len(sys.argv) > 1 else "2026-09-23"
out = io.StringIO()
out.write(f"=== 实测报告 {DATE} ===\n")

def h2count(p: Path) -> int:
    import re
    t = p.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(r"^## ", t, re.MULTILINE))

def maxpara(p: Path) -> int:
    import re
    body = g._raw_body(p)
    mx = 0
    for blk in re.split(r"\n\s*\n", body):
        b = blk.strip()
        if not b or b.startswith(("#", "|", ">", "-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "[")):
            continue
        mx = max(mx, len(re.findall(r"[\u4e00-\u9fff]", b)))
    return mx

base = ROOT / "drafts" / DATE
for d in sorted([x for x in base.iterdir() if x.is_dir()]):
    out.write(f"\n--- {d.name} ---\n")
    final = list(d.glob("终稿-*.md"))
    fc = g.count_body_chars(final[0]) if final else 0
    out.write(f"终稿正文字数: {fc} | H2={h2count(final[0]) if final else 0} | 最长段={maxpara(final[0]) if final else 0}\n")
    for pat in ("草稿-*.md", "润色稿-*.md"):
        for f in sorted(d.glob(pat)):
            out.write(f"  {f.name}: 字数={g.count_body_chars(f)} H2={h2count(f)} 最长段={maxpara(f)}\n")
    d1 = d.glob("草稿-*.md")
    d2 = d.glob("润色稿-*.md")
    dd = list(d1), list(d2)
    if dd[0] and dd[1]:
        import difflib
        a = g.extract_body_text(dd[0][0])
        b = g.extract_body_text(dd[1][0])
        r = difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()
        out.write(f"  草稿→润色稿差异率(1-ratio): {(1-r)*100:.2f}%\n")
    plats = []
    for pf in sorted(d.glob("*.md")):
        if any(pf.name.startswith(p) for p in g.PLATFORM_PREFIX):
            plats.append(pf)
    for pf in plats:
        n = g.count_body_chars(pf)
        ratio = (n * 100.0 / fc) if fc else 0
        sim = g.text_similarity(g.extract_body_text(pf), g.extract_body_text(final[0])) if final else 0
        out.write(f"  [平台] {pf.name}: 字数={n} 保真={ratio:.1f}% 与终稿相似={sim*100:.1f}% H2={h2count(pf)}\n")
    for i in range(len(plats)):
        for j in range(i + 1, len(plats)):
            s = g.text_similarity(g.extract_body_text(plats[i]), g.extract_body_text(plats[j]))
            if s >= 0.80:
                out.write(f"  [两两] {plats[i].name} vs {plats[j].name} = {s*100:.1f}%\n")

res = out.getvalue()
(ROOT / ".workbuddy" / "_measure_0923.txt").write_text(res, encoding="utf-8")
print("DONE")
