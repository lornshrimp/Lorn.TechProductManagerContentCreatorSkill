# -*- coding: utf-8 -*-
import urllib.request, re, json, os
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'}
def fetch(url, timeout=25):
    req=urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8','ignore')
res={}
# 百度热搜
try:
    h=fetch('https://top.baidu.com/board?tab=realtime')
    titles=re.findall(r'"query":"(.*?)"', h)
    if not titles:
        titles=re.findall(r'class="c-single-text-ellipsis">\s*(.*?)\s*<', h, re.S)
    seen=[];
    for t in titles:
        t=t.strip()
        if t and t not in seen: seen.append(t)
    res['baidu']=seen[:30]
except Exception as e:
    res['baidu']=['ERR:'+str(e)[:80]]
print('###BAIDU###')
print('\n'.join(res['baidu']))
