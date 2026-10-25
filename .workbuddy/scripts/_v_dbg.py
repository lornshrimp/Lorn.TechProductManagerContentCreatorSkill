import pathlib, sys, traceback
BASE = pathlib.Path(r'D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体')
log = BASE / '.workbuddy' / '_v_dbg.txt'
try:
    log.write_text('start\n', encoding='utf-8')
    import subprocess
    CHECKER = BASE / '.workbuddy' / 'scripts' / '规范校验.py'
    log.write_text(log.read_text(encoding='utf-8') + f'checker exists={CHECKER.exists()}\n', encoding='utf-8')
    r = subprocess.run([sys.executable, str(CHECKER), '--date', '2026-10-06'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    log.write_text(log.read_text(encoding='utf-8') + f'rc={r.returncode} outlen={len(r.stdout or "")} errlen={len(r.stderr or "")}\n', encoding='utf-8')
    (BASE / '.workbuddy' / '_校验_2026-10-06.txt').write_text((r.stdout or '') + '\n[STDERR]\n' + (r.stderr or ''), encoding='utf-8')
    log.write_text(log.read_text(encoding='utf-8') + 'written\n', encoding='utf-8')
except Exception:
    log.write_text(log.read_text(encoding='utf-8') + traceback.format_exc(), encoding='utf-8')
