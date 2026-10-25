# -*- coding: utf-8 -*-
"""2026-10-07 百度热搜修正采集（修正 UTF-8/unicode_escape 双重编码）"""
import urllib.request, re, io, sys, json, os, ssl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ssl._create_default_https_context = ssl._create_unverified_context
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36')

req = urllib.request.Request('https://top.baidu.com/board?tab=realtime',
                             headers={'User-Agent': UA, 'Accept-Language': 'zh-CN,zh;q=0.9'})
raw = urllib.request.urlopen(req, timeout=25).read()
h = raw.decode('utf-8', 'ignore')

ESC = chr(92) + 'u'   # "\u"
out = []
for m in re.finditer(r'"word":"(.*?)"', h):
    w = m.group(1)
    if ESC in w:
        w = w.encode().decode('unicode_escape')
    else:
        try:
            w = w.encode('latin-1').decode('utf-8')
        except Exception:
            pass
    if w and w not in out:
        out.append(w)

for i, t in enumerate(out[:30], 1):
    print(f'{i}. {t}')
json.dump({'百度热搜榜': out[:30]},
          open(os.path.join(os.environ['TEMP'], 'baidu1007.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('N=', len(out))
