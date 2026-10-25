# -*- coding: utf-8 -*-
"""验证 check_platform_title_punctuation 生效：已知不达标样例必须报 ❌。"""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("vfy", ROOT / ".workbuddy" / "scripts" / "规范校验.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BAD = """---
date: 2026-09-17
---

## 三、平台适配

| 平台 | 首选标题 | 备选标题 | 来源 |
|---|---|---|---|
| 知乎 | 1050 亿美元的对面站着什么这笔账谁在付 | 首富的 1050 亿是估值那 70 个人的失业是真的 | #1 / #5 |
| 公众号 | 他成了亚洲首富那 70 个人的工资单呢 | 1050 亿美元对面站着谁的工资单 | #5 / #1 |
| 头条 | 亚洲首富 1050 亿美元对面是 70 个人的工资单 | 用 AI 裁掉 70 多人之后为什么利润就上去了 | #1 / #3 |
| 百家号 | 张一鸣成亚洲首富 1050 亿美元 AI 造富与裁员的账怎么算 | 亚洲首富换人了 1050 亿美元背后的产业与分配账 | #4 / #4 |
| CSDN | 从 1050 亿美元到 16.7% 净利率 AI 造富的成本归属拆解 | 未上市的 1050 亿市场预支还是欠条 | #2 / #6 |
"""

GOOD = """---
date: 2026-09-17
---

## 三、平台适配

| 平台 | 首选标题 | 备选标题 | 来源 |
|---|---|---|---|
| 知乎 | 1050 亿美元的对面，站着什么？这笔账谁在付 | 首富的 1050 亿是估值，那 70 个人的失业是真的 | #1 / #5 |
| 公众号 | 他成了亚洲首富，那 70 个人的工资单呢？ | 1050 亿美元的对面，站着谁的工资单？ | #5 / #1 |
| 头条 | 亚洲首富 1050 亿美元，对面是 70 个人的工资单 | 用 AI 裁掉 70 多人之后，为什么利润就上去了？ | #1 / #3 |
| 百家号 | 张一鸣成亚洲首富，1050 亿美元 AI 造富与裁员的账怎么算？ | 亚洲首富换人了，1050 亿美元背后的产业与分配账 | #4 / #4 |
| CSDN | 从 1050 亿美元到 16.7% 净利率，AI 造富的成本归属拆解 | 未上市的 1050 亿：市场预支，还是欠条 | #2 / #6 |
"""

tmp = ROOT / ".workbuddy" / "_punct_test.md"
out = []
for name, body in (("已知不达标样例", BAD), ("修复后样例", GOOD)):
    tmp.write_text(body, encoding="utf-8")
    iss = mod.check_platform_title_punctuation(tmp)
    out.append(f"\n===== {name}：{len(iss)} 项 =====")
    out += iss or ["  无（通过）"]
tmp.unlink()

errs = sum(1 for i in out if "❌" in i)
print("\n".join(out).encode("ascii", "replace").decode("ascii"))
(ROOT / ".workbuddy" / "_标点门禁自测.txt").write_text("\n".join(out), encoding="utf-8")
print("ERR_COUNT=", errs)
