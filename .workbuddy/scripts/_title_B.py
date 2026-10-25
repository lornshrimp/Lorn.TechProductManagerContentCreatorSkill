# -*- coding: utf-8 -*-
import re, difflib
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")

def n(t):
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", t))

titles = {
    "母稿#1": "限量这本账：欧盟要中国「自愿」限出口，限的是车，还是价？",
    "知乎#7": "欧盟要中国「自愿限制」汽车出口，这意味着什么？",
    "微信#3": "关税的钱进财政，「自愿限制」的钱进企业",
    "头条#6": "两年十倍：3,800 辆到 50,000 辆之后，欧盟动了插混",
    "百家号#12": "欧盟要 15% 的份额上限，中国品牌现在超过三分之一",
    "CSDN#13": "欧盟「自愿限制」汽车出口拆解：数量账、价格账、利润账",
}
ranges = {"知乎#7": (15,35), "微信#3": (15,25), "头条#6": (18,25), "百家号#12": (20,30), "CSDN#13": (1,60), "母稿#1": (0,99)}

out = ["=== 字数（[汉字/A-Za-z0-9] 计）==="]
for k, v in titles.items():
    r = ranges[k]
    ok = "OK" if r[0] <= n(v) <= r[1] else "OVER"
    out.append(f"{k}: {n(v)} 字  区间{r[0]}-{r[1]}  [{ok}]")
    out.append(f"   标点数={len(re.findall(r'[，。：；？！、「」,.!?]', v))}")

out.append("")
out.append("=== 平台两两相似度 + 与母稿 ===")
keys = [k for k in titles if k != "母稿#1"]
mx = 0
for i in range(len(keys)):
    for j in range(i+1, len(keys)):
        a, b = keys[i], keys[j]
        rt = difflib.SequenceMatcher(None, titles[a], titles[b], autojunk=False).ratio()
        mx = max(mx, rt)
        out.append(f"{a} vs {b}: {rt:.4f}  [{'OK' if rt<0.85 else 'XX'}]")
for k in keys:
    rt = difflib.SequenceMatcher(None, titles["母稿#1"], titles[k], autojunk=False).ratio()
    mx = max(mx, rt)
    out.append(f"母稿#1 vs {k}: {rt:.4f}  [{'OK' if rt<0.85 else 'XX'}]")
out.append(f"最大相似度 = {mx:.4f}")

Path(str(ROOT/".workbuddy"/"_title_B_out.txt")).write_text("\n".join(out), encoding="utf-8")
print("done")
