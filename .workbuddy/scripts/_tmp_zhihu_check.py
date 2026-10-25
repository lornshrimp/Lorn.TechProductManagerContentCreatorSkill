# -*- coding: utf-8 -*-
import sys, io, re
from pathlib import Path
_out = open(str(Path(__file__).resolve().parent.parent.parent / "_zhihu_check_out.txt"), "w", encoding="utf-8")
sys.stdout = _out
sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util
spec = importlib.util.spec_from_file_location("chk", str(Path(__file__).resolve().parent / "规范校验.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

d = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-09-13\车市价格带断裂-购车能力退出")
z = d / "知乎-车市均价连涨为什么5万元以下的车反而没人造了.md"
files = {
    "知乎": z,
    "头条": d / "头条-少了220万辆的车市只剩最后一档还在涨.md",
    "百家号": d / "百家号-5万以下销量跌55%40万以上却在涨车市价格带的两端.md",
    "微信": d / "微信-均价涨了3%但不是消费升级是便宜车消失了.md",
    "终稿": d / "终稿-车市均价上升的真相是便宜车消失了.md",
}
print("知乎正文中文字符数:", m.count_body_chars(z))
texts = {}
for k, f in files.items():
    if f.exists():
        texts[k] = m.extract_body_text(f)
    else:
        print("缺失:", f.name)
names = list(texts)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = names[i], names[j]
        print(f"{a} vs {b}: {m.text_similarity(texts[a], texts[b]):.1%}")
