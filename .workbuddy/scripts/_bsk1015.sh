#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$PATH"
export BSK_AUTO_START=0
O="$TEMP/bsk1015"
mkdir -p "$O"
SID=$(bsk session start 2>&1 | grep -oE '[a-z0-9]{4,}' | tail -1)
echo "SESSION=$SID" | tee "$O/_sid.txt"

shot() { # name url js
  local n="$1" u="$2" js="$3"
  bsk navigate --session "$SID" --wait-until load --timeout 60s "$u" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 5000 >/dev/null 2>&1
  bsk evaluate --session "$SID" "$js" > "$O/$n.txt" 2>&1
  echo "[$n] bytes=$(wc -c < "$O/$n.txt" 2>/dev/null)"
}

# 1 知乎问题热榜（四元组）
shot zhihu_hot "https://www.zhihu.com/hot" "Array.from(document.querySelectorAll('.HotItem')).slice(0,30).map(el=>{const r=el.querySelector('.HotItem-rank');const m=el.querySelector('.HotItem-metrics');const a=el.querySelector('a[href*=\\\"/question/\\\"]');const t=a?(a.innerText||'').trim().split('\n')[0]:'';const h=a?a.getAttribute('href'):'';return (r?r.innerText.trim():'?')+'##'+(m?m.innerText.trim().split('\n')[0]:'?')+'##'+t+'##'+h}).join('\n')"

# 2 知乎推荐问题 4 轮
: > "$O/zhihu_recommend.txt"
for i in 1 2 3 4; do
  bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.zhihu.com/creator/featured-question/recommend" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 4500 >/dev/null 2>&1
  bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a[href*=\\\"/question/\\\"]')).map(a=>(a.innerText||'').trim()+'##'+a.getAttribute('href')).filter(x=>x.split('##')[0].length>8).slice(0,25).join('\n')" >> "$O/zhihu_recommend.txt" 2>&1
  echo "" >> "$O/zhihu_recommend.txt"
  bsk evaluate --session "$SID" "window.scrollTo(0,document.body.scrollHeight)" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 2000 >/dev/null 2>&1
done
echo "[zhihu_recommend] bytes=$(wc -c < "$O/zhihu_recommend.txt")"

# 3 知乎邀请问题 3 轮
: > "$O/zhihu_invited.txt"
for i in 1 2 3; do
  bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.zhihu.com/creator/featured-question/invited" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 4500 >/dev/null 2>&1
  bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a[href*=\\\"/question/\\\"]')).map(a=>(a.innerText||'').trim()+'##'+a.getAttribute('href')).filter(x=>x.split('##')[0].length>8).slice(0,25).join('\n')" >> "$O/zhihu_invited.txt" 2>&1
  echo "" >> "$O/zhihu_invited.txt"
done
echo "[zhihu_invited] bytes=$(wc -c < "$O/zhihu_invited.txt")"

# 4 知乎想法话题
shot zhihu_idea "https://www.zhihu.com/creator/creative-inspiration/idea-topics" "document.body.innerText.slice(0,5000)"

# 5 知乎想法热榜
shot zhihu_pin "https://www.zhihu.com/pin/hot" "document.title+'##'+location.href+'##'+document.body.innerText.slice(0,600)"

# 6 微博热搜
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://s.weibo.com/top/summary" >/dev/null 2>&1
bsk wait-ms --session "$SID" 5000 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.title+'###'+location.href" > "$O/weibo_meta.txt" 2>&1
bsk get-html --session "$SID" > "$O/weibo.html" 2>&1
echo "[weibo] html=$(wc -c < "$O/weibo.html")"

# 7 B站排行榜
shot bilibili "https://www.bilibili.com/ranking" "Array.from(document.querySelectorAll('a[href*=\\\"/video/\\\"]')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>6&&t.length<70).slice(0,40).join('\n')"

# 8 抖音热点
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://www.douyin.com/hot" >/dev/null 2>&1
bsk wait-ms --session "$SID" 9000 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.body.innerText.slice(0,6000)" > "$O/douyin.txt" 2>&1
echo "[douyin] bytes=$(wc -c < "$O/douyin.txt")"

# 9 知微事见
shot zhiwei "https://ef.zhiweidata.com/library" "document.body.innerText.slice(0,9000)"

# 10 虎嗅
shot huxiu "https://www.huxiu.com/" "Array.from(document.querySelectorAll('a[href*=\\\"/article/\\\"]')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>8&&t.length<60).slice(0,30).join('\n')"

# 11 InfoQ
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.infoq.cn/hotlist?tag=day" >/dev/null 2>&1
bsk wait-ms --session "$SID" 4000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,document.body.scrollHeight)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 3000 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>10&&t.length<80).slice(0,40).join('\n')" > "$O/infoq.txt" 2>&1
echo "[infoq] bytes=$(wc -c < "$O/infoq.txt")"

# 12 品玩
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.pingwest.com/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 4000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,document.body.scrollHeight)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 2500 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a[href*=\\\"/a/\\\"]')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>8&&t.length<60).slice(0,30).join('\n')" > "$O/pingwest.txt" 2>&1
echo "[pingwest] bytes=$(wc -c < "$O/pingwest.txt")"

# 13 百度指数
shot baidu_index "https://index.baidu.com/v2/index.html#/" "document.title+'###'+document.body.innerText.slice(0,1500)"

# 14 小红书（WebSearch 兜底源，标待适配）
shot xhs "https://www.xiaohongshu.com/explore" "document.title+'###'+document.body.innerText.slice(0,2000)"

echo "ALL_DONE SESSION=$SID"

