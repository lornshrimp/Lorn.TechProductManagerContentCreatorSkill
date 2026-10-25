from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
lines = (ROOT / ".workbuddy" / "_chk_out.txt").read_text(encoding="utf-8", errors="ignore").splitlines()

blocks = []
i = 0
while i < len(lines):
    if lines[i].startswith("[选题目录]") and "2026-10-06" in lines[i]:
        blk = [lines[i]]
        j = i + 1
        while j < len(lines) and (lines[j].startswith("  ") or lines[j].strip() == ""):
            blk.append(lines[j])
            j += 1
        blocks.append("\n".join(blk).rstrip())
        i = j
    else:
        i += 1

today_bad = sum(b.count("\u274c") for b in blocks)
today_warn = sum(b.count("\u26a0") for b in blocks)

out = []
out.append("今日（2026-10-06）选题目录块数 = %d" % len(blocks))
out.append("今日 ❌ 数 = %d" % today_bad)
out.append("今日 ⚠️ 数 = %d" % today_warn)
out.append("")
for b in blocks:
    out.append(b)
    out.append("")
out.append("== 全局统计行 ==")
for l in lines:
    if "共发现" in l:
        out.append(l)

(ROOT / ".workbuddy" / "_chk_today.txt").write_text("\n".join(out), encoding="utf-8")
print("OK today_bad=%d" % today_bad)
