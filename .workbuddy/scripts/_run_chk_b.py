# -*- coding: utf-8 -*-
"""同进程运行 规范校验.py（runpy + StringIO 接管 stdout），绕开子进程限制与 PowerShell 编码。
用法：python _run_chk.py --date 2026-10-06
输出：{项目根}/.workbuddy/_校验_{date}.txt
"""
import argparse
import io
import pathlib
import runpy
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
CHECKER = BASE / '.workbuddy' / 'scripts' / '规范校验.py'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', default='2026-10-06')
    args = ap.parse_args()

    buf = io.StringIO()
    old_argv, old_out = sys.argv, sys.stdout
    sys.argv = [str(CHECKER), '--date', args.date]
    sys.stdout = buf
    try:
        runpy.run_path(str(CHECKER), run_name='__main__')
    except SystemExit:
        pass
    except Exception:
        import traceback
        buf.write('\n[EXC]\n' + traceback.format_exc())
    finally:
        sys.stdout = old_out
        sys.argv = old_argv

    text = buf.getvalue()
    out = BASE / '.workbuddy' / f'_校验_{args.date}.txt'
    out.write_text(text, encoding='utf-8')

    marker = f'drafts\\{args.date}\\'
    status = BASE / '.workbuddy' / '_v_status.txt'
    today_block = marker in text
    tail = [ln for ln in text.splitlines() if ln.startswith('共发现')]
    status.write_text(
        f'today_block={today_block}\nsummary={tail[-1] if tail else "n/a"}\nbytes={out.stat().st_size}\n',
        encoding='utf-8')


if __name__ == '__main__':
    main()
