# -*- coding: utf-8 -*-
import subprocess, json, datetime, sys

CLI = r'C:\Users\lorns\AppData\Local\ZhihuCLI\current\zhihu-cli.exe'
sys.stdout.reconfigure(encoding='utf-8')

def run(args):
    p = subprocess.run([CLI] + args, capture_output=True)
    raw = p.stdout
    for enc in ('utf-8', 'gbk', 'utf-16'):
        try:
            return json.loads(raw.decode(enc))
        except Exception:
            continue
    print('PARSE FAIL, raw head:', raw[:300])
    return None

def show(title, ctype):
    d = run(['me', 'contents', '--type', ctype, '--sort', 'ts', '--order', 'desc', '--limit', '50'])
    if not d or 'Data' not in d:
        print(title, '-> no data', d)
        return
    items = d['Data']['Items']
    print(f'===== {title} ({len(items)} items) =====')
    for it in items:
        ts = it.get('CreatedAt', 0)
        dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M') if ts else '?'
        t = it.get('Title', '')
        url = it.get('Url', '')
        mark = ' <<<<< 房贷/40年' if ('房贷' in t or '40' in t or '四十年' in t or '贷款' in t) else ''
        print(f'{dt} | {it.get("ContentType")} | {url} | {t[:50]}{mark}')

show('ANSWER 列表', 'answer')
show('ARTICLE 列表', 'article')
