from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
p = ROOT / "drafts" / "2026-10-06" / "央行四箭齐发-7000亿再贷款定向六张网" / "合规自检表-央行四箭齐发-7000亿再贷款定向六张网.md"
t = p.read_text(encoding="utf-8")

reps = [
    ("CSDN 0.4367", "CSDN 0.4363"),
    ("头条 0.6497", "头条 0.6501"),
    ("知乎 0.8607", "知乎 0.8608"),
    ("最高 0.8417", "最高 0.8415"),
    ("0.6891（vs 知乎）", "0.6900（vs 知乎）"),
    ("正文实测 3105 字", "正文实测 3101 字"),
    ("复测最高 0.8417", "复测最高 0.8415"),
]
miss = []
for a, b in reps:
    if a in t:
        t = t.replace(a, b)
    else:
        miss.append(a)
p.write_text(t, encoding="utf-8")
print("OK miss=%s" % miss)
