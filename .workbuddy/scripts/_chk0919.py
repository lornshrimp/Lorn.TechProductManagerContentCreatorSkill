from pathlib import Path
import re

root = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
t = (root / ".workbuddy" / "_校验_2026-09-19.txt").read_text(encoding="utf-8")

seg = "drafts" + chr(92) + "2026-09-19" + chr(92)
print("含 2026-09-19 选题目录段:", seg in t)

names = [
    "8月16-24岁失业率18.9%-统计口径这本账",
    "人民币兑美元升破6.7-汇率升值的两本账",
    "住建部房地产进入存量时代-现房销售改的是哪本账",
]
for n in names:
    print(n, "出现次数:", t.count(n))

# 历史 vs 今日：统计报告中出现的日期目录
dates = sorted(set(re.findall(r"drafts[\\/](\d{4}-\d{2}-\d{2})[\\/]", t)))
print("报告中涉及的日期目录:", dates)
