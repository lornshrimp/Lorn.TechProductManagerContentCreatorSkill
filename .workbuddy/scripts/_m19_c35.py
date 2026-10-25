# -*- coding: utf-8 -*-
"""C 题纠错后：草稿/润色稿/终稿字数、差异率、最长段落、H2 计数。"""
import difflib
import importlib.util
import re
from pathlib import Path

BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", BASE / ".workbuddy" / "scripts" / "规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)
count_body_chars = chk.count_body_chars

D = BASE / "drafts" / "2026-09-19" / "8月16-24岁失业率18.9%-统计口径这本账"
files = {
    "草稿": D / "草稿-统计口径这本账.md",
    "润色稿": D / "润色稿-统计口径这本账.md",
    "终稿": D / "终稿-统计口径这本账.md",
}
for k, f in files.items():
    print(f"{k}: {count_body_chars(f)} 字")

# 草稿 × 润色稿 差异率（去空白）
def txt(p):
    t = p.read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        i = t.find("\n---", 3)
        t = t[i + 4:]
    t = re.sub(r"^#\s+.*$", "", t, flags=re.M)
    for m in ["## 素材溯源", "## 质量自检报告", "## 视觉与配图", "## 配图搜索替换指令"]:
        idx = t.find(m)
        if idx != -1:
            t = t[:idx]
    return re.sub(r"\s+", "", t)

a, b = txt(files["草稿"]), txt(files["润色稿"])
r = difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()
print(f"草稿 × 润色稿 相似度={r:.2%} 差异率={(1-r)*100:.2f}%")

# 最长段落 + H2 计数
for k, f in files.items():
    t = f.read_text(encoding="utf-8", errors="ignore")
    h2 = re.findall(r"^##\s+", t, flags=re.M)
    paras = [re.sub(r"\s+", "", p) for p in t.split("\n\n")]
    # 只统计正文段落（排除标题行）
    body = [p for p in paras if p and not p.startswith("#")]
    longest = max((len(p) for p in body), default=0)
    print(f"{k}: H2={len(h2)} 最长段={longest} 字")

# 头条最长段落
tt = D / "头条-统计口径这本账.md"
t = tt.read_text(encoding="utf-8", errors="ignore")
for m in ["## 视觉与配图"]:
    idx = t.find(m)
    if idx != -1:
        t = t[:idx]
paras = [re.sub(r"\s+", "", p) for p in t.split("\n\n")]
body = [p for p in paras if p and not p.startswith("#")]
print(f"头条: H2={len(re.findall(r'^##\\s+', tt.read_text(encoding='utf-8', errors='ignore'), flags=re.M))} 最长段={max((len(p) for p in body), default=0)} 字")
