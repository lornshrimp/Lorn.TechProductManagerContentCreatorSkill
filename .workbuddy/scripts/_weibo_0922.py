# -*- coding: utf-8 -*-
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
p = os.path.join(os.environ['TEMP'], 'bsk0922', 'weibo.html')
h = open(p, encoding='utf-8', errors='ignore').read()
print("len", len(h))
# 热搜词条通常在 <a href="//s.weibo.com/weibo?q=..."> 或 数据脚本里
words = []
for m in re.finditer(r'<a[^>]*href="[^"]*s\.weibo\.com/weibo\?q=[^"]*"[^>]*>(.*?)</a>', h, re.S):
    t = re.sub(r"<[^>]+>", "", m.group(1))
    t = re.sub(r"\s+", "", t)
    if t and t not in words:
        words.append(t)
print("A_weibo_q", len(words))
for w in words[:60]:
    print(" -", w)
print("---- num/hot pattern ----")
# 尝试 数字 + 词条 + 热度
for m in re.finditer(r'"word":"(.*?)"', h):
    print("J", m.group(1))
# 通用: 提取 "热搜" 附近文本块
idx = h.find("热搜")
print("---- snippet around 热搜 ----")
if idx > 0:
    s = re.sub(r"<[^>]+>", "|", h[idx-200:idx+3000])
    s = re.sub(r"\|+", "|", s)
    print(s[:2500])
