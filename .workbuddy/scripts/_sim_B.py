import importlib.util, re, itertools
from pathlib import Path
root = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("guifan", root / ".workbuddy" / "scripts" / "规范校验.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
d = root / "drafts" / "2026-09-22" / "中办国办分类推进高校改革-教育供给的错配账"
final = d / "终稿-教育供给的错配账.md"
plats = ["知乎","微信","百家号","CSDN","头条"]
files = {p: d / f"{p}-教育供给的错配账.md" for p in plats}
fb = mod.extract_body_text(final)
out=[]
for p,f in files.items():
    tb = mod.extract_body_text(f)
    sim = mod.text_similarity(fb, tb)
    cnt = mod.count_body_chars(f)
    out.append(f"{p}: 字数={cnt} 保真={cnt/mod.count_body_chars(final)*100:.1f}% vs终稿相似={sim*100:.1f}%")
out.append("---两两---")
for a,b in itertools.combinations(plats,2):
    s = mod.text_similarity(mod.extract_body_text(files[a]), mod.extract_body_text(files[b]))
    out.append(f"{a} x {b}: {s*100:.1f}%")
Path(root/".workbuddy"/"scripts"/"_sim_B_out.txt").write_text("\n".join(out),encoding="utf-8")
print("OK")
