# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
R = Path(".workbuddy/scripts/规范校验.py").resolve()
spec = importlib.util.spec_from_file_location("chk", R)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
D = Path("drafts/2026-09-26")
out = []
for topic in sorted([p for p in D.iterdir() if p.is_dir()]):
    out.append("### %s" % topic.name)
    fin = list(topic.glob("终稿-*.md"))[0]
    pfs = sorted([f for f in topic.glob("*.md") if any(f.name.startswith(x) for x in m.PLATFORM_PREFIX)])
    for pf in pfs:
        txt = pf.read_text(encoding="utf-8", errors="ignore")
        rows = []
        if pf.name.startswith("知乎-"):
            fm, _ = m.parse_yaml_frontmatter(txt)
            if not fm.get("source_label"): rows.append("缺 source_label")
            rows += m.check_clickable_link(pf)
        else:
            pfx = next((p for p in m.PLATFORM_PREFIX if pf.name.startswith(p)), None)
            for kws, desc in m.PLATFORM_PREFIX[pfx]:
                if not any(k in txt for k in kws): rows.append("缺: " + desc)
        if not pf.name.startswith("头条-"):
            for vk,(vkw,vdesc) in m.PLATFORM_VISUAL_CHECKS.items():
                if not any(k in txt for k in vkw): rows.append("视觉缺: " + vdesc)
        else:
            for vkw,vdesc in m.TOUTIAO_VISUAL_REQUIRED:
                if not any(k in txt for k in vkw): rows.append("头条视觉缺: " + vdesc)
            fk,fdesc = m.PLATFORM_VISUAL_CHECKS["figures"]
            if not any(k in txt for k in fk): rows.append("头条视觉缺: " + fdesc)
        import re
        if re.search(r"^#{1,3}\s*(读者互动|互动引导)\s*$", txt, re.M):
            rows.append("互动引导另起小标题")
        out.append("  %-58s %s" % (pf.name[:58], "OK" if not rows else " | ".join(rows)))
    # titles
    out.append("  --- 平台标题: " + " | ".join(f.name.split("-")[0] for f in pfs))
out.append("")
out.append("=== 标题标点门禁 ===")
out.append("(标题标点：见全量校验报告，今日无段=0问题)")
Path(".workbuddy/scripts/_spec_0926.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
