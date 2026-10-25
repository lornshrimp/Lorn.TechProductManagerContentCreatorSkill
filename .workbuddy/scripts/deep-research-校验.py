#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deep-research 项目级字段覆盖校验（适配本项目 fields.yaml 字典格式）

背景：上游 skill 自带 validate_json.py 依赖硬编码的 CATEGORY_MAPPING（仅认"基本信息/技术特性"
等固定分类名），且读取顶层键 field_categories；本项目 fields.yaml 使用 `fields:` 字典格式且
分类为自定义中文名（数据/方法论/交叉验证/支付能力判别/写作可用性/作者观点对齐），
导致上游脚本解析出 0 字段、覆盖率恒 100%、valid 恒真 —— 属空校验。
本脚本按实际结构校验，作为真实门禁。

用法:
  python deep-research-校验.py --topic-dir "<主题目录>"            # 校验 results/ 下全部 json
  python deep-research-校验.py --topic-dir "<目录>" --json a.json b.json
  python deep-research-校验.py --topic-dir "<目录>" --quiet
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

SKIP_KEYS = {"_source_file", "uncertain", "uncertain_fields"}

# python 代码块误报：字段值里出现 "python -c ..." 等不影响，但需防止把列表项当字段
NOISE_PATTERNS = [
    re.compile(r"^\s*$"),
]


def load_fields(fields_path: Path):
    """从 fields.yaml 提取全部叶子字段名（兼容 fields 字典 / field_categories 列表两种格式）"""
    data = yaml.safe_load(fields_path.read_text(encoding="utf-8")) or {}
    fields = {}          # name -> category
    required = set()
    uncertain_declared = set(data.get("uncertain") or [])

    # 格式 A：fields: {分类: [ {name,...}, ... ]}
    if isinstance(data.get("fields"), dict):
        for cat, flist in data["fields"].items():
            if not isinstance(flist, list):
                continue
            for f in flist:
                if isinstance(f, dict) and f.get("name"):
                    fields[f["name"]] = cat
                    if f.get("required"):
                        required.add(f["name"])

    # 格式 B：field_categories: [ {category:..., fields:[{name,...}]} ]
    if isinstance(data.get("field_categories"), list):
        for cat in data["field_categories"]:
            cname = cat.get("category", "未知")
            for f in cat.get("fields", []) or []:
                if isinstance(f, dict) and f.get("name"):
                    fields[f["name"]] = cname
                    if f.get("required"):
                        required.add(f["name"])

    return fields, required, uncertain_declared


def collect_leaf_keys(obj, acc, depth=0):
    """递归收集 JSON 中的叶子字段名。
    规则：dict 的 key 全部计入；若 value 也是 dict 则同时下钻（叶子与容器名都算，
    以便兼容 'basic_info: {name:...}' 与 'name: {...}' 两类写法）。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_KEYS:
                continue
            if isinstance(v, dict):
                acc.add(k)
                collect_leaf_keys(v, acc, depth + 1)
            elif isinstance(v, list):
                acc.add(k)
                for it in v:
                    if isinstance(it, dict):
                        collect_leaf_keys(it, acc, depth + 1)
            else:
                acc.add(k)
    return acc


def check_json(json_path: Path, all_fields, required, uncertain_declared):
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        load_ok, load_err = True, ""
    except Exception as e:                                   # noqa: BLE001
        return {
            "file": json_path.name, "load_ok": False,
            "load_err": f"{type(e).__name__}: {e}",
            "total": len(all_fields), "covered": 0, "missing": sorted(all_fields),
            "coverage": 0.0, "missing_required": sorted(required), "extra": [],
        }

    json_keys = collect_leaf_keys(data, set())
    covered = set(all_fields) & json_keys
    missing = set(all_fields) - json_keys
    extra = json_keys - set(all_fields)

    # 未获取项：值里含 "❌ 未获取" 视为已声明缺失（合规），不计入错误
    undeclared = []
    for f in missing:
        pass  # 缺失即缺失，值层面的 ❌ 已由代理在字段内声明

    return {
        "file": json_path.name, "load_ok": True, "load_err": "",
        "total": len(all_fields), "covered": len(covered),
        "missing": sorted(missing),
        "coverage": len(covered) / len(all_fields) * 100 if all_fields else 100.0,
        "missing_required": sorted(missing & set(required)),
        "extra": sorted(extra),
        "uncertain_count": len(data.get("uncertain") or []) if isinstance(data, dict) else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic-dir", "-t", required=True, help="主题目录（含 fields.yaml 与 results/）")
    ap.add_argument("--fields", "-f", default=None, help="fields.yaml 路径（默认 <topic>/fields.yaml）")
    ap.add_argument("--json", "-j", nargs="*", default=None, help="指定 json 文件（默认 results/*.json）")
    ap.add_argument("--quiet", "-q", action="store_true")
    ap.add_argument("--out", "-o", default=None, help="结果写入文件（默认 <topic>/_校验结果.txt）")
    args = ap.parse_args()

    topic = Path(args.topic_dir)
    fields_path = Path(args.fields) if args.fields else topic / "fields.yaml"
    if not fields_path.exists():
        print(f"[ERROR] fields.yaml not found: {fields_path}")
        sys.exit(1)

    all_fields, required, uncertain_declared = load_fields(fields_path)
    if not all_fields:
        print("[ERROR] fields.yaml 未解析出任何字段，请检查格式")
        sys.exit(1)

    if args.json:
        files = [Path(p) for p in args.json]
    else:
        rdir = topic / "results"
        files = sorted(rdir.glob("item_*.json")) if rdir.exists() else []

    lines = []
    lines.append("=" * 68)
    lines.append(f"字段定义: {fields_path}")
    lines.append(f"定义字段数: {len(all_fields)}  (必填 {len(required)})")
    lines.append(f"待校验文件: {len(files)}")
    lines.append("=" * 68)

    if not files:
        lines.append("[WARN] 未找到待校验 JSON")

    ok = 0
    bad = []
    for fp in files:
        r = check_json(fp, all_fields, required, uncertain_declared)
        if not r["load_ok"]:
            lines.append(f"\n[FAIL] {r['file']}  JSON 解析失败 -> {r['load_err']}")
            bad.append(r["file"])
            continue
        status = "OK  " if r["coverage"] >= 99.9 else "WARN"
        if r["missing_required"]:
            status = "FAIL"
        if status == "OK  ":
            ok += 1
        if status != "OK  ":
            bad.append(r["file"])
        lines.append(
            f"\n[{status}] {r['file']}  覆盖 {r['covered']}/{r['total']} ({r['coverage']:.1f}%)"
            f"  uncertain={r['uncertain_count']}"
        )
        if r["missing"] and not args.quiet:
            lines.append(f"    缺失字段: {', '.join(r['missing'])}")
        if r["extra"] and not args.quiet:
            lines.append(f"    额外字段: {', '.join(r['extra'][:12])}")
        if r["missing_required"]:
            lines.append(f"    [必填缺失] {', '.join(r['missing_required'])}")

    lines.append("\n" + "=" * 68)
    lines.append(f"汇总: 通过 {ok}/{len(files)}")
    if bad:
        lines.append(f"待处理: {', '.join(bad)}")
    lines.append("=" * 68)

    report = "\n".join(lines)
    out_path = Path(args.out) if args.out else (topic / "_校验结果.txt")
    out_path.write_text(report, encoding="utf-8")

    # 只回传 ASCII 摘要，规避 shell 编码问题
    print(f"OUT={out_path}")
    print(f"FILES={len(files)} OK={ok} BAD={len(bad)}")
    print(f"FIELDS={len(all_fields)}")
    if bad:
        print(f"BADLIST={';'.join(bad)}")


if __name__ == "__main__":
    main()
