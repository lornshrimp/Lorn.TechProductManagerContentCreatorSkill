# -*- coding: utf-8 -*-
"""实测正文字数：排除 frontmatter 与附属区（素材溯源/质量自检/标题决策/编辑终审），只计中文字符。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def body_chars(path, cut_markers=None):
    txt = open(path, encoding='utf-8').read()
    txt = re.sub(r'^---.*?---\n', '', txt, flags=re.S)
    if cut_markers is None:
        cut_markers = ['## 素材溯源表', '## 质量自检报告', '## 标题决策说明',
                       '## 编辑终审签报', '## 附', '[封面图提示词]', '[内容简介]',
                       '[配图1]', '[配图2]', '[配图3]', '## 配图搜索替换指令',
                       '## 互动引导', '## 发布建议', '## 知乎发布建议', '---']
    for cut in cut_markers:
        idx = txt.find(cut)
        if idx > 0:
            txt = txt[:idx]
            break
    txt = re.sub(r'[#*_>\-\[\]()|`=~]', '', txt)
    return len(re.findall(r'[\u4e00-\u9fff]', txt))

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, '->', body_chars(p), '字')
