# -*- coding: utf-8 -*-
"""逐单元格打印三选题标题方案「平台适配」表的字数/标点判定，定位所有不达标单元"""
import re, sys, importlib.util
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
sys.modules["chk"] = chk
spec.loader.exec_module(chk)

drafts = ROOT / "drafts/2026-09-22"
out = []
for d in sorted(drafts.iterdir()):
    if not d.is_dir():
        continue
    f = d / "标题方案.md"
    if not f.exists():
        continue
    text = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^#{2,4}\s*.*平台适配.*$", text, re.MULTILINE)
    start = m.end()
    nxt = re.search(r"^##(?!#)\s+", text[start:], re.MULTILINE)
    seg = text[start: start + nxt.start()] if nxt else text[start:]
    out.append(f"########## {d.name} ##########")
    for ln in [x.strip() for x in seg.split("\n") if x.strip()]:
        if not ln.startswith("|") or re.fullmatch(r"\|[\s:\-|]+\|", ln):
            continue
        cells = [c.strip().strip("*`").strip() for c in ln.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("平台", "序号", "排名", "平台名称") or not cells[0]:
            continue
        plat = cells[0]
        plen = None
        pk = None
        for k, (lo, hi) in chk.PLATFORM_TITLE_LEN.items():
            if k in plat or plat in k:
                plen = (lo, hi); pk = k; break
        for name, cell in (("首选", cells[1]), ("备选", cells[2] if len(cells) > 2 else "")):
            if not cell:
                continue
            t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
            t = t.strip().strip("*`\"'“”‘’「」『』").strip()
            n = len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", t))
            punct = any(c in chk.TITLE_PUNCT_CHARS for c in t)
            qflag = (not punct or ("？" not in t and "?" not in t)) and any(
                re.search(p, t) for p in chk.TITLE_QWORD_PATTERNS)
            flag = ""
            if plen:
                lo, hi = plen
                if n > hi:
                    flag += f" >>>超上限({hi})"
                elif n < lo:
                    flag += f" >>>过短(<{lo})"
            if not punct and n >= chk.TITLE_PUNCT_STRICT_LEN:
                flag += " >>>零标点❌"
            elif not punct and n >= chk.TITLE_PUNCT_WARN_LEN:
                flag += " >>>零标点⚠️"
            if qflag:
                flag += " >>>设问缺问号⚠️"
            out.append(f"[{plat}][{name}] {n}字 区间{plen} | {t}{flag}")
    out.append("")

(ROOT / ".workbuddy/_titlecells_0922.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
