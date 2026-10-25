# -*- coding: utf-8 -*-
import importlib.util, sys
from pathlib import Path
HERE = Path(".workbuddy/scripts").resolve()
_spec = importlib.util.spec_from_file_location("gbjy", HERE / "规范校验.py")
_g = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_g)
d = Path(sys.argv[1])
files = sorted([p for p in d.iterdir() if p.suffix == ".md" and any(p.name.startswith(k) for k in ["知乎-","微信-","百家号-","CSDN-","头条-"])])
fin = next((p for p in d.iterdir() if p.name.startswith("终稿-")), None)
txt = {p.name: _g.extract_body_text(p) for p in files}
if fin: txt[fin.name] = _g.extract_body_text(fin)
names = list(txt)
for i in range(len(names)):
    for j in range(i+1, len(names)):
        s = _g.text_similarity(txt[names[i]], txt[names[j]])
        flag = "  <<< 超限" if s >= (0.99 if "终稿" in names[i]+names[j] else 0.85) else ""
        print("%.3f  %s  x  %s%s" % (s, names[i], names[j], flag))
