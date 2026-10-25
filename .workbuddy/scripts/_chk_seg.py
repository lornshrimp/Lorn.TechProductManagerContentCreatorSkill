# -*- coding: utf-8 -*-
"""分段统计草稿正文字数（H2 分段），用于占比较验。
用法：python _chk_seg.py <文件路径>
"""
import re
import sys
from pathlib import Path
from io import StringIO

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main():
    p = Path(sys.argv[1])
    text = p.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    # 截到附属区
    for marker in ["## 素材溯源", "## 标题决策说明", "## 质量自检报告"]:
        i = text.find(marker)
        if i != -1:
            text = text[:i]
            break
    text = re.sub(r"^#\s+.*$", "", text, flags=re.MULTILINE)
    # 按 H2 分段
    segs = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    # segs[0] 是段前内容
    rows = []
    total = 0
    chunks = []
    for i in range(1, len(segs), 2):
        title = segs[i].strip()
        body = segs[i + 1] if i + 1 < len(segs) else ""
        n = len(re.findall(r"[\u4e00-\u9fff]", body))
        total += n
        chunks.append((title, n))
    out = "\n".join(f"{n} 字 ({n*100//max(total,1)}%)  {t}" for t, n in chunks)
    out += f"\n----\n合计 {total} 字"
    Path(ROOT / "_chk_seg_out.txt").write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
