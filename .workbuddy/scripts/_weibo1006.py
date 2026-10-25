# -*- coding: utf-8 -*-
import re, json, os, sys
O = os.path.join(os.environ.get("TEMP", ""), "bsk1006")
p = os.path.join(O, "weibo.html")
h = open(p, encoding="utf-8", errors="ignore").read()
out = []
# 微博热搜条目通常含 "word":"xxx" 或 data-title
for m in re.finditer(r'"word"\s*:\s*"(.*?)"', h):
    w = m.group(1)
    try:
        w = w.encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")
    except Exception:
        pass
    if w and w not in out:
        out.append(w)
if not out:
    for m in re.finditer(r'<span[^>]*class="[^"]*word[^"]*"[^>]*>(.*?)</span>', h):
        t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if t and t not in out:
            out.append(t)
if not out:
    # fallback: td-02 结构
    for m in re.finditer(r'>(.*?)</a>', h):
        t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if t and 4 < len(t) < 40 and t not in out:
            out.append(t)
print("WEIBO", len(out))
for x in out[:30]:
    print(" ", x)
json.dump(out, open(os.path.join(O, "weibo_parsed.json"), "w", encoding="utf-8"), ensure_ascii=False)
