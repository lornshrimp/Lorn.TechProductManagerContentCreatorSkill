import re,sys
def c(s):
    return len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
def punct(s):
    # 零标点检测：标题中是否含任一标点
    marks='，。？！：；、·—…《》“”‘’（）%．.,?!:;'
    return any(m in s for m in marks), ('？' in s or '?' in s)
RANGE={'zhihu':(15,35),'wechat':(15,25),'toutiao':(18,25),'baijiahao':(20,30),'csdn':(1,60)}
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    parts=line.split('\t')
    plat=parts[0].strip(); t=parts[1].strip() if len(parts)>1 else ''
    n=c(t); hasp,hasq=punct(t)
    lo,hi=RANGE.get(plat,(0,999))
    ok='OK' if lo<=n<=hi else 'FAIL'
    warn=[]
    if n>=16 and not hasp: warn.append('PUNCT0')
    elif 12<=n<=15 and not hasp: warn.append('PUNCT0-WARN')
    if re.search(r'(为什么|怎么|吗|呢|哪些|多少|是什么|如何)',t) and not hasq:
        warn.append('NOQ')
    print(f"{plat}\t{n}\t[{lo},{hi}]\t{ok}\t{','.join(warn) or '-'}\t{t}")
