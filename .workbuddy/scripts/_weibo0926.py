import json, urllib.request, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
hdr = {
 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
 'Referer':'https://weibo.com/hot/search',
 'Accept':'application/json, text/plain, */*',
}
out=[]
for u in ['https://weibo.com/ajax/side/hotSearch']:
    try:
        req=urllib.request.Request(u, headers=hdr)
        with urllib.request.urlopen(req, timeout=25) as r:
            d=json.loads(r.read().decode('utf-8'))
        band=d.get('data',{}).get('realtime',[])
        for i,x in enumerate(band[:50],1):
            w=x.get('word') or x.get('note') or ''
            if w: out.append(f"{i}##{w}##{x.get('num','')}")
        print("WEIBO OK", len(out))
    except Exception as e:
        print("WEIBO FAIL", type(e).__name__, e)
open(r"C:/Users/lorns/AppData/Local/Temp/bsk0926/weibo_api.txt","w",encoding="utf-8").write("\n".join(out))
for l in out[:15]: print(l)
