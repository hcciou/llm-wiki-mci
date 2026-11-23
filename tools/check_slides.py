#!/usr/bin/env python3
"""[4a] 事實回溯：簡報內容稿每一點 → 所標 Wiki 頁。
列出：(1) 數字不在 Wiki 頁；(2) 中文雙字詞重疊度低；(3) Wiki 頁找不到的新詞（供人工判斷是否為來源外內容）。
標「（示例）」的行只檢查數字門檻是否與 START 一致，不檢查重疊。"""
import re, glob, os, sys
def load(f):
    # 「LLM 補充・未驗證」的行不得作為簡報依據
    return "\n".join(l for l in open(f, encoding="utf-8") if "LLM 補充" not in l)
wiki = {os.path.splitext(os.path.basename(f))[0]: load(f) for f in glob.glob("wiki/**/*.md", recursive=True)}
STOP = set("的了是在和與或而但也都就要會能有沒不一個這那些先後再才只更最很如果所以因為以及其中可以已經還是比較依據")
def bigrams(s):
    s = re.sub(r"[^一-鿿]", "", s); return [s[i:i+2] for i in range(len(s)-1)]
cur = None; flagged = 0; n = 0
for ln in open(sys.argv[1] if len(sys.argv) > 1 else "slides/content.md", encoding="utf-8"):
    m = re.match(r"^## (\d+)", ln)
    if m: cur = m.group(1); continue
    refs = re.findall(r"【(.+?)】", ln)
    if not refs or not ln.strip().startswith("-"): continue
    n += 1
    body = re.sub(r"【.+?】", "", ln).strip("- \n")
    src = " ".join(wiki.get(r, "") for r in refs)
    missing_pages = [r for r in refs if r not in wiki]
    nums = [x for x in re.findall(r"\d+(?:\.\d+)?", body) if x not in src]
    bg = bigrams(body); srcz = re.sub(r"\s", "", src)
    new = [g for g in bg if g not in srcz and not (set(g) & STOP)]
    score = (1 - len(new)/len(bg)) if bg else 1
    example = "（示例）" in body
    issues = []
    if missing_pages: issues.append(f"頁不存在={missing_pages}")
    if nums and not example: issues.append(f"數字不在Wiki={nums}")
    if not example and score < 0.75: issues.append(f"新詞={sorted(set(new))[:12]}")
    if issues:
        flagged += 1; print(f"[{cur}] {score:.2f} {'; '.join(issues)}\n     {body[:80]}")
print(f"checked={n} flagged={flagged}")
