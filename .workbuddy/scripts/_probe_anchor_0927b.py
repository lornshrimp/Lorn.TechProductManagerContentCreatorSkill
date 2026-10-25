# -*- coding: utf-8 -*-
"""探针2：为三篇选定最终锚文本（正文唯一 + 段首/小标题）。"""
import re
import importlib.util
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

D = ROOT / "drafts/2026-09-27"
cand = {
    "A": ("中美300亿美元对等降税落地-排除清单才是核心清单/润色稿-降了-300-亿美元关税，芯片一件没提，这比降税本身更值得看.md",
          ["一头在降，一头纹丝不动", "被塞进清单的品类", "被排除的是这几样",
           "清单不长。", "那现在把清单倒过来看。"]),
    "B": ("油价调控半年四次压缩涨幅-成品油定价这本账/润色稿-油价调控半年四次，少涨的-435-元到底谁承担.md",
          ["答案在机制第七条。", "它不会凭空消失。", "读一次油价调控，顺序该是这样。",
           "这本账怎么算", "被压掉的那部分，记在三本账上", "先看应涨多少。"]),
    "C": ("盖茨警告AI或致十亿人死亡-风险定义权与立法门槛/润色稿-盖茨说-AI-或致十亿人死亡，但重点不在这个数字.md",
          ["规则真要立", "定义权只是上半场。", "到这儿，几种声音得摆一起。",
           "眼下的局面，是四方力量在对撞。", "说到底，读一条 AI 监管新闻"]),
}
for tag, (rel, anchors) in cand.items():
    raw = (D / rel).read_text(encoding="utf-8")
    # 模拟门禁 body：去 frontmatter/H1，截断于附属区（本文无附属区 → 全文）
    body = raw
    if body.startswith("---"):
        e = body.find("\n---", 3)
        body = body[e + 4:]
    body = re.sub(r"^#\s+.*$", "", body, flags=re.MULTILINE)
    body = re.sub(r"^##\s+.*$", "", body, flags=re.MULTILINE)
    print(f"\n=== {tag} ===")
    for a in anchors:
        cnt = body.count(a)
        i = body.find(a)
        head = body[max(0, i - 8):i].replace("\n", "\\n") if i != -1 else "N/A"
        start_ok = (i != -1 and body[:i].rstrip("\n").endswith(("。", "？", "！", "—", "：", '"')))
        print(f"  [{cnt}] {a!r}  前文尾={head!r} 段首={'✅' if start_ok else '?'}")
