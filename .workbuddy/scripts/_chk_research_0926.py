import sys, re
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

root = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
dirs = ["全国牛肉批发均价涨至一公斤71元-创两年新高","Anthropic推演2030美国经济-钱继续流向有钱人","央视曝光挂靠参保骗社保-灰色产业链如何运作"]
for d in dirs:
    p = root/"research"/d/"研究报告.md"
    if not p.exists():
        print(f"[ MISS ] {d}")
        continue
    txt = p.read_text(encoding="utf-8")
    n = len(re.findall(r"[\u4e00-\u9fff]", txt))
    body = chk.count_body_chars(p)
    keys = chk.check_yaml_required(p, chk.REQUIRED_YAML_KEYS["research"])
    urls = len(re.findall(r"https?://", txt))
    head = txt.split("---")[1] if txt.startswith("---") else ""
    print(f"[FILE] {d}")
    print(f"   全文中文字符={n}  count_body_chars={body}  URL数={urls}")
    print(f"   frontmatter:\n{head.strip()}")
    print(f"   yaml required issues={keys}")
    print()
