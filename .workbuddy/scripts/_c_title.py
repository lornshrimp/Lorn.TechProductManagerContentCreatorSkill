# -*- coding: utf-8 -*-
"""选题 C 平台标题字数 / 相似度实测"""
import re, difflib
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

titles = {
    "知乎": "7000 亿再贷款来了，央行这次动的为什么是水管？",
    "微信": "支持比例从 60% 到 100%：这行数字比降息更狠",
    "头条": "央行四箭齐发：7000 亿不是加量，是换水管",
    "百家号": "7000 亿定向六张网：清单内外就是一本分配账",
    "CSDN": "三张表读懂本轮央行工具：价格、比例、清单",
    "母稿": "7000 亿不是放水，是定向：央行这次动的是水管",
}
backups = {
    "知乎": "7000 亿砸向六张网，谁在清单里、谁在清单外？",
    "微信": "PSL 从 3 万亿缩到 6308 亿：这次是降价扩围",
    "头条": "六张网 7 万亿，7000 亿再贷款浇得到哪一张？",
    "百家号": "定价权与投向权分给了两只手：读懂结构性工具",
    "CSDN": "央行这次动的是水管，不是水量",
}
LIMITS = {"知乎": (15, 35), "微信": (15, 25), "头条": (18, 25), "百家号": (20, 30), "CSDN": (1, 60)}


def cnt(s):
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", s))


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


out = []
out.append("== 首选标题字数 ==")
for k, v in titles.items():
    if k == "母稿":
        continue
    n = cnt(v)
    lo, hi = LIMITS[k]
    ok = "OK" if lo <= n <= hi else "FAIL"
    punct = bool(re.search(r"[，。？！：；、（）《》]", v))
    out.append(f"{k}: {n} ({lo}-{hi}) {ok} | 标点={punct} | {v}")

out.append("")
out.append("== 备选标题字数 ==")
for k, v in backups.items():
    n = cnt(v)
    lo, hi = LIMITS[k]
    ok = "OK" if lo <= n <= hi else "FAIL"
    punct = bool(re.search(r"[，。？！：；、（）《》]", v))
    out.append(f"{k}: {n} ({lo}-{hi}) {ok} | 标点={punct} | {v}")

out.append("")
out.append("== 平台两两相似度 ==")
pk = ["知乎", "微信", "头条", "百家号", "CSDN"]
mx = 0.0
mxp = ""
for i in range(len(pk)):
    for j in range(i + 1, len(pk)):
        s = sim(titles[pk[i]], titles[pk[j]])
        if s > mx:
            mx, mxp = s, f"{pk[i]} vs {pk[j]}"
        out.append(f"{pk[i]} vs {pk[j]}: {s:.4f} {'OK' if s < 0.85 else 'FAIL'}")

out.append("")
out.append("== 母稿 vs 平台 ==")
for k in pk:
    s = sim(titles["母稿"], titles[k])
    if s > mx:
        mx, mxp = s, f"母稿 vs {k}"
    out.append(f"母稿 vs {k}: {s:.4f} {'OK' if s < 0.85 else 'FAIL'}")

out.append("")
out.append(f"最大相似度: {mx:.4f} @ {mxp}  ->  {'OK' if mx < 0.85 else 'FAIL'}")

dst = BASE / ".workbuddy" / "_c_title.txt"
dst.write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
