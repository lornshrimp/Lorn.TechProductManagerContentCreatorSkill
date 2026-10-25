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

D = ROOT / "drafts" / "2026-10-06" / "央行四箭齐发-7000亿再贷款定向六张网"
final = list(D.glob("终稿-*.md"))[0]
PREF = ("知乎-", "微信-", "头条-", "百家号-", "CSDN-")
plats = sorted([p for p in D.glob("*.md") if p.name.startswith(PREF)])

lines = []
fc = count_body_chars(final)
ft = extract_body_text(final)
lines.append("终稿 %s = %d 字" % (final.name, fc))
lines.append("平台稿数 = %d" % len(plats))
lines.append("")
for p in plats:
    n = count_body_chars(p)
    sim = text_similarity(extract_body_text(p), ft)
    lines.append("%s" % p.name)
    lines.append("  字数 %d | 占终稿 %d%% | 与终稿相似度 %.4f" % (n, n * 100 // fc, sim))
lines.append("")
lines.append("== 平台两两相似度 ==")
mx = 0.0
mxpair = ""
for i in range(len(plats)):
    for j in range(i + 1, len(plats)):
        s = text_similarity(extract_body_text(plats[i]), extract_body_text(plats[j]))
        lines.append("  %s vs %s = %.4f" % (plats[i].name[:4], plats[j].name[:4], s))
        if s > mx:
            mx, mxpair = s, "%s/%s" % (plats[i].name[:4], plats[j].name[:4])
lines.append("")
lines.append("MAX_PAIR = %.4f (%s)" % (mx, mxpair))

(ROOT / ".workbuddy" / "_c_plat.txt").write_text("\n".join(lines), encoding="utf-8")
print("OK")
