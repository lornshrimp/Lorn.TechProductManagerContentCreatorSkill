import json, yaml, os, sys

base = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\research\车市价格带断裂-购车能力退出"
d0 = yaml.safe_load(open(os.path.join(base, "fields.yaml"), encoding="utf-8"))
fields = d0["fields"]
req = list(fields.keys())

print("fields.yaml section与叶子字段数:", {k: len([x["name"] for x in v]) for k, v in fields.items()})
print("-" * 60)

allok = True
files = ["item_E1.json", "item_E2.json", "item_E3.json", "item_E4.json", "item_E7.json",
         "item_C1.json", "item_C2.json", "item_C3.json", "item_B5.json"]
for f in files:
    p = os.path.join(base, "results", f)
    if not os.path.exists(p):
        print("[缺失]", f)
        allok = False
        continue
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print("[JSON解析失败]", f, e)
        allok = False
        continue
    miss_sec = [s for s in req if s not in d]
    miss = []
    for sec, items in fields.items():
        for it in items:
            if it["name"] not in d.get(sec, {}):
                miss.append(sec + "." + it["name"])
    ok = (not miss_sec) and (not miss)
    allok = allok and ok
    tag = "[通过] " if ok else "[未通过] "
    print(tag + f)
    print("   缺section:", miss_sec or "无")
    print("   缺叶子字段:", miss or "无")
    print("   uncertain:", ("有, %d项" % len(d.get("uncertain", []))) if "uncertain" in d else "缺失!")

print("-" * 60)
print("全部通过" if allok else "存在缺漏")
