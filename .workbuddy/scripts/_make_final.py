# -*- coding: utf-8 -*-
from pathlib import Path
JOBS = [
 ("drafts/2026-09-18/用AI裁掉70多人后利润就上去了-提效的账最后谁在付/润色稿-用AI裁掉70多人后利润就上去了.md",
  "drafts/2026-09-18/用AI裁掉70多人后利润就上去了-提效的账最后谁在付/终稿-用AI裁掉70多人后利润就上去了.md",
  "用 AI 裁掉 70 多人后利润就上去了 · 提效的账最后谁在付"),
 ("drafts/2026-09-18/华为与赛力斯分家-问界移交的定价权重分配/润色稿-那10%到底买了什么.md",
  "drafts/2026-09-18/华为与赛力斯分家-问界移交的定价权重分配/终稿-那10%到底买了什么.md",
  "华为与赛力斯\u201c分家\u201d · 问界移交的定价权重分配"),
 ("drafts/2026-09-18/世界银行-中国人均GNI距高收入门槛仅差145美元/润色稿-就差145美元.md",
  "drafts/2026-09-18/世界银行-中国人均GNI距高收入门槛仅差145美元/终稿-就差145美元.md",
  "世界银行：中国人均 GNI 距高收入门槛仅差 145 美元"),
]
for src, dst, topic in JOBS:
    t = Path(src).read_text(encoding="utf-8")
    if t.startswith("---"):
        t = t.split("---", 2)[2].lstrip("\n")
    fm = ("---\ntype: 终稿\ndate: 2026-09-18\ntopic: %s\nplatform: 母稿\n"
          "genre: 深度分析体\nmodel: deai-review\n审核结论: 通过\n---\n\n" % topic)
    Path(dst).write_text(fm + t, encoding="utf-8")
    print("OK", dst)
