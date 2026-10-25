# -*- coding: utf-8 -*-
"""规范校验·PM 方法论门禁 正反例自测（2026-10-20）

目的：证明新增门禁「不达标样例确实能报 ❌」，而不只是"跑通不报错"。
同时验证「只对 --date 当日生效」这一隔离设计真的生效。
结果写入 _selftest_pm_result.txt（避免控制台编码问题）。
"""
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

TODAY = "2026-10-20"
OTHER = "2026-10-19"

FULL_BOARD = """## 二（补）、产品经理拆解板（PM Board）

### 4.0 方法论骨架
主用「成本三问」，通用框架补位用「约束三角」。

### 4.1 五问定位

| # | 问题 | 本次答案 |
|:--:|------|------|
| Q1 | 谁的什么问题 | 灵活就业者今年要续上缴费 |
| Q2 | 现在这条路怎么走 | 借钱—缴费—退休扣划 |
| Q3 | 卡在哪一步 | 扣划比例与基数错配 |
| Q4 | 谁在为这一步付费 | 借款人的未来养老金 |
| Q5 | 换个设计会怎样 | 降基数，但基金现金流当期更紧 |

### 4.2 交付物一：现状链条
银行放款 → 社保入账 → 退休扣划 65%-80%。
钱流：银行出钱、养老金还款。责任流：借款人兜底。权力流：规则由地方定。

### 4.3 交付物二：度量视角
被「缴费率」衡量，由地方社保局定义，会被生产出「为达标而借」的行为。

### 4.4 交付物三：一组真实权衡
约束 A 基金当期现金流；约束 B 参保人终身可支配收入。成本最终放在参保人一侧。

### 4.5 交付物四：反方案 + 副作用
方案：基数下限与最低工资挂钩。解决门槛。新坏：统筹收入下降，需财政补口。代价落在财政。

### 4.6 术语预算

| 术语 | 人话解释 | 拟出现位置 |
|------|------|------|
| 缴费基数 | 按多少钱算保费 | 第四节 |
"""


def mk(name, date="2026-10-20", depth="L4", board=FULL_BOARD):
    t = f"---\ntype: 研究报告\ndate: {date}\ntopic: 测试\ndepth: {depth}\nmodel: x\n---\n\n"
    t += "## 一、研究概要\n\n内容。\n\n"
    t += board
    t += "\n## 三、素材库\n\n内容。\n"
    d = Path(tempfile.mkdtemp())
    p = d / f"{name}.md"
    p.write_text(t, encoding="utf-8")
    return p


outline_full = """---
type: 大纲
date: 2026-10-20
topic: 测试
model: x
---

## 一、标题策略

略。

## 一（补）、产品拆解映射

| 项 | 落位段落 | 具体承载 |
|---|---|---|
| 交付物一 · 现状链条 | 第 2 段 | 钱流/责任流/权力流 |
| 交付物二 · 度量视角 | 第 3 段 | 缴费率与定义方 |
| 交付物三 · 真实权衡 | 第 4 段 | 现金流 vs 可支配收入 |
| 交付物四 · 反方案+副作用 | 第 5 段 | 降基数，财政补口 |
| 主框架 | 第 3 段 | 成本三问 |
| 辅助框架 | 第 4 段 | 约束三角 |

## 二、段落骨架

略。
"""


def mk_outline(text):
    d = Path(tempfile.mkdtemp())
    p = d / "大纲.md"
    p.write_text(text, encoding="utf-8")
    return p


results = []


def case(name, issues, expect_error):
    has = bool(issues)
    ok = has == expect_error
    results.append((ok, name, "报 ❌" if has else "通过", expect_error, issues))


# ---- 研究报告门禁 ----
case("① 完整 L4 拆解板（应通过）", chk.check_pm_board(mk("a", depth="L4"), TODAY), False)
case("② 缺整个拆解板章节（应报错）", chk.check_pm_board(mk("b", board=""), TODAY), True)
case("③ L4 只写 4 节、缺术语预算与骨架（应报错）",
     chk.check_pm_board(mk("c", board=FULL_BOARD.split("### 4.4")[0]), TODAY), True)
case("④ 占位符未替换（应报错）",
     chk.check_pm_board(mk("d", board=FULL_BOARD.replace("银行放款 → 社保入账 → 退休扣划 65%-80%。",
                                                        "{环节1} → {环节2} → {环节3}")), TODAY), True)
case("⑤ 非当日报告（应静默跳过）", chk.check_pm_board(mk("e", date=OTHER), TODAY), False)
case("⑥ L1 深度豁免（应通过）", chk.check_pm_board(mk("f", depth="L1", board=""), TODAY), False)
case("⑦ L2 缺 Q3 行（应报错）",
     chk.check_pm_board(mk("g", depth="L2", board=FULL_BOARD.replace("| Q3 |", "| QX |")), TODAY), True)
case("⑧ L2 完整（应通过）", chk.check_pm_board(mk("h", depth="L2"), TODAY), False)

# ---- 大纲映射门禁 ----
case("⑨ 大纲含完整映射（应通过）", chk.check_pm_mapping(mk_outline(outline_full)), False)
case("⑩ 大纲缺映射章节（应报错）",
     chk.check_pm_mapping(mk_outline(outline_full.replace("## 一（补）、产品拆解映射", "## 一（补）、别的"))), True)
case("⑪ 大纲映射缺「反方案」行（应报错）",
     chk.check_pm_mapping(mk_outline(
         "\n".join(l for l in outline_full.split("\n") if "交付物四" not in l))), True)
case("⑫ 大纲映射留占位符（应报错）",
     chk.check_pm_mapping(mk_outline(outline_full.replace("钱流/责任流/权力流", "{链条标了哪几环}"))), True)

lines = ["PM 方法论门禁 · 正反例自测结果", "=" * 52]
n_fail = 0
for ok, name, got, expect, issues in results:
    mark = "PASS" if ok else "FAIL"
    if not ok:
        n_fail += 1
    lines.append(f"[{mark}] {name} → 实测{got}")
    for i in issues:
        lines.append("        " + i.strip())
lines.append("=" * 52)
lines.append(f"共 {len(results)} 例，通过 {len(results)-n_fail}，失败 {n_fail}")
(ROOT / ".workbuddy/scripts/_selftest_pm_result.txt").write_text("\n".join(lines), encoding="utf-8")
print(f"done fail={n_fail}")
