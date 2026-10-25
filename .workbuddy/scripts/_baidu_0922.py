# -*- coding: utf-8 -*-
import urllib.request, re, io, sys, gzip
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
req = urllib.request.Request("https://top.baidu.com/board?tab=realtime",
                             headers={"User-Agent": UA})
h = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
out = []
for m in re.finditer(r'"word":"(.*?)"', h):
    w = m.group(1)
    if w not in out:
        out.append(w)
print("count", len(out))
for i, w in enumerate(out[:35], 1):
    print(i, w)
