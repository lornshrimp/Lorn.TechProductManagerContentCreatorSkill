from pathlib import Path
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-22/反外国制裁法新案例安世21.39亿财产被查封-资产保全的定价权")
src = (d / "润色稿-资产保全的定价权.md").read_text(encoding="utf-8")
fm = """---
type: 终稿
date: 2026-09-22
topic: 反外国制裁法新案例 · 安世 21.39 亿元财产保全的定价权
genre: 深度分析体
审核结论: 通过
model: deai-review
---
"""
body = src.split("---", 2)[2]
(d / "终稿-资产保全的定价权.md").write_text(fm + body, encoding="utf-8")
print("OK")
