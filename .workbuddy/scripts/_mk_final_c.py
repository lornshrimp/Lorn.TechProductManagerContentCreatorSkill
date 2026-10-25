from pathlib import Path
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16/8月国民经济数据剪刀差-生产热与消费冷的对账")
src = (d/"润色稿-生产热与消费冷的对账.md").read_text(encoding="utf-8")
old_fm = """---
type: 润色稿
date: 2026-09-16
topic: 8 月国民经济数据——社零 +1.1% 与规上工业 +5.2% 的剪刀差
genre: 深度分析体
model: deai-polish
---"""
new_fm = """---
type: 终稿
date: 2026-09-16
topic: 8 月国民经济数据——社零 +1.1% 与规上工业 +5.2% 的剪刀差
genre: 深度分析体
model: deai-review
审核结论: 通过
---"""
assert src.startswith(old_fm), src[:200]
out = new_fm + src[len(old_fm):]
(d/"终稿-生产热与消费冷的对账.md").write_text(out, encoding="utf-8")
print("ok")
