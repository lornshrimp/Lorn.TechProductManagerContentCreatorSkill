# -*- coding: utf-8 -*-
import re,io,sys,os,json,pathlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=os.path.join(os.environ.get("TEMP","."),"bsk1017","douyin.txt")
raw=pathlib.Path(p).read_text(encoding='utf-8',errors='replace')
lines=[l.strip() for l in raw.split("\n") if l.strip()]
out=[]
i=0
while i<len(lines):
    l=lines[i]
    if re.match(r'^\d+$',l) and i+1<len(lines):
        nm=lines[i+1]
        hv=lines[i+2] if i+2<len(lines) and re.match(r'^[\d.]+万?$',lines[i+2]) else ""
        if 4<len(nm)<60: out.append([nm,hv])
        i+=3; continue
    i+=1
seen=[]
for nm,hv in out:
    if nm not in [x[0] for x in seen]: seen.append([nm,hv])
print(f"抖音命中 {len(seen)} 条")
for i,(a,b) in enumerate(seen[:30],1): print(f"{i}. {a} [{b}]")
json.dump(seen[:30],open(os.path.join(os.environ.get("TEMP","."),"douyin1017.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("SAVED")
