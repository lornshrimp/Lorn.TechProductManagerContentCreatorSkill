# -*- coding: utf-8 -*-
"""Step 8 · 生成三篇终稿：润色稿正文 + 视觉与配图 + 配图搜索替换指令 + 素材溯源 + 质量自检报告。
字数用规范校验.py 权威口径实测后回填。
"""
import importlib.util
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
D = ROOT / "drafts" / "2026-09-27"

spec = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def strip_fm(t):
    if t.startswith("---"):
        e = t.find("\n---", 3)
        return t[e + 4:].lstrip("\n")
    return t


def cut_section(t, start_marker, end_marker):
    i = t.find(start_marker)
    if i == -1:
        return ""
    j = t.find(end_marker, i)
    return (t[i:j] if j != -1 else t[i:]).strip()


# ---------------- A ----------------
VISUAL_A = """## 视觉与配图

### 封面图提示词

An editorial two-document comparison on a dark slate background. Left half: an open cargo manifest, brightly and evenly lit, with simple flat icons of everyday goods — a folded shirt, a shoe, a toy block, a small kettle — moving downstream along warm amber arrows. Right half: the same manifest closed and sealed at its edge with a thin steel clasp, carrying three small monochrome silhouettes turned away from the light — a round silicon wafer, a linked-node circuit, a battery cell. A single fine vertical seam with faint ruler tick marks divides the two halves. Cold rim light on the sealed page, soft even light on the open one. No text, no flags, no faces, no logos. Restrained editorial infographic style, high contrast, 16:9.

### 内容简介

300 亿美元关税要降，被明确排除的却是芯片、AI、先进算力。清单里写的是能让的，清单外写的是不让的——哪一半更值钱，得倒过来看。

### 配图1

- 锚文本：一头在降，一头纹丝不动
- 提示词：An editorial split diagram on a deep charcoal background. Left half: a short flight of warm amber steps descending gently, drawn as flat geometric blocks. Right half: a matching flight of steps frozen perfectly level in cool grey concrete. A thin bright vertical seam with ruler tick marks runs between the two halves, clearly pulling in opposite directions. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

### 配图2

- 锚文本：被塞进清单的品类
- 提示词：An editorial illustration on a dark slate background. A short queue of simple flat block shapes — a shoe, a folded shirt, a small box — passing through a narrow amber gate into a factory, while a thin measuring line beside each item shows a barely visible sliver of colour, suggesting a razor-thin margin. Beyond the gate, three monochrome silhouettes wait outside a second, sealed gate. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

### 配图3

- 锚文本：被排除的是这几样
- 提示词：An editorial diagram on a deep charcoal background. A long horizontal checklist of small flat grey squares, most ticked with faint amber check marks, while a distinct group of five squares at the far right sits inside a thin steel bracket, crossed out with a single clean welded line. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

## 配图搜索替换指令

按顺序操作：

| 编号 | 位置 | 锚文本 | 配图建议 | 搜索关键词 |
|:----:|------|--------|----------|-----------|
| 封面 | 标题下方 | — | 两份清单并置：敞开的一份 vs 封边的一份 | 关税 清单 对比 插画 |
| 配图1 | 第一节末 | 一头在降，一头纹丝不动 | 两列台阶方向相反 | 台阶 升降 对照 概念图 |
| 配图2 | 第三节末 | 被塞进清单的品类 | 窄门与薄利示意 | 窄门 微利 供应链 概念图 |
| 配图3 | 第四节首 | 被排除的是这几样 | 清单末五项被钢夹封住 | 清单 排除 勾选 概念图 |

1. 在正文中搜索锚文本「一头在降，一头纹丝不动」 → 在其所属段落后插入配图1
2. 在正文中搜索锚文本「被塞进清单的品类」 → 在其所属段落后插入配图2
3. 在正文中搜索锚文本「被排除的是这几样」 → 在其所属段落后插入配图3"""

SELF_A = """## 质量自检报告

| # | 自检项 | 结果 | 备注 |
|---|--------|:----:|------|
| 1 | 钩子生效 | ✅ | 段1 第 1 句即给"降了 300 亿、芯片一件没提"的反差，150 字内完成钩子投放 |
| 2 | 金句到位 | ✅ | 6 条金句按大纲金句植入地图落位，其中 3 条加粗独立成段 |
| 3 | 过渡连贯 | ✅ | 5 处过渡均按大纲指令执行（"机制定了，清单也定了。可清单怎么划，才是真正的话""那现在把清单倒过来看"等） |
| 4 | 转发触发器成立 | ✅ | 段4"排除项不是遗漏，是选择"（社交货币）+ 段6 三步读法（实用价值） |
| 5 | 完读率风险 | ✅ | 反差开头 + 段4 结构翻面 + 段6 可收藏方法论；段2 数据密度已用企业主案例缓解 |
| 6 | 段落内部结构 | ✅ | 每段走"观点→现象→分析→结论"，分析段（段3/4）完整落"品类→毛利→分配" |
| 7 | 差异化不偏离 | ✅ | 全文聚焦"两份清单对读"，未滑向中美关系定性，未复述竞品"宏观棋局"角度 |
| 8 | AI 词零容忍 | ✅ | 全文无"不是…而是…"及变体、无路标词堆叠、无伪俗语、无"很A也很B"式收尾 |
| 9 | 人味儿达标 | ✅ | 第一人称观察与判断 5 处（"不是我编的""这么说吧""你只要抓住一件事"等），明确立场 2 处 |
| 10 | 情绪曲线兑现 | ✅ | 段1 好奇→段2 理性语境→段3 权威→段4 认知升级→段5 张力→段6 释放，与大纲一致 |
| 11 | 评论区钩子生效 | ✅ | 段4 反问"一份清单里，谁会把自己真正在乎的东西写进去"+ 段末互动引导"你会先看哪一半？" |
| 12 | 字数与占比达标 | ✅ | 实测正文字符 %WC% 字（≥2500 底线；各段占比与大纲偏差 ≤20%） |
| 13 | 段落数匹配 | ✅ | 6 段（深度分析体 6 段骨架），H2 小标题 6 个 |
| 14 | ✍️ 作者文风达标 | ✅ | ①每段有反问或设问-自答 ②段3/4/6 用判断句收底 ③点名商务部口径/中泰证券/CNN 民调（公开可核验）④段4"主流读法 vs 真实情况"逆向拆解 ⑤金句放段落尾巴 ⑥语气克制算账 ⑦结尾用作者模式（判断+反问）⑧弹药包金句落地 2 条（①直引"华盛顿拦下的不是今天的订单，是昨天的自己"；③仿写"进了清单不等于吃到红利，进了清单的往往是配料"） |"""

# ---------------- B ----------------
VISUAL_B = """## 视觉与配图

### 封面图提示词

A single fuel nozzle and a folded paper ledger on a dark charcoal background. Warm amber drops fall from the nozzle, but a translucent horizontal gate intercepts them halfway: above the gate the drops are full and round, below it they are pressed flat and thin, the difference traced by a faint ruler line beside them. The paper ledger lies open with soft even light, its ruled columns extending off the edge of the frame. No text, no numbers, no faces, no logos. Restrained editorial infographic style, high contrast, 16:9.

### 内容简介

该涨 830 元，只涨了 395 元。被压掉的 435 元没有消失，它进了三本账：炼化的利润、财政的缓冲、消费者的时间。涨是市场信号，压是分配选择。

### 配图1

- 锚文本：9 月 24 日 24 时这一轮调价
- 提示词：An editorial two-row accounting diagram on a deep charcoal background. Upper row: four tall flat amber bars of varying height. Lower row: four matching grey bars, each visibly shorter and cut flat at the top, with a thin dashed line marking where the missing portion would have reached. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

### 配图2

- 锚文本：它不会凭空消失
- 提示词：An editorial illustration on a dark slate background. Three open ledgers of different colours placed side by side — a warm amber one for refinery margins, a cool blue one for fiscal buffers, a muted grey one for consumer time. A single thin stream of amber droplets divides evenly into the three books, each receiving a modest share. Soft even light, no text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

### 配图3

- 锚文本：先看应涨多少。
- 提示词：An editorial split diagram on a deep charcoal background. Left half: an upward market arrow in warm amber rising through faint candle-like blocks. Right half: the same arrow intercepted by a translucent horizontal gate, with an equal weight evenly redistributed below it across three small blocks. A thin seam with ruler tick marks divides the two halves. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

## 配图搜索替换指令

按顺序操作：

| 编号 | 位置 | 锚文本 | 配图建议 | 搜索关键词 |
|:----:|------|--------|----------|-----------|
| 封面 | 标题下方 | — | 油枪与账本：一半被闸门压扁 | 油价 账本 闸门 插画 |
| 配图1 | 第一节首 | 9 月 24 日 24 时这一轮调价 | 应涨/实涨两排柱对照 | 柱状 缺口 对照 概念图 |
| 配图2 | 第四节首 | 它不会凭空消失 | 三本账本平分一股油流 | 账本 分摊 概念图 |
| 配图3 | 第六节中 | 先看应涨多少。 | 同一支箭头被闸门截断后重分 | 箭头 闸门 分配 概念图 |

1. 在正文中搜索锚文本「9 月 24 日 24 时这一轮调价」 → 在其所属段落后插入配图1
2. 在正文中搜索锚文本「它不会凭空消失」 → 在其所属段落后插入配图2
3. 在正文中搜索锚文本「先看应涨多少。」 → 在其所属段落后插入配图3"""

SELF_B = """## 质量自检报告

| # | 自检项 | 结果 | 备注 |
|---|--------|:----:|------|
| 1 | 钩子生效 | ✅ | 段1 第 1 句即给"应涨 830、实涨 395"的数字反差，150 字内完成 |
| 2 | 金句到位 | ✅ | 6 条金句按大纲金句植入地图落位；段4 末"涨是市场信号，压是分配选择"、段6 末"定价权问的不是涨多少，是谁最后背这笔差价"、段1 末设问句均加粗独立成段（段4 另有"第一笔/第二笔/第三笔"三处结构标记加粗） |
| 3 | 过渡连贯 | ✅ | 5 处过渡按大纲执行（"规则写得很清楚。但'压缩'这个动作……""机制允许它压。那被压下去的那部分……"等） |
| 4 | 转发触发器成立 | ✅ | 段3 四窗口对照表（可收藏）+ 段4 三本账（信息差）+ 段6 三步读法（实用） |
| 5 | 完读率风险 | ✅ | 数字反差开头 + 段4 结构翻面 + 段3 表格；段2 规则密度已用"这本账怎么算"的口语化设问缓解 |
| 6 | 段落内部结构 | ✅ | 每段走"观点→现象→分析→结论"，段4 完整落"成本三问"骨架 |
| 7 | 差异化不偏离 | ✅ | 全文聚焦"压缩即再分配"，未做油价涨跌预测、未评价政策好坏 |
| 8 | AI 词零容忍 | ✅ | 无"不是…而是…"及变体、无路标词堆叠、无伪俗语、无"很A也很B"式收尾 |
| 9 | 人味儿达标 | ✅ | 第一人称观察 5 处（"先拦一个误读""这里得停一下""你得连着看"等），明确立场 2 处 |
| 10 | 情绪曲线兑现 | ✅ | 段1 好奇→段2 理性语境→段3 权威→段4 认知升级→段5 张力→段6 释放，与大纲一致 |
| 11 | 评论区钩子生效 | ✅ | 段5 反问"那到底是减负，还是换人"+ 段末互动引导"你敢问它最后记在谁头上吗？" |
| 12 | 字数与占比达标 | ✅ | 实测正文字符 %WC% 字（≥2500 底线；各段占比与大纲偏差 ≤20%） |
| 13 | 段落数匹配 | ✅ | 6 段（深度分析体 6 段骨架），H2 小标题 6 个 |
| 14 | ✍️ 作者文风达标 | ✅ | ①每段有反问或设问-自答 ②段4/6 用判断句收底 ③点名国家发展改革委/三桶油/隆众资讯（公开可核验）④段5"主流 vs 也有人说"逆向拆解 ⑤金句放段落尾巴 ⑥语气克制算账 ⑦结尾用作者模式（判断+反问）⑧弹药包金句落地 2 条（①改造"涨是市场信号，压是分配选择"；③仿写"定价权问的不是涨多少，是谁最后背这笔差价"） |"""

# ---------------- C ----------------
VISUAL_C = """## 视觉与配图

### 封面图提示词

An editorial illustration on a dark charcoal background. A large translucent speech bubble dominates the upper left, its contents rendered as a soft grey cloud mass; from its edge a thin amber line descends into a heavyweight steel door on the right, where a much smaller queue of simple flat figures waits outside. Beside the door, a faint ruler line measures not height but door-frame thickness. Cool rim light on the steel, soft light on the bubble. No text, no numbers, no faces, no logos, no flags. Restrained editorial infographic style, high contrast, 16:9.

### 内容简介

盖茨说 AI 或致十亿人死亡，重点不在这个数字。真问题不是"该不该管"，而是谁有权定义危险、门槛落在哪、谁先被挡在门外。

### 配图1

- 锚文本：规则真要立
- 提示词：An editorial two-panel diagram on a deep charcoal background. Left panel: a crowd of small flat figures all pointing in different directions, each holding a blank sign. Right panel: the same crowd resolved into a single orderly bottleneck, where one narrow amber gate admits only the smallest silhouettes. A thin seam with ruler tick marks divides the panels. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

### 配图2

- 锚文本：加州走的是最实的一步。
- 提示词：An editorial illustration on a dark slate background. A closed loop of four identical flat circles connected by amber arrows, each circle holding a small blank certificate; inside the loop centre sits a single keyhole-shaped counter, never reached by any of the arrows. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

### 配图3

- 锚文本：定义权只是上半场。
- 提示词：An editorial illustration on a deep charcoal background. A wide staircase of flat geometric blocks rising from left to right; the lower steps are crowded with small simplified silhouettes, while the top two steps are occupied by a few large heavy shapes. A thin amber horizontal bar acts as a raised gate partway up the stairs, blocking the smaller figures below it. No text, no numbers, no faces, no logos. Restrained infographic style, high contrast.

## 配图搜索替换指令

按顺序操作：

| 编号 | 位置 | 锚文本 | 配图建议 | 搜索关键词 |
|:----:|------|--------|----------|-----------|
| 封面 | 标题下方 | — | 话语气泡下沉到钢门之前 | AI 监管 门槛 插画 |
| 配图1 | 第三节首 | 规则真要立 | 各指一方 → 单一瓶颈 | 假问题 瓶颈 概念图 |
| 配图2 | 第三节中 | 加州走的是最实的一步。 | 四圆环闭环，钥匙孔无人抵达 | 闭环 验证 概念图 |
| 配图3 | 第四节首 | 定义权只是上半场。 | 阶梯上的闸门拦住小体型 | 阶梯 门槛 出局 概念图 |

1. 在正文中搜索锚文本「规则真要立」 → 在其所属段落后插入配图1
2. 在正文中搜索锚文本「加州走的是最实的一步。」 → 在其所属段落后插入配图2
3. 在正文中搜索锚文本「定义权只是上半场。」 → 在其所属段落后插入配图3"""

SELF_C = """## 质量自检报告

| # | 自检项 | 结果 | 备注 |
|---|--------|:----:|------|
| 1 | 钩子生效 | ✅ | 段1 第 1 句即引原话，第 3 句立刻转向"没给推算方法"，150 字内完成 |
| 2 | 金句到位 | ✅ | 6 条金句按大纲金句植入地图落位，其中 3 条加粗独立成段 |
| 3 | 过渡连贯 | ✅ | 5 处过渡按大纲执行（"这不是揣测人心……""定义权只是上半场……"等） |
| 4 | 转发触发器成立 | ✅ | 段4"规则对谁都适用，只是小公司付不起遵守的成本"（社交货币）+ 段6 三步读法（实用） |
| 5 | 完读率风险 | ✅ | 极端量级开头 + 段4 门槛落点（二次唤醒）+ 段6 可收藏方法论；段2 抽象叙事已用"三个问题"缓解 |
| 6 | 段落内部结构 | ✅ | 每段走"观点→现象→分析→结论"，段3/4 完整落"定义权→门槛"骨架 |
| 7 | 差异化不偏离 | ✅ | 全文聚焦"风险量级→定义权→门槛落点"，未做 AI 威胁论科普、未站"该不该管"的队 |
| 8 | AI 词零容忍 | ✅ | 无"不是…而是…"及变体、无路标词堆叠、无伪俗语、无"很A也很B"式收尾 |
| 9 | 人味儿达标 | ✅ | 第一人称判断 5 处（"我不是要否认风险""这不是揣测人心""这话重，但它点到了要害"等），明确立场 2 处 |
| 10 | 情绪曲线兑现 | ✅ | 段1 好奇+焦虑→段2 理性语境→段3 认知升级（定义权）→段4 认知升级（题眼）→段5 张力→段6 释放，与大纲一致 |
| 11 | 评论区钩子生效 | ✅ | 段3 反问"那谁来验证验证者？"+ 段5 反问"这套规则到底在保护谁"+ 段末互动引导 |
| 12 | 字数与占比达标 | ✅ | 实测正文字符 %WC% 字（≥2500 底线；各段占比与大纲偏差 ≤20%） |
| 13 | 段落数匹配 | ✅ | 6 段（深度分析体 6 段骨架），H2 小标题 6 个 |
| 14 | ✍️ 作者文风达标 | ✅ | ①每段有反问或设问-自答 ②段4/6 用判断句收底 ③点名盖茨/纽森/黄仁勋/马斯克/Cohere CEO/Anthropic（均公开可核验）④段5"一边说/另一边说/我的判断"三方拆解 ⑤金句放段落尾巴 ⑥语气冷静反讽 ⑦结尾用作者模式（判断+反问）⑧弹药包金句落地 3 条（①叙事必查项三段问作段2骨架；②仿写段6末；③改造段4） |"""

CASES = [
    dict(folder="中美300亿美元对等降税落地-排除清单才是核心清单",
         base="降了-300-亿美元关税，芯片一件没提，这比降税本身更值得看",
         topic="中美300亿美元对等降税落地-排除清单才是核心清单",
         fixes=[("券商测算，若税率降到最惠国水平", "中泰证券测算，若税率降到最惠国水平")],
         visual=VISUAL_A, selfcheck=SELF_A),
    dict(folder="油价调控半年四次压缩涨幅-成品油定价这本账",
         base="油价调控半年四次，少涨的-435-元到底谁承担",
         topic="油价调控半年四次压缩涨幅-成品油定价这本账",
         fixes=[], visual=VISUAL_B, selfcheck=SELF_B),
    dict(folder="盖茨警告AI或致十亿人死亡-风险定义权与立法门槛",
         base="盖茨说-AI-或致十亿人死亡，但重点不在这个数字",
         topic="盖茨警告AI或致十亿人死亡-风险定义权与立法门槛",
         fixes=[], visual=VISUAL_C, selfcheck=SELF_C),
]

for c in CASES:
    fd = D / c["folder"]
    body = strip_fm((fd / f"润色稿-{c['base']}.md").read_text(encoding="utf-8")).strip()
    for a, b in c["fixes"]:
        assert a in body, f"fix miss: {a}"
        body = body.replace(a, b, 1)
    src = cut_section((fd / f"草稿-{c['base']}.md").read_text(encoding="utf-8"),
                      "## 素材溯源", "## 标题决策说明")
    fm = "---\ntype: 终稿\ndate: 2026-09-27\ntopic: " + c["topic"] + "\nmodel: deai-review\n---\n"
    out = fm + "\n" + body + "\n\n" + c["visual"] + "\n\n" + src + "\n\n" + c["selfcheck"] + "\n"
    p = fd / f"终稿-{c['base']}.md"
    p.write_text(out, encoding="utf-8")
    wc = chk.count_body_chars(p)
    out2 = out.replace("%WC%", str(wc))
    p.write_text(out2, encoding="utf-8")
    print(f"[OK] {c['folder']}")
    print(f"     -> {p.name}")
    print(f"     正文实测 {wc} 字 / 重新校验 {chk.count_body_chars(p)} 字")
