#!/usr/bin/env bash
# 采集知乎推荐/邀请问题（标题##链接 成对），用于回填 hotspot/榜单 链接列
PY="C:/Users/lorns/.workbuddy/binaries/python/versions/3.13.12/python.exe"
BASE="D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/测试"
OUT="$BASE/bsk_scrape3.txt"
TMP="$BASE/_sid.json"
JS='Array.from(document.querySelectorAll("a[href*=\"/question/\"]")).map(a=>(a.innerText||"").trim()+"##"+a.getAttribute("href")).filter(x=>x.split("##")[0].length>8).slice(0,25).join("\n")'

bsk session stop --all >/dev/null 2>&1
bsk session start --json > "$TMP" 2>/dev/null
SID=$("$PY" -c "import re;d=open(r'$TMP',encoding='utf-8',errors='ignore').read();m=re.search(r'session_id[^a-z0-9]*([a-z0-9]+)',d);print(m.group(1) if m else '')")

{
echo "SID=$SID"
echo "=== NAV RECOMMEND ==="
bsk navigate --session "$SID" --wait-until load "https://www.zhihu.com/creator/featured-question/recommend"
bsk wait-ms 5000
echo "=== URL1 ==="
bsk evaluate --session "$SID" "location.href"
echo "=== TITLE1 ==="
bsk evaluate --session "$SID" "document.title"
echo "=== EVAL RECOMMEND ==="
bsk evaluate --session "$SID" "$JS"
echo "=== NAV INVITED ==="
bsk navigate --session "$SID" --wait-until load "https://www.zhihu.com/creator/featured-question/invited"
bsk wait-ms 5000
echo "=== URL2 ==="
bsk evaluate --session "$SID" "location.href"
echo "=== TITLE2 ==="
bsk evaluate --session "$SID" "document.title"
echo "=== EVAL INVITED ==="
bsk evaluate --session "$SID" "$JS"
echo "=== DONE ==="
} > "$OUT" 2>&1

bsk session stop --all >/dev/null 2>&1
echo finished
