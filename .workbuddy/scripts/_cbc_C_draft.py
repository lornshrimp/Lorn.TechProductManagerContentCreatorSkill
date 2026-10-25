import re, difflib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(".workbuddy/scripts").resolve()))
import importlib.util
spec = importlib.util.spec_from_file_location("chk", ".workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

d = Path("drafts/2026-09-25/美团抽成太多-25元外卖的三方账/草稿-三方账.md")
print("草稿 count_body_chars =", m.count_body_chars(d))
body = m.extract_body_text(d) if hasattr(m, "extract_body_text") else None
if body:
    n = len(re.findall(r"[\u4e00-\u9fff]", body))
    print("草稿 extract_body_text 汉字 =", n)
