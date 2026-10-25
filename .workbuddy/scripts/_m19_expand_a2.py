# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-19/住建部房地产进入存量时代-现房销售改的是哪本账/润色稿-现房销售改的是哪本账.md")
t = p.read_text(encoding="utf-8")
INS = [
('这就是"存量时代"这四个字在会计上的真实含义。',
 '这就是"存量时代"这四个字在会计上的真实含义。\n\n说白一点：过去是拿购房人的钱去做开发，现在是拿房企自己的钱去证明能力。钱从谁兜里先出，就是这两种模式最本质的差别。'),
('成本没消失，只是在链条上换了个位置。',
 '成本没消失，只是在链条上换了个位置。\n\n链上每一环的账期，最后都得有人垫。垫到哪一环垫不动了，哪一环就先出事——这也是为什么这套改革要先配套"新老划断"，把存量项目留在旧规则里。'),
]
n = 0
for a, r in INS:
    if a in t:
        t = t.replace(a, r, 1); n += 1
    else:
        print("MISS:", a[:20])
p.write_text(t, encoding="utf-8")
print("inserted:", n)
