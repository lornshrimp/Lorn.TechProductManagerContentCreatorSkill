from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
src = (ROOT / ".workbuddy" / "_chk_out.txt").read_text(encoding="utf-8", errors="ignore")
lines = src.splitlines()

res = []
res.append("总行数 = %d" % len(lines))
res.append("")
res.append("== 全部含 ❌ 的行 ==")
bad = [l for l in lines if "\u274c" in l]
res.append("count = %d" % len(bad))
for l in bad:
    res.append(l)
res.append("")
res.append("== 含 2026-10-06 的行 ==")
for i, l in enumerate(lines):
    if "2026-10-06" in l:
        res.append("%d| %s" % (i, l))
res.append("")
res.append("== 尾部 40 行 ==")
for l in lines[-40:]:
    res.append(l)

(ROOT / ".workbuddy" / "_chk_summary.txt").write_text("\n".join(res), encoding="utf-8")
print("OK bad=%d" % len(bad))
