# -*- coding: utf-8 -*-
"""门禁自测：check_notebook_refs 必须能报出已知不存在的引用（正例/负例各一）"""
import sys, importlib.util
from pathlib import Path

root = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("guifan", root / ".workbuddy" / "scripts" / "规范校验.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

nb = root / "notebook"
tmp = root / ".workbuddy" / "_t_notebookref.md"
out = []

# 正例：引用不存在文件 → 应报 ❌
tmp.write_text(
    "---\ntype: 大纲\ndate: 2026-09-22\ntopic: t\nmodel: m\n---\n\n"
    "作者观点底座取自 `notebook/指标治理.md` 与 `notebook/不存在的观点域.md`。\n",
    encoding="utf-8")
r = mod.check_notebook_refs(tmp, nb)
out.append(f"[正例] 命中 {len(r)} 项（期望 2）")
for x in r:
    out.append("   " + x.strip())

# 负例：全部引用真实存在 → 应 0 项
tmp.write_text(
    "---\ntype: 大纲\ndate: 2026-09-22\ntopic: t\nmodel: m\n---\n\n"
    "作者观点底座取自 `notebook/宏观数据的阶级分析.md`、`notebook/制度激励与资本转移.md`。\n",
    encoding="utf-8")
r2 = mod.check_notebook_refs(tmp, nb)
out.append(f"[负例] 命中 {len(r2)} 项（期望 0）")
for x in r2:
    out.append("   " + x.strip())

tmp.unlink()
(root / ".workbuddy/_nbgate_selftest.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
