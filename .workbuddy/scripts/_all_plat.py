import io, sys, runpy
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
CHECKER = ROOT / ".workbuddy" / "scripts" / "规范校验.py"

buf = io.StringIO()
_old = sys.stdout
sys.stdout = buf
ns = runpy.run_path(str(CHECKER), run_name="_notmain_")
sys.stdout = _old

count_body_chars = ns["count_body_chars"]
extract_body_text = ns["extract_body_text"]
text_similarity = ns["text_similarity"]

BASE = ROOT / "drafts" / "2026-10-06"
PREF = ("知乎-", "微信-", "头条-", "百家号-", "CSDN-")

lines = []
for D in sorted([p for p in BASE.iterdir() if p.is_dir()]):
    finals = list(D.glob("终稿-*.md"))
    if not finals:
        continue
    final = finals[0]
    fc = count_body_chars(final)
    ft = extract_body_text(final)
    plats = sorted([p for p in D.glob("*.md") if p.name.startswith(PREF)])
    lines.append("==== %s ====" % D.name)
    lines.append("终稿 = %d 字" % fc)
    for p in plats:
        n = count_body_chars(p)
        sim = text_similarity(extract_body_text(p), ft)
        lines.append("  %-6s 字数 %4d | 占终稿 %3d%% | 与终稿 %.4f" % (p.name.split("-")[0], n, n * 100 // fc, sim))
    mx = 0.0
    mxpair = ""
    for i in range(len(plats)):
        for j in range(i + 1, len(plats)):
            s = text_similarity(extract_body_text(plats[i]), extract_body_text(plats[j]))
            if s > mx:
                mx, mxpair = s, "%s/%s" % (plats[i].name[:3], plats[j].name[:3])
    lines.append("  MAX_PAIR = %.4f (%s)" % (mx, mxpair))
    lines.append("")

(ROOT / ".workbuddy" / "_all_plat.txt").write_text("\n".join(lines), encoding="utf-8")
print("OK")
