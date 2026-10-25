#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$PATH"
export BSK_AUTO_START=0
O="$TEMP/bsk1008"
SID=$(bsk session start 2>&1 | grep -oE '[a-z0-9]{4,}' | tail -1)
echo "SESSION2=$SID" | tee "$O/_sid2.txt"

# InfoQ 重试（首页编辑精选兜底）
bsk navigate --session "$SID" --wait-until load --timeout 70s "https://www.infoq.cn/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 5000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,1800)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 3000 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>10&&t.length<90).slice(0,40).join('\\n')" > "$O/infoq2.txt" 2>&1
echo "[infoq2] bytes=$(wc -c < "$O/infoq2.txt")"

# 抖音重试
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://www.douyin.com/hot" >/dev/null 2>&1
bsk wait-ms --session "$SID" 11000 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('div,span,a')).map(e=>(e.innerText||'').trim()).filter(t=>t&&t.length>6&&t.length<45).slice(0,70).join('\\n')" > "$O/douyin2.txt" 2>&1
echo "[douyin2] bytes=$(wc -c < "$O/douyin2.txt")"

echo "DONE2 SESSION=$SID"
