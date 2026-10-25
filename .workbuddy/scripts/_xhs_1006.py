# -*- coding: utf-8 -*-
import os
BASE = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"
OUTD = os.path.join(BASE, "hotspot", "榜单", "2026-10-06")
DATE = "2026-10-06"
CT = "2026-10-06 08:45"

body = """## 小红书热榜/话题（WebSearch 兜底 · 降级）

⚠️ explore 页在无头环境仅渲染页脚，适配器未建；改采公开趋势数据。

| 序号 | 话题/热词 | 说明 |
|------|-----------|------|
| 1 | #我的十月小确幸 | 情感治愈类话题，阅读破 8.3 亿 |
| 2 | 陈都灵短卷发 / 复古摩登短发 | 巴黎时装周 LOEWE 大秀，两小时揽 5 个小红书热点，浏览量破千万 |
| 3 | 文化游话题榜 | 鲁迅故里「早」字课桌成国庆顶流打卡点，居文化游话题榜第一 |
| 4 | 大理民宿空置率 / 50 元床位无人住 | 住宿消费结构变化，旺季不旺引热议 |
| 5 | 秋日出行灵感（收藏榜） | 季节性出行话题持续上榜 |

> 采集时间：2026-10-06 08:45；通道：WebSearch + 聚合站兜底（适配器待建）。
"""
with open(os.path.join(OUTD, "小红书热榜.md"), "w", encoding="utf-8") as f:
    f.write(f"---\ntitle: 小红书热榜 · {DATE}\ndate: {DATE}\nsource: 小红书热榜\ncollectTime: {CT}\nstatus: 部分可用\n---\n\n" + body)
print("OK 小红书热榜.md")
