#!/usr/bin/env python3
"""Lint：孤兒頁、斷連結、frontmatter 與實際引用不符、無引用的事實行、未標記 LLM 補充、術語不一致、單一來源主張。"""
import re, glob, os
pages = {os.path.splitext(os.path.basename(f))[0]: f for f in glob.glob("wiki/**/*.md", recursive=True) if not f.endswith(("index.md","log.md"))}
text = {k: open(f, encoding="utf-8").read() for k, f in pages.items()}
index = open("wiki/index.md", encoding="utf-8").read()
links = {k: set(re.findall(r"\[\[(.+?)\]\]", t)) for k, t in text.items()}
inbound = {k: 0 for k in pages}
for k, ls in links.items():
    for l in ls:
        if l in inbound and l != k: inbound[l] += 1
print("== 斷連結（連到不存在的頁）")
for k, ls in links.items():
    for l in ls:
        if l not in pages: print(f"  {k} → [[{l}]]")
print("== 孤兒頁（沒有其他頁連進來）")
for k, n in inbound.items():
    if n == 0: print(f"  {k}")
print("== 未列入 index")
for k in pages:
    if f"[[{k}]]" not in index: print(f"  {k}")
print("== frontmatter sources 與內文引用不符")
for k, t in text.items():
    fm = set(re.findall(r"S0\d", re.search(r"sources: \[(.*?)\]", t).group(1)))
    used = set(re.findall(r"〔(S0\d) ", t))
    if fm != used: print(f"  {k}: frontmatter={sorted(fm)} 內文={sorted(used)}")
print("== 無引用的條列事實行（排除標題、相關、註記、LLM 補充、明示歸納）")
skip = ("相關", "[[", "LLM 補充", "歸納", "推論", "看圖", "待", "已解", "衝突", "不裁決", "簡報", "範圍", "⚠️", "檔案", "性質", "出處", "方法", "角色", "作者")
for k, t in text.items():
    body = t.split("---", 2)[-1]
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith(("- ", "| ", "1.", "2.", "3.", "4.", "5.")) and "〔S0" not in s and not s.startswith("|---") and not any(x in s for x in skip) and len(s) > 12:
            if s.startswith("| 系統") or s.startswith("| 研究") or s.startswith("| 顏色") or s.startswith("| ID") or s.startswith("| 頁面"): continue
            print(f"  {k}: {s[:70]}")
print("== 術語一致性")
for bad, good in [("頻死","瀕死"),("大量傷患事件","大量傷病患"),("過度檢傷","過度分類"),("低估檢傷","低估分類"),("檢傷分級","檢傷分類")]:
    for k, t in text.items():
        if bad in t and "錯字" not in t.split(bad)[1][:20] and "原文" not in t.split(bad)[0][-20:]:
            print(f"  {k}: 用了「{bad}」，應為「{good}」")
print("== 只有單一來源支撐的頁面")
for k, t in text.items():
    used = set(re.findall(r"〔(S0\d) ", t))
    if len(used) == 1 and not k.startswith("S0"): print(f"  {k}: 僅 {used.pop()}")
