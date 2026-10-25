# -*- coding: utf-8 -*-
import re
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"
r = (D/"润色稿-限量这本账.md").read_text(encoding="utf-8")
body = r
for mk in ["## 素材溯源表","## 视觉与配图","## 配图搜索替换指令"]:
    if mk in body: body = body.split(mk)[0]
out=[]
# 敏感词
sens=["围堵","封堵","脱钩","倒戈","打压","制裁","霸权","敌对","殖民","掠夺","崩溃","崩盘","失业潮","倒闭潮","血洗","收割","割韭菜","灭亡","溃败","投降","阴谋"]
hit=[s for s in sens if s in body]
out.append(f"敏感词命中: {hit if hit else '0 处'}")
# 占位符
ph=re.findall(r"\{[^}\n]{1,30}\}", r)
out.append(f"未替换占位符: {ph if ph else '0 处'}")
# 段落行数（手机端 >6 行）
paras=[p.strip() for p in body.split("\n\n") if p.strip()]
long_rows=[]
for i,p in enumerate(paras,1):
    cn=len(re.findall(r"[\u4e00-\u9fff]",p))
    if cn>200: long_rows.append((i,cn))
out.append(f"段落中文字符>200 的段: {long_rows if long_rows else '0 处'}")
# 第一人称
for w in ["我","你","我们","咱们"]:
    out.append(f"\"{w}\" 出现 {body.count(w)} 次（密度 {body.count(w)/len(re.findall(r'[一-鿿]',body))*1000:.2f}/千字）")
# 不是..而是 家族
fam=re.findall(r"不是[^。！？\n]{1,25}而是", body)
out.append(f"\"不是…而是\"家族: {len(fam)} 处 {fam}")
# 路标
for w in ["首先","其次","最后","此外","同时","并且","综上","因此","然而"]:
    c=body.count(w)
    if c: out.append(f"路标词 \"{w}\": {c} 次")
# 假深刻收尾
fake=re.findall(r"很[一二三四五六七八九十]?[^，。]{1,6}，也很[^。]{1,8}", body)
out.append(f"\"很A，也很B\"式收尾: {len(fake)} 处 {fake}")
# 硬伤扫描：企业负面/人身攻击
out.append(f"含\"骗子/黑心/无良\": {sum(body.count(x) for x in ['骗子','黑心','无良','流氓','强盗'])} 处")
Path(str(ROOT/".workbuddy"/"_chk_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print("done")
