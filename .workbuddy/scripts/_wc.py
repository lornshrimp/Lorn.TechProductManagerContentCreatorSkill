# -*- coding: utf-8 -*-
import re, sys, os, glob

BASE = r"d:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"

MARKERS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检", "## 封面图", "## 内容简介",
    "## 互动引导", "## SEO 关键词", "## 配图详情", "# 附属内容区域",
    "## 配图搜索替换指令", "## 参考来源", "## 润色说明", "## 发布建议",
]

def strip_fm(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 3)
            if nl != -1:
                return text[nl + 1:]
    return text

def body(text):
    t = strip_fm(text)
    cut = len(t)
    for m in MARKERS:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]

def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))

def total_lines_no_fm(text):
    return len(strip_fm(text).splitlines())

def h2count(text):
    return len(re.findall(r"(?m)^##\s", body(text)))

def max_para(text):
    b = body(text)
    paras = [p.strip() for p in re.split(r"\n\s*\n", b) if p.strip()]
    paras = [p for p in paras if not p.startswith("#") and not p.startswith("|") and not p.startswith(">") and not p.startswith("```")]
    mx = 0
    for p in paras:
        mx = max(mx, cn(p))
    return mx

targets = sys.argv[1:] if len(sys.argv) > 1 else [r"drafts\2026-09-13\车市价格带断裂-购车能力退出"]
for t in targets:
    p = t if os.path.isabs(t) else os.path.join(BASE, t)
    files = []
    if os.path.isdir(p):
        files = sorted(glob.glob(os.path.join(p, "*.md")))
    else:
        files = [p]
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                c = fh.read()
        except Exception as e:
            print("ERR", f, e); continue
        print("%-58s | body_cn=%5d | h2=%2d | maxpara=%4d | lines=%4d" % (
            os.path.basename(f), cn(body(c)), h2count(c), max_para(c), total_lines_no_fm(c)))
