# -*- coding: utf-8 -*-
"""通用：三选题平台稿保真比 + 两两相似度 + 与终稿相似度 + 平台标题两两相似度"""
import importlib.util, itertools, re
from pathlib import Path

root = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("guifan", root / ".workbuddy" / "scripts" / "规范校验.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

TOPICS = [
    ("A", "前8个月税收增5.9%-纳税集中度的分配读数", "纳税集中度的分配读数"),
    ("B", "中办国办分类推进高校改革-教育供给的错配账", "教育供给的错配账"),
    ("C", "反外国制裁法新案例安世21.39亿财产被查封-资产保全的定价权", "资产保全的定价权"),
]
plats = ["知乎", "微信", "百家号", "CSDN", "头条"]
out = []
for tag, dirname, stem in TOPICS:
    d = root / "drafts" / "2026-09-22" / dirname
    final = d / f"终稿-{stem}.md"
    if not final.exists():
        out.append(f"## {tag} 终稿缺失 {final}")
        continue
    fc = mod.count_body_chars(final)
    fb = mod.extract_body_text(final)
    files = {p: d / f"{p}-{stem}.md" for p in plats}
    out.append(f"########## {tag} {dirname} | 终稿字数={fc} ##########")
    for p, f in files.items():
        if not f.exists():
            out.append(f"{p}: 文件缺失")
            continue
        tb = mod.extract_body_text(f)
        cnt = mod.count_body_chars(f)
        sim = mod.text_similarity(fb, tb)
        out.append(f"{p}: 字数={cnt} 保真={cnt/fc*100:.1f}% vs终稿相似={sim*100:.1f}%")
    out.append("--- 平台两两 ---")
    ok = {p: f for p, f in files.items() if f.exists()}
    for a, b in itertools.combinations(sorted(ok), 2):
        s = mod.text_similarity(mod.extract_body_text(ok[a]), mod.extract_body_text(ok[b]))
        mark = "  <<<超85%" if s * 100 >= 85 else ""
        out.append(f"{a} x {b}: {s*100:.1f}%{mark}")
    out.append("--- 平台标题两两 ---")
    tt = {}
    for p, f in ok.items():
        txt = f.read_text(encoding="utf-8", errors="ignore")
        try:
            fm, _ = mod.parse_yaml_frontmatter(txt)
        except Exception:
            fm = {}
        t = (fm.get("title") or "").strip()
        h1 = re.search(r"^#\s+(.+)$", txt, re.MULTILINE)
        h1t = h1.group(1).strip() if h1 else ""
        if h1t and (not t or any(t.startswith(x + "-") for x in plats)):
            t = h1t
        tt[p] = t
    for a, b in itertools.combinations(sorted(tt), 2):
        s = mod.text_similarity(tt[a], tt[b])
        mark = "  <<<超85%" if s * 100 >= 85 else ""
        out.append(f"{a}「{tt[a]}」x {b}「{tt[b]}」: {s*100:.1f}%{mark}")
    out.append("")

txt = "\n".join(out)
(root / ".workbuddy/_sim_all_0922.txt").write_text(txt, encoding="utf-8")
print("OK")
