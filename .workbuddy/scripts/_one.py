# -*- coding: utf-8 -*-
import importlib.util, sys
from pathlib import Path
R = Path(".workbuddy/scripts/规范校验.py").resolve()
spec = importlib.util.spec_from_file_location("chk", R)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
p = Path(sys.argv[1])
print(p.name, "->", m.count_body_chars(p))
