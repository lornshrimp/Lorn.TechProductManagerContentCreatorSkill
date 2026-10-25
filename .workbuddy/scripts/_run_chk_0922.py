import runpy, io, sys, pathlib, traceback
root = pathlib.Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
sys.argv = ["规范校验.py", "--date", "2026-09-22"]
buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
err = ""
try:
    runpy.run_path(str(root / ".workbuddy/scripts/规范校验.py"), run_name="__main__")
except SystemExit as e:
    err = "SystemExit: %r" % (e,)
except BaseException:
    err = traceback.format_exc()
finally:
    sys.stdout = old
out = root / ".workbuddy/_chk_0922.txt"
out.write_text(buf.getvalue() + "\n\n=== ERR ===\n" + err, encoding="utf-8")
print("DONE", len(buf.getvalue()))
