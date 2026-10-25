# -*- coding: utf-8 -*-
import io, sys, re, importlib.util, difflib
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def stats(p):
    p = Path(p)
    c = p.read_text(encoding="utf-8", errors="ignore")
    start = 0
    if c.startswith("---"):
        e = c.find("\n---", 3)
        start = e + 4 if e != -1 else 0
    m = re.search(r"^# .*$", c[start:], re.MULTILINE)
    if m:
        start += m.end()
    tail = re.search(r"\n# 附属内容区域|\n## 配图详情|\n## 素材溯源|\n## 标题决策说明|"
                     r"\n## 质量自检报告|\n## 互动引导|\n## 配图搜索替换指令|\n## 视觉与配图", c[start:])
    end = start + tail.start() if tail else len(c)
    body = c[start:end]
    paras = []
    for blk in re.split(r"\n\s*\n", body):
        b = blk.strip()
        if not b or b.startswith(("#", "|", ">", "-", "*", "[", "`")):
            continue
        if len(re.findall(r"[\u4e00-\u9fff]", b)) < 5:
            continue
        paras.append(len(re.findall(r"[\u4e00-\u9fff]", b)))
    q = len(re.findall(r"[？?]", body))
    paren = len(re.findall(r"[（(][^）)]{1,40}[）)]", body))
    nums = len(re.findall(r"\d+(?:\.\d+)?", body))
    return dict(n=chk.count_body_chars(p), paras=len(paras),
                avg=round(sum(paras) / len(paras), 1) if paras else 0,
                mx=max(paras) if paras else 0, q=q, paren=paren, nums=nums)


for d in sys.argv[1:]:
    dp = Path(d)
    print(f"\n### {dp.name}")
    for label, pat in (("草稿", "草稿-*.md"), ("润色稿", "润色稿-*.md")):
        fs = list(dp.glob(pat))
        if fs:
            s = stats(fs[0])
            print(f"  {label}: {s}")
    a = chk.extract_body_text(list(dp.glob("草稿-*.md"))[0])
    b = chk.extract_body_text(list(dp.glob("润色稿-*.md"))[0])
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = sm.get_opcodes()
    blocks = [o for o in ops if o[0] != "equal"]
    kinds = {"replace": 0, "insert": 0, "delete": 0}
    for o in blocks:
        kinds[o[0]] = kinds.get(o[0], 0) + 1
    print(f"  相似度 {sm.ratio()*100:.2f}% / 差异率 {(1-sm.ratio())*100:.2f}% / 块 {len(blocks)} / {kinds}")
