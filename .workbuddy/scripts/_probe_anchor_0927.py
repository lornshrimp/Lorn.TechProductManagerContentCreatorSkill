# -*- coding: utf-8 -*-
"""探针：对 09-26 样板终稿跑锚文本门禁（确认历史通过形态），
并测试今日候选锚文本的命中/唯一/段首三项。"""
import importlib.util
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

f26 = ROOT / "drafts/2026-09-26/全国牛肉批发均价涨至一公斤71元-创两年新高/终稿-牛肉创两年新高-CPI-只有-0-8-两个数为什么都是真的.md"
print("=== 09-26 样板锚文本门禁 ===")
for x in chk.check_anchor_quality(f26):
    print(x)
t = f26.read_text(encoding="utf-8")
for a in ["一公斤 71 元和你钱包里那只篮子"]:
    i = t.find(a)
    print(repr(a), "count=", t.count(a), "前文=", repr(t[max(0, i - 30):i]) if i != -1 else "N/A")

D = ROOT / "drafts/2026-09-27"
cand = {
    "A": ("中美300亿美元对等降税落地-排除清单才是核心清单/润色稿-降了-300-亿美元关税，芯片一件没提，这比降税本身更值得看.md",
          ["一头在降，一头纹丝不动", "被塞进清单的品类", "被排除的是这几样", "清单不长。",
           "那现在把清单倒过来看。", "这份清单最值钱的信息不在里面", "能降的，都是对方不在乎的"]),
    "B": ("油价调控半年四次压缩涨幅-成品油定价这本账/润色稿-油价调控半年四次，少涨的-435-元到底谁承担.md",
          ["少涨的那 435 元", "有个前提得先摆下。", "它不会凭空消失。", "答案在机制第七条。",
           "涨是市场信号，压是分配选择。", "被压掉的那部分，记在三本账上", "这本账怎么算"]),
    "C": ("盖茨警告AI或致十亿人死亡-风险定义权与立法门槛/润色稿-盖茨说-AI-或致十亿人死亡，但重点不在这个数字.md",
          ["那谁来验证验证者？", "规则真要立", "定义权只是上半场。", "到这儿，几种声音得摆一起。",
           "立出技术上可执行、可核查的规则", "说到底，读一条 AI 监管新闻"]),
}
for tag, (rel, anchors) in cand.items():
    t = (D / rel).read_text(encoding="utf-8")
    print(f"\n=== {tag} 候选锚文本 ===")
    for a in anchors:
        cnt = t.count(a)
        i = t.find(a)
        head = t[max(0, i - 12):i].replace("\n", "\\n") if i != -1 else ""
        print(f"  [{cnt}] {a!r} 前文={head!r}")
