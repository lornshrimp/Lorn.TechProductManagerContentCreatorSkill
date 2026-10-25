# -*- coding: utf-8 -*-
"""统计 md 文件的结构指标：H2 数 / 最长段落中文字符数（复刻 规范校验.py 口径）。"""
import sys, re
from pathlib import Path

import importlib.util
spec = importlib.util.spec_from_file_location("v", str(Path(__file__).parent / "规范校验.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def stats(p: Path, label: str):
    c = p.read_text(encoding="utf-8", errors="ignore")
    start = 0
    if c.startswith("---"):
        e = c.find("\n---", 3)
        start = e + 4 if e != -1 else 0
    m = re.search(r"^# .*$", c[start:], re.MULTILINE)
    if m:
        start += m.end()
    tail = re.search(
        r"\n# 附属内容区域|\n## 配图详情|\n## 素材溯源|\n## 标题决策说明|"
        r"\n## 质量自检报告|\n## 互动引导|\n## 配图搜索替换指令", c[start:])
    end = start + tail.start() if tail else len(c)
    body = c[start:end]
    h2 = len(re.findall(r"^## ", body, re.MULTILINE))
    skip = ("#", "|", ">", "-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "[", "```")
    maxp, over = 0, []
    for blk in re.split(r"\n\s*\n", body):
        b = blk.strip()
        if not b or b.startswith(skip):
            continue
        cn = len(re.findall(r"[\u4e00-\u9fff]", b))
        if cn > maxp:
            maxp = cn
        if cn > 300:
            over.append(cn)
    wc = v.count_body_chars(p)
    return h2, maxp, wc, over


if __name__ == "__main__":
    for a in sys.argv[1:]:
        p = Path(a)
        h2, maxp, wc, over = stats(p, p.name)
        print(f"{p.name}\tH2={h2}\tmaxPara={maxp}\twc={wc}\tover300={over}")
