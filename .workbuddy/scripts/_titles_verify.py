# -*- coding: utf-8 -*-
"""标题标点体检 + 表稿一致性核对（2026-09-14 ~ 2026-09-17）。

检查项：
1. 平台稿 frontmatter title / H1：无标点长串（≥12 字零标点）、强疑问句丢问号
2. 标题方案「平台适配」表：同样的标点体检 + 字数区间
3. 一致性：标题方案首选标题 == 对应平台稿 frontmatter title
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "drafts"
OUT = ROOT / ".workbuddy" / "_标题体检_复核.txt"

PUNCT = set("，。、：；？！…—·《》〈〉「」『』（）【】“”‘’\"'-–~!?,:;()[]{}<>")
QWORDS = ("为什么", "怎么", "如何", "哪", "谁", "什么", "吗", "呢", "多少", "是否")
LIMITS = {"知乎": (15, 35), "微信": (15, 25), "公众号": (15, 25), "微信公众号": (15, 25),
          "头条": (18, 25), "百家号": (20, 30), "CSDN": (1, 60)}

PREFIX = {"知乎-": "知乎", "微信-": "微信", "公众号-": "微信公众号", "百家号-": "百家号",
          "头条-": "头条", "CSDN-": "CSDN", "小红书-": "小红书", "视频号-": "视频号"}


def cc(s):
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", s))


def punct_issues(t):
    out = []
    n = cc(t)
    if n >= 12 and not any(ch in PUNCT for ch in t):
        out.append("无标点长串")
    if any(q in t for q in QWORDS) and "？" not in t and "?" not in t:
        # 仅当标题以疑问收尾/开头或含明确疑问焦点时判为丢问号
        if re.search(r"(吗|呢)([\s」』”\"']*)$", t) or re.match(r"^(为什么|怎么|如何)", t) \
                or re.search(r"(是什么|怎么算|怎么念|归谁|去哪|为什么|谁在|谁为|多少)", t):
            out.append("疑问句无问号")
    return out, n


buf = []
tot_plat = tot_tbl = 0
bad_plat = bad_tbl = 0
mis = []

for day in ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17"]:
    dd = DRAFTS / day
    if not dd.exists():
        continue
    buf.append(f"\n===== {day} =====")
    for tdir in sorted(d for d in dd.iterdir() if d.is_dir()):
        # ---- 平台稿 ----
        tbl = {}
        src = tdir / "标题方案.md"
        if src.exists():
            text = src.read_text(encoding="utf-8")
            m = re.search(r"^#{2,4}\s*.*平台适配.*$", text, re.MULTILINE)
            if m:
                seg = text[m.end():]
                nx = re.search(r"^##(?!#)\s+", seg, re.MULTILINE)
                seg = seg[:nx.start()] if nx else seg
                for ln in seg.split("\n"):
                    if not ln.strip().startswith("|"):
                        continue
                    cells = [c.strip() for c in ln.strip("|").split("|")]
                    if len(cells) >= 2 and cells[0] in ("知乎", "微信", "公众号", "微信公众号",
                                                        "头条", "百家号", "CSDN", "小红书", "视频号"):
                        tbl[cells[0]] = cells[1]
        for pf in sorted(tdir.glob("*.md")):
            pname = None
            for pre, p in PREFIX.items():
                if pf.name.startswith(pre):
                    pname = p
                    break
            if not pname or pf.name == "标题方案.md":
                continue
            txt = pf.read_text(encoding="utf-8")
            mm = re.search(r"^title:\s*(.+)$", txt, re.MULTILINE)
            t = mm.group(1).strip() if mm else ""
            iss, n = punct_issues(t)
            tot_plat += 1
            pl = LIMITS.get("微信公众号" if pname in ("微信", "微信公众号") else pname)
            if pl is None:
                continue
            lo, hi = pl
            flag = ""
            if n < lo or n > hi:
                flag = f" ⚠️字数{n}超出{lo}-{hi}"
            if iss:
                bad_plat += 1
                buf.append(f"  ❌ [平台稿][{pname}] {t}  ← {'/'.join(iss)}{flag}")
            elif flag:
                buf.append(f"  ⚠️ [平台稿][{pname}] {t}{flag}")
            # 与标题方案表比对（微信/公众号/微信公众号 视为同一平台）
            def norm(p):
                return "微信" if p in ("微信", "公众号", "微信公众号") else p
            key = [k for k in tbl if norm(k) == norm(pname)]
            if key:
                tv = tbl[key[0]]
                tot_tbl += 1
                if tv != t:
                    mis.append(f"{day}/{tdir.name} [{key[0]}] 表「{tv}」≠ 稿「{t}」")
                    bad_tbl += 1

buf.append("\n===== 汇总 =====")
buf.append(f"平台稿标题数：{tot_plat}；标点/字数问题：{bad_plat}")
buf.append(f"表稿标题比对：{tot_tbl} 组；不一致：{bad_tbl}")
buf.append("\n不一致明细：" if mis else "\n不一致明细：无")
buf += mis or []
OUT.write_text("\n".join(buf), encoding="utf-8")
print("OK plat=", tot_plat, "bad=", bad_plat, "mis=", bad_tbl)
