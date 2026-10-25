import importlib.util, sys, io
from pathlib import Path

spec = importlib.util.spec_from_file_location('chk', r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

d = Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-10-06/华为与高通达成5G-AI广泛专利许可协议')
final = list(d.glob('终稿-*.md'))[0]
fc = m.count_body_chars(final)
ft = m.extract_body_text(final)
lines = [f'终稿 {final.name} = {fc}']
for p in sorted(d.glob('*.md')):
    if not any(p.name.startswith(x) for x in ['知乎-','微信-','百家号-','CSDN-','头条-']):
        continue
    n = m.count_body_chars(p)
    sim = m.text_similarity(m.extract_body_text(p), ft)
    lines.append(f'{p.name} | {n} 字 | ratio={n/fc:.3f} | vs终稿sim={sim:.4f}')
# pairwise
import itertools
pfs = [p for p in sorted(d.glob('*.md')) if any(p.name.startswith(x) for x in ['知乎-','微信-','百家号-','CSDN-','头条-'])]
for a,b in itertools.combinations(pfs,2):
    s = m.text_similarity(m.extract_body_text(a), m.extract_body_text(b))
    if s >= 0.6:
        lines.append(f'PAIR {a.name[:6]} vs {b.name[:6]} = {s:.4f}')
Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/_b_len.txt').write_text('\n'.join(lines), encoding='utf-8')
print('done')
