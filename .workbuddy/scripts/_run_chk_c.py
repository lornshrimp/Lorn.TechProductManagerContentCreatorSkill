import io, sys, runpy, traceback
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
CHECKER = ROOT / ".workbuddy" / "scripts" / "规范校验.py"

buf = io.StringIO()
_old = sys.stdout
sys.stdout = buf
sys.argv = ["规范校验.py", "--date", "2026-10-06"]
err = ""
try:
    runpy.run_path(str(CHECKER), run_name="__main__")
except SystemExit:
    pass
except BaseException:
    err = traceback.format_exc()
finally:
    sys.stdout = _old

out = ROOT / ".workbuddy" / "_chk_out.txt"
out.write_text(buf.getvalue() + "\n\n===TRACEBACK===\n" + err, encoding="utf-8")
print("OK len=%d" % len(buf.getvalue()))
