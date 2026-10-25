import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('chk', r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-10-06/华为与高通达成5G-AI广泛专利许可协议')
final = list(d.glob('终稿-*.md'))[0]
out=[]
for p in sorted(d.glob('*.md')):
    if not any(p.name.startswith(x) for x in ['知乎-','微信-','百家号-','CSDN-','头条-']):
        continue
    out.append(f'--- {p.name}')
    out += m.check_platform_coherence(p, final) or ['  ✅ coherence ok']
    out += m.check_body_structure(p, next((k for k in m.BODY_STRUCTURE_H2_MIN if p.name.startswith(k)),'平台')) or ['  ✅ structure ok']
    out += m.check_anchor_quality(p) or ['  ✅ anchor ok']
Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/_b_chk.txt').write_text('\n'.join(out), encoding='utf-8')
print('ok')
