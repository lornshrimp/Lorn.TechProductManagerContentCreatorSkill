#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
D="$TEMP/collect"
mkdir -p "$D"
rm -f "$D"/*.txt "$D"/*.html

S=$(bsk session start 2>/dev/null < /dev/null | grep -E '^[a-z]{4}$' | head -1)
echo "SESSION=$S"
if [ -z "$S" ]; then S=$(bsk session start 2>/dev/null < /dev/null | tail -1); echo "SESSION2=$S"; fi

n() { bsk navigate --session $S --wait-until load --timeout 40s "$1" > "$D/$2.nav.txt" 2>&1 < /dev/null; }
ev() { bsk evaluate --session $S "$1" > "$D/$2.txt" 2>&1 < /dev/null; }

n "https://www.zhihu.com/hot" zhihu_hot
ev 'Array.from(document.querySelectorAll(".HotItem")).slice(0,25).map(el=>{const r=el.querySelector(".HotItem-rank");const m=el.querySelector(".HotItem-metrics");const a=el.querySelector("a[href*=\"/question/\"]");const t=a?(a.innerText||"").trim().split("\n")[0]:"";const h=a?a.getAttribute("href"):"";return (r?r.innerText.trim():"?")+"##"+(m?m.innerText.trim().split("\n")[0]:"?")+"##"+t+"##"+h}).join("\n")' zhihu_hot

n "https://www.zhihu.com/creator/featured-question/recommend" zhihu_rec
ev 'Array.from(document.querySelectorAll("a[href*=\"/question/\"]")).map(a=>{const t=(a.innerText||"").trim().replace(/\n+/g," ");return (t.length>6&&t.length<90)?(t+"##"+a.getAttribute("href")):""}).filter(x=>x).filter((v,i,arr)=>arr.indexOf(v)===i).slice(0,20).join("\n")' zhihu_rec

n "https://www.zhihu.com/creator/featured-question/invited" zhihu_inv
ev 'Array.from(document.querySelectorAll("a[href*=\"/question/\"]")).map(a=>{const t=(a.innerText||"").trim().replace(/\n+/g," ");return (t.length>6&&t.length<90)?(t+"##"+a.getAttribute("href")):""}).filter(x=>x).filter((v,i,arr)=>arr.indexOf(v)===i).slice(0,20).join("\n")' zhihu_inv

n "https://www.zhihu.com/creator/creative-inspiration/idea-topics" zhihu_idea
ev 'document.body.innerText.slice(0,4000)' zhihu_idea

n "https://www.zhihu.com/pin/hot" zhihu_pin
ev 'document.body.innerText.slice(0,1500)' zhihu_pin

n "https://s.weibo.com/top/summary" weibo
bsk get-html --session $S > "$D/weibo.html" 2>/dev/null < /dev/null

n "https://top.baidu.com/board?tab=realtime" baidu
ev 'document.body.innerText.slice(0,4000)' baidu

n "https://www.toutiao.com/?channel=hot" toutiao
ev 'document.body.innerText.slice(0,4000)' toutiao

n "https://www.bilibili.com/ranking" bilibili
ev 'Array.from(document.querySelectorAll(".rank-item")).slice(0,30).map(el=>{const t=el.querySelector(".title");const pt=el.querySelector(".pts");return (t?t.innerText.trim():"")+"##"+(pt?pt.innerText.trim().replace(/\s+/g," "):"")}).join("\n")' bilibili

n "https://www.douyin.com/hot" douyin
ev 'Array.from(document.querySelectorAll("a")).map(a=>a.innerText.trim()).filter(t=>t&&t.length>4&&t.length<45).filter((v,i,arr)=>arr.indexOf(v)===i).slice(0,60).join("\n")' douyin

n "https://index.baidu.com/v2/index.html#/" baidu_index
ev 'document.body.innerText.slice(0,3000)' baidu_index

n "https://ef.zhiweidata.com/library" zhiwei
ev 'document.body.innerText.slice(0,7000)' zhiwei

bsk session stop $S < /dev/null > /dev/null 2>&1
echo "DONE_BATCH1 session=$S"
