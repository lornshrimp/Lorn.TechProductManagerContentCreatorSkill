import re
from pathlib import Path
root = Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体')
drafts_dir = root / 'drafts'
topic_dirs = []
for d in sorted(drafts_dir.iterdir()):
    if not d.is_dir():
        continue
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', d.name):
        topic_dirs += [c for c in sorted(d.iterdir()) if c.is_dir()]
    else:
        topic_dirs.append(d)
today = [d for d in topic_dirs if '2026-10-06' in str(d)]
lines = [f'total topic dirs scanned = {len(topic_dirs)}', f'today dirs = {len(today)}']
for d in today:
    lines.append(f'  {d.relative_to(root)} :: md files = {len(list(d.glob("*.md")))}')
Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/_v_scan.txt').write_text('\n'.join(lines), encoding='utf-8')
