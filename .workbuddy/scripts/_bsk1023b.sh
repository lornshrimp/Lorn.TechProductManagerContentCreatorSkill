#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$PATH"
export BSK_AUTO_START=0
O="$TEMP/bsk1023"
mkdir -p "$O"
SID=ndbk

# 知微事见 滚动三轮
: > "$O/zhiwei.txt"
for i in 1 2 3 4; do
  bsk navigate --session "$SID" --wait-until load --timeout 60s "https://ef.zhiweidata.com/library" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 6000 >/dev/null 2>&1
  bsk evaluate --session "$SID" "window.scrollTo(0,1200*$i)" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 2500 >/dev/null 2>&1
  bsk evaluate --session "$SID" "document.body.innerText.slice(0,14000)" >> "$O/zhiwei.txt" 2>&1
  echo "" >> "$O/zhiwei.txt"
done
echo "[zhiwei] bytes=$(wc -c < "$O/zhiwei.txt")"

# InfoQ 首页热点
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.infoq.cn/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 5000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,900)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 2500 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a')).map(a=>(a.innerText||'').replace(/\s+/g,' ').trim()).filter(t=>t.length>12&&t.length<70).join('\n')" > "$O/infoq2.txt" 2>&1
echo "[infoq2] bytes=$(wc -c < "$O/infoq2.txt")"

# 澎湃 首页热榜
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.thepaper.cn/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 5000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,600)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 2000 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a[href*=\\\"newsDetail\\\"]')).map(a=>(a.innerText||'').replace(/\s+/g,' ').trim()).filter(t=>t.length>10&&t.length<70).join('\n')" > "$O/thepaper2.txt" 2>&1
echo "[thepaper2] bytes=$(wc -c < "$O/thepaper2.txt")"

# 百度指数 首页
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://index.baidu.com/v2/index.html#/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 4000 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.body.innerText.slice(0,1500)" > "$O/baidu_index.txt" 2>&1
echo "[baidu_index] bytes=$(wc -c < "$O/baidu_index.txt")"

echo "DONE2"
