import io, sys, runpy, importlib.util
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy" / "scripts" / "规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

BASE = ROOT / "drafts" / "2026-10-09"
PREF = ("知乎-", "微信-", "头条-", "百家号-", "CSDN-")
MIN = {"知乎-": 0.90, "微信-": 0.85, "百家号-": 0.70, "CSDN-": 0.70, "头条-": 0.70}

lines = []
for D in sorted([p for p in BASE.iterdir() if p.is_dir()]):
    finals = list(D.glob("终稿-*.md"))
    if not finals:
        continue
    final = finals[0]
    fc = m.count_body_chars(final)
    ft = m.extract_body_text(final)
    plats = sorted([p for p in D.glob("*.md") if p.name.startswith(PREF)])
    lines.append("==== %s ====" % D.name)
    lines.append("终稿 = %d 字 | H2=%d" % (fc, len(__import__('re').findall(r"^## ", m._raw_body(final), __import__('re').MULTILINE))))
    for p in plats:
        pf = next(k for k in MIN if p.name.startswith(k))
        n = m.count_body_chars(p)
        sim = m.text_similarity(m.extract_body_text(p), ft)
        ok = "OK" if n >= fc * MIN[pf] else "SHORT(need %d)" % int(fc * MIN[pf] + 1)
        lines.append("  %-6s 字数 %4d | 占终稿 %3d%% | 与终稿 %.4f | %s" % (pf.rstrip('-'), n, n * 100 // fc, sim, ok))
    mx, mxpair = 0.0, ""
    for i in range(len(plats)):
        for j in range(i + 1, len(plats)):
            s = m.text_similarity(m.extract_body_text(plats[i]), m.extract_body_text(plats[j]))
            if s > mx:
                mx, mxpair = s, "%s/%s" % (plats[i].name.split("-")[0], plats[j].name.split("-")[0])
    lines.append("  MAX_PAIR = %.4f (%s)" % (mx, mxpair))
    lines.append("")

(ROOT / ".workbuddy" / "_plat1009.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
