"""平台稿保真比与相似度实测（逐平台）"""
import sys, importlib.util
from pathlib import Path
import difflib

BASE = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("v", BASE / ".workbuddy" / "scripts" / "规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

dirs = [BASE / "drafts" / "2026-09-20" / d for d in sorted(__import__("os").listdir(BASE / "drafts" / "2026-09-20"))]
out = []
for d in dirs:
    finals = list(d.glob("终稿-*.md"))
    if not finals:
        out.append(f"== {d.name}: NO 终稿")
        continue
    fin = finals[0]
    ftext = m.extract_body_text(fin)
    fn = m.count_body_chars(fin)
    out.append(f"== {d.name}")
    out.append(f"   终稿 = {fn}")
    plats = []
    for p in sorted(d.glob("*.md")):
        if p.name.startswith(("终稿", "草稿", "润色稿", "去AI化", "编辑终审", "大纲", "标题方案", "研究报告")):
            continue
        pn = m.count_body_chars(p)
        try:
            pt = m.extract_body_text(p)
            r = difflib.SequenceMatcher(None, "".join(ftext.split()), "".join(pt.split()), autojunk=False).ratio()
        except Exception as e:
            r = float("nan")
        ratio = pn / fn if fn else 0
        plats.append((p.name, pn, ratio, r))
    for name, pn, ratio, sim in plats:
        out.append(f"   {name}: {pn}  保真={ratio:.1%}  与终稿相同度={sim:.1%}")
    for i in range(len(plats)):
        for j in range(i + 1, len(plats)):
            ta = "".join(m.extract_body_text(d / plats[i][0]).split())
            tb = "".join(m.extract_body_text(d / plats[j][0]).split())
            r = difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()
            out.append(f"   [两两] {plats[i][0]} × {plats[j][0]} = {r:.1%}")

txt = "\n".join(out)
(BASE / ".workbuddy" / "scripts" / "_plat_a.txt").write_text(txt, encoding="utf-8")
print(txt)
