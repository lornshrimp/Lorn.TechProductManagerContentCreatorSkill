# -*- coding: utf-8 -*-
import re,io,sys,os,json,pathlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=os.path.join(os.environ.get("TEMP","."),"bsk1017","weibo.html")
h=pathlib.Path(p).read_text(encoding='utf-8',errors='replace')
out=[]
for m in re.finditer(r'<td class="td-02">\s*<a[^>]*>(.*?)</a>', h, re.S):
    t=re.sub(r"<[^>]+>","",m.group(1)).strip()
    if t and t not in out: out.append(t)
if len(out)<10:
    for m in re.finditer(r'<a href="/weibo\?q=[^"]*"[^>]*>(.*?)</a>', h, re.S):
        t=re.sub(r"<[^>]+>","",m.group(1)).strip()
        if 4<len(t)<50 and t not in out: out.append(t)
print(f"微博命中 {len(out)} 条")
for i,t in enumerate(out[:55],1): print(f"{i}. {t}")
json.dump(out[:55],open(os.path.join(os.environ.get("TEMP","."),"weibo1017.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("SAVED")
