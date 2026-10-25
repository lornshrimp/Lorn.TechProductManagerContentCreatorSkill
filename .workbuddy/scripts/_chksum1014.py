# -*- coding: utf-8 -*-
import io, sys, collections, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
t = open('.workbuddy/scripts/_校验_2026-10-14.txt', encoding='utf-8', errors='ignore').read()
lines = t.splitlines()
dirs = [l for l in lines if l.startswith('[选题目录]')]
c = collections.Counter()
for d in dirs:
    m = re.search(r'drafts[\\/]+(\d{4}-\d{2}-\d{2})', d)
    c[m.group(1) if m else '(无日期/顶层)'] += 1
print('问题目录按日期分布：')
for k in sorted(c):
    print(' ', k, c[k])
print('今日 2026-10-14 问题目录数：', c.get('2026-10-14', 0))
