import subprocess, sys, pathlib
BASE = pathlib.Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体')
CHECKER = BASE / '.workbuddy' / 'scripts' / '规范校验.py'
r = subprocess.run([sys.executable, str(CHECKER), '--date', '2026-10-06'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
out = BASE / '.workbuddy' / '_校验_2026-10-06.txt'
out.write_text((r.stdout or '') + '\n[STDERR]\n' + (r.stderr or ''), encoding='utf-8')
status = BASE / '.workbuddy' / '_v_status.txt'
lines = (r.stdout or '').splitlines()
today = [l for l in lines if '2026-10-06' in l]
status.write_text(
    f'rc={r.returncode}\nbytes={out.stat().st_size}\ntoday_lines={len(today)}\n'
    + '\n'.join(today[:80]), encoding='utf-8')
print('done', r.returncode, out.stat().st_size)
