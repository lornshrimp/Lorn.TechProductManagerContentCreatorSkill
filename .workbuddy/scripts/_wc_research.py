import re,sys
from pathlib import Path
p=Path(sys.argv[1])
t=p.read_text(encoding='utf-8')
# strip frontmatter
if t.startswith('---'):
    i=t.find('\n---',3)
    t=t[i+4:]
# truncate at 质量控制自检
for m in ['## 报告质量控制标准自检','## 质量控制自检','## 素材溯源','## 质量自检报告','## 质量自检']:
    j=t.find(m)
    if j>0:
        t=t[:j]
        break
n=len(re.findall(r'[\u4e00-\u9fff]',t))
print(f"{n}")
