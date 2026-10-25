import urllib.request, re, html, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36'}
def get(u):
    r=urllib.request.Request(u,headers=UA)
    return urllib.request.urlopen(r,timeout=25).read().decode('utf-8','ignore')

# 1 百度热搜
try:
    t=get('https://top.baidu.com/board?tab=realtime')
    m=re.findall(r'"word":"(.*?)"', t)
    seen=[]
    for x in m:
        x=html.unescape(x)
        if x not in seen: seen.append(x)
    print('=== BAIDU ===')
    for i,x in enumerate(seen[:36],1): print('%d##%s'%(i,x))
    print('N',len(seen))
except Exception as e:
    print('BAIDU ERR',repr(e))

# 2 IT之家
try:
    t=get('https://www.ithome.com/')
    m=re.findall(r'<a[^>]*href="https://www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', t, re.S)
    seen=[]
    for x in m:
        x=re.sub(r'<[^>]+>','',html.unescape(x)).strip()
        if len(x)>8 and x not in seen: seen.append(x)
    print('=== ITHOME ===')
    for i,x in enumerate(seen[:25],1): print('%d##%s'%(i,x))
    print('N',len(seen))
except Exception as e:
    print('ITHOME ERR',repr(e))

# 3 网易新闻
try:
    t=get('https://news.163.com/')
    m=re.findall(r'<a[^>]*href="https://www\.163\.com/(?:news|dy)/article/[^"]*"[^>]*>(.*?)</a>', t, re.S)
    seen=[]
    for x in m:
        x=re.sub(r'<[^>]+>','',html.unescape(x)).strip()
        if len(x)>10 and x not in seen: seen.append(x)
    print('=== 163 ===')
    for i,x in enumerate(seen[:25],1): print('%d##%s'%(i,x))
    print('N',len(seen))
except Exception as e:
    print('163 ERR',repr(e))

# 4 澎湃新闻
try:
    t=get('https://www.thepaper.cn/')
    m=re.findall(r'"name":"(.*?)"', t)
    m2=re.findall(r'"title":"(.*?)"', t)
    seen=[]
    for x in m+m2:
        x=html.unescape(x).replace('\\/','/')
        if len(x)>10 and x not in seen: seen.append(x)
    print('=== THEPAPER ===')
    for i,x in enumerate(seen[:25],1): print('%d##%s'%(i,x))
    print('N',len(seen))
except Exception as e:
    print('THEPAPER ERR',repr(e))
