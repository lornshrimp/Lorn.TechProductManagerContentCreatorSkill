# -*- coding: utf-8 -*-
import urllib.request, re, json
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'}
def fetch(url, timeout=25):
    req=urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8','ignore')
# IT之家 首页
try:
    h=fetch('https://www.ithome.com/')
    ts=re.findall(r'<a[^>]*href="https://www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', h, re.S)
    ts=[re.sub(r'<[^>]+>','',t).strip() for t in ts]
    ts=[t for t in ts if len(t)>=6]
    seen=[]
    for t in ts:
        if t not in seen: seen.append(t)
    print('###ITHOME###'); print('\n'.join(seen[:30]))
except Exception as e:
    print('###ITHOME###'); print('ERR:'+str(e)[:100])
# 网易新闻
try:
    h=fetch('https://news.163.com/')
    ts=re.findall(r'<a[^>]*>(.*?)</a>', h)
    ts=[re.sub(r'<[^>]+>','',t).strip() for t in ts]
    ts=[t for t in ts if 10<=len(t)<=45 and not re.search(r'登录|下载|客户端|更多|网易|举报|京ICP', t)]
    seen=[]
    for t in ts:
        if t not in seen: seen.append(t)
    print('###163###'); print('\n'.join(seen[:25]))
except Exception as e:
    print('###163###'); print('ERR:'+str(e)[:100])
# 澎湃新闻
try:
    h=fetch('https://www.thepaper.cn/')
    ts=re.findall(r'"name":"(.*?)"', h)
    if len(ts)<5:
        ts=re.findall(r'<a[^>]*class="[^"]*"[^>]*>(.*?)</a>', h)
        ts=[re.sub(r'<[^>]+>','',t).strip() for t in ts]
    ts=[t for t in ts if 8<=len(t)<=60]
    seen=[]
    for t in ts:
        if t not in seen: seen.append(t)
    print('###THEPAPER###'); print('\n'.join(seen[:25]))
except Exception as e:
    print('###THEPAPER###'); print('ERR:'+str(e)[:100])
