# -*- coding: utf-8 -*-
"""修正百度热搜榜编码 + 补采：直接 JSON 解析 word 字段"""
import urllib.request, re, json, gzip, ssl

ssl._create_default_https_context = ssl._create_unverified_context
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", "ignore")


h = fetch("https://top.baidu.com/board?tab=realtime")
out = []
for m in re.finditer(r'"word":"(.*?)"', h):
    s = m.group(1)
    # 正确处理 JSON 转义（仅在有反斜杠时）
    if "\\" in s:
        try:
            s = json.loads('"' + s + '"')
        except Exception:
            pass
    out.append(s)
print("BAIDU", len(out))
for x in out[:30]:
    print(x)
json.dump(out[:30], open(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\.workbuddy\scripts\_baidu_0927.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
