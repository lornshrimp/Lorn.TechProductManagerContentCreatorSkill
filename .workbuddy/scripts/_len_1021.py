# -*- coding: utf-8 -*-
"""字数/结构实测（复用 规范校验.py 口径）"""
import io
import sys
import importlib.util
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def report(p):
    p = Path(p)
    if not p.exists():
        print(f"MISSING {p}")
        return {}
    n = chk.count_body_chars(p)
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
    h2 = len(re.findall(r"^## ", body, re.MULTILINE))
    mx = 0
    for blk in re.split(r"\n\s*\n", body):
        b = blk.strip()
        if not b or b.startswith(("#", "|", ">", "-", "*", "[", "`")):
            continue
        mx = max(mx, len(re.findall(r"[\u4e00-\u9fff]", b)))
    print(f"{p.name}: {n} 字 / H2={h2} / 最长段={mx}")
    return {"n": n, "h2": h2, "mx": mx}


if __name__ == "__main__":
    for a in sys.argv[1:]:
        report(a)
