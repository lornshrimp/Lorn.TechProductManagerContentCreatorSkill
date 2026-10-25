# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
R = Path(".workbuddy/scripts/规范校验.py").resolve()
spec = importlib.util.spec_from_file_location("chk", R)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
f = Path("drafts/2026-09-26/Anthropic推演2030美国经济-钱继续流向有钱人/终稿-Anthropic-自己算出了-钱继续流向有钱人-AI-的账-不在能力表上-在分配那一栏.md")
body = m._raw_body(f)
print("raw_body chars:", len(body))
print("count:", m.count_body_chars(f))
for mk in m.BODY_TRUNCATE_MARKERS:
    idx = body.find(mk)
    if idx >= 0:
        print("marker hit:", repr(mk), "at", idx)
print("--- tail 400 ---")
print(body[-400:])
