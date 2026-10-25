# -*- coding: utf-8 -*-
"""平台稿体检：正文字数/占终稿比/H2数/最长段/视觉要素/关键词"""
import io, sys, re, difflib
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
sys.path.insert(0, str(ROOT / ".workbuddy" / "scripts"))
from 规范校验 import extract_body_text, text_similarity, count_body_chars  # noqa

D = sys.argv[1] if len(sys.argv) > 1 else "2026-10-13"
base = ROOT / "drafts" / D
for topic in sorted([p for p in base.iterdir() if p.is_dir()]):
    finals = list(topic.glob("终稿-*.md"))
    if not finals:
        continue
    f = finals[0]
    ft = f.read_text(encoding="utf-8")
    fc = count_body_chars(f)
    print(f"\n### {topic.name}  终稿={fc}")
    plats = [p for p in topic.glob("*.md") if p.name.split("-")[0] in ("知乎", "微信", "百家号", "CSDN", "头条")]
    ratio = {"知乎": .90, "微信": .85, "百家号": .70, "CSDN": .70, "头条": .70}
    fb = extract_body_text(f)
    bodies = {}
    for p in plats:
        plat = p.name.split("-")[0]
        t = p.read_text(encoding="utf-8")
        c = count_body_chars(p)
        h2 = len(re.findall(r"^##\s+", t, re.MULTILINE))
        h2 = h2 - len(re.findall(r"^##\s+(视觉与配图|配图搜索替换指令|SEO 关键词)", t, re.MULTILINE))
        # 最长段
        body = extract_body_text(p)
        segs = [s for s in re.split(r"[。！？\n]", body) if s]
        longest = max((len(s) for s in segs), default=0)
        sim = text_similarity(fb, body)
        bodies[plat] = body
        figs = len(set(re.findall(r"\[配图\s*(\d+)\]", t)))
        print(f"  {plat}: 正文={c} 占终稿={c/fc:.3f} H2={h2} 最长段={longest} 与终稿sim={sim:.4f} 配图={figs}")
    ks = list(bodies)
    mx = 0; pair = ""
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            s = text_similarity(bodies[ks[i]], bodies[ks[j]])
            if s > mx:
                mx, pair = s, f"{ks[i]}x{ks[j]}"
    print(f"  平台两两最高: {pair} {mx:.4f}")
