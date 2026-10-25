import difflib, importlib.util, itertools
from pathlib import Path
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16/约谈在线酒店预订平台-竞争秩序账本")
final = d/"终稿-约谈在线酒店预订平台.md"
fb = m.count_body_chars(final)
out=[f"FINAL={fb}"]
plats={}
for p in ["知乎","微信","百家号","CSDN","头条"]:
    f = next(d.glob(p+"-*.md"))
    n = m.count_body_chars(f)
    body = m.extract_body_text(f)
    sim = difflib.SequenceMatcher(None, body, m.extract_body_text(final), autojunk=False).ratio()
    plats[p]=body
    out.append(f"{p}: {n} ratio={n/fb*100:.1f}% sim_final={sim*100:.1f}%")
out.append("--- pairwise ---")
for a,b in itertools.combinations(plats,2):
    r = difflib.SequenceMatcher(None, plats[a], plats[b], autojunk=False).ratio()
    out.append(f"{a}x{b}: {r*100:.1f}%")
Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_m2_a.txt").write_text("\n".join(out), encoding="utf-8")
print("ok")
