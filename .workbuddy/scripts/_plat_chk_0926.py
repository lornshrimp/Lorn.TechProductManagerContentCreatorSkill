# -*- coding: utf-8 -*-
import re, io
from pathlib import Path

BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-26")
TRUNC = ["## 素材溯源", "## 质量自检报告", "## 标题决策说明", "## 配图搜索替换指令",
         "# 附属内容区域", "## 配图详情", "## 视觉与配图", "[封面图提示词]", "[内容简介]"]
out = io.StringIO()

def split_fm(t):
    if t.startswith("---"):
        p = t.split("---", 2)
        if len(p) >= 3:
            return p[1], p[2]
    return "", t

def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))

def body_only(t):
    fm, b = split_fm(t)
    for m in TRUNC:
        i = b.find(m)
        if i != -1:
            b = b[:i]
    return b.strip()

PLAT = ["知乎-", "微信-", "百家号-", "CSDN-", "头条-"]

for d in sorted([p for p in BASE.iterdir() if p.is_dir()]):
    out.write("=" * 78 + "\n" + f"### {d.name}\n")
    for f in sorted(d.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        is_plat = any(f.name.startswith(x) for x in PLAT)
        if not is_plat:
            continue
        fm, b = split_fm(raw)
        body = body_only(raw)
        out.write("-" * 70 + "\n")
        out.write(f"  [{f.name}]\n")
        fmd = {}
        for line in fm.strip().splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                fmd[k.strip()] = v.strip()
        out.write(f"    frontmatter keys: {list(fmd.keys())}\n")
        out.write(f"    title: {fmd.get('title','(缺)')}\n")
        out.write(f"    正文中文字符: {cn(body)}\n")
        out.write(f"    总中文字符(含附属): {cn(raw)}\n")
        h2 = len(re.findall(r"^## ", body, re.M))
        h3 = len(re.findall(r"^### ", body, re.M))
        out.write(f"    H2(正文区): {h2} / H3: {h3} / H2全部: {len(re.findall(r'^## ', raw, re.M))}\n")
        out.write(f"    互动引导独立小标题: {bool(re.search(r'^#{1,3}\s*(读者互动|互动引导|互动话题)\s*$', raw, re.M))}\n")
        paras = [x for x in body.split("\n\n") if x.strip() and not x.strip().startswith("#")]
        over = [cn(x) for x in paras if cn(x) > 300]
        out.write(f"    段数: {len(paras)} / >300字段: {over if over else '无'} / 最长段: {max([cn(x) for x in paras]) if paras else 0}\n")
        # 配图
        figs = re.findall(r"^### \[配图(\d+)\]", raw, re.M)
        out.write(f"    配图张数: {len(figs)}\n")
        # anchors
        anchors = re.findall(r"锚文本\"([^\"]+)\"", raw)
        anchors += re.findall(r"锚文本：([^\n]+)", raw)
        uniq = []
        for a in anchors:
            a = a.strip().strip('"')
            if a and a not in uniq:
                uniq.append(a)
        for a in uniq:
            cnt = body.count(a)
            out.write(f"    anchor 命中: {cnt}  「{a}」\n")
        out.write(f"    含封面图提示词: {'封面图提示词' in raw} / 内容简介: {'内容简介' in raw}\n")
        m = re.search(r"封面图提示词\]?\s*\n+(.+?)(?=\n\[|\n###|\n##|\Z)", raw, re.S)
        if m:
            ratio = "16:9" if "16:9" in m.group(1) else ("3:2" if "3:2" in m.group(1) else "?")
            out.write(f"    封面比例: {ratio}\n")
        # 平台专项
        checks = []
        if "Clickable Link" in raw or "去回答该问题" in raw: checks.append("知乎ClickableLink")
        if "source_label" in fm: checks.append("source_label")
        if "source_url" in fm: checks.append("source_url")
        if any(k in raw for k in ["在看", "留言", "关注"]): checks.append("互动三词")
        if "SEO" in raw: checks.append("SEO段")
        if "核心" in raw: checks.append("核心答案")
        out.write(f"    专项要素: {checks}\n")

Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_plat_chk_0926_out.txt").write_text(out.getvalue(), encoding="utf-8")
print("DONE")
