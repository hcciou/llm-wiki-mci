#!/usr/bin/env python3
"""引用檢查 [1a]-自動段：逐行比對 Wiki 敘述與所引來源。
引用格式：〔S05 p.22〕、〔S02 p.3–4〕、〔S01 §START〕，一行可多個。
- 中文來源（S05）：中文二字詞重疊度
- 英文來源：該行出現的數字、英文術語必須出現在所引頁／節
輸出低分行，交給人工（含看圖）複核。用法：python3 tools/check_citations.py [Sxx ...]
"""
import re, subprocess, glob, sys
RAW = {
 "S01": "raw/01 - EMS Mass Casualty Triage (Archived).md",
 "S02": "raw/02 - aaem-10-e32.pdf",
 "S03": glob.glob("raw/03 - *.pdf")[0],
 "S04": glob.glob("raw/04 - *.pdf")[0],
 "S05": glob.glob("raw/05 - *.pdf")[0],
}
LANG = {"S05": "zh"}
SECT = {"introduction":"Introduction","issues":"Issues of Concern","clinical":"Clinical Significance",
        "start":"START Triage","salt":"SALT Triage","jumpstart":"JumpSTART"}
def norm(s): return re.sub(r"\s+", " ", s)
def pdf_pages(path):
    out = subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True).stdout
    return {i+1: norm(p) for i, p in enumerate(out.split("\f"))}
def md_sections(path):
    t = open(path, encoding="utf-8").read(); secs = {}; cur = "head"
    for ln in t.splitlines():
        m = re.match(r"^(?:##\s+|\*\*)(.+?)(?:\*\*)?\s*$", ln)
        if m and (ln.startswith("## ") or (ln.startswith("**") and ln.rstrip().endswith("**"))): cur = m.group(1).strip()
        secs[cur] = secs.get(cur, "") + " " + ln
    return {k: norm(v) for k, v in secs.items()}
cache = {}
def src_text(sid, loc):
    if sid not in cache:
        p = RAW[sid]; cache[sid] = md_sections(p) if p.endswith(".md") else pdf_pages(p)
    d = cache[sid]
    if loc.startswith("§"):
        out = []
        for part in re.split(r"[、,]\s*", loc):
            part = part.strip().lstrip("§").strip()
            key = SECT.get(part.lower(), part)
            out += [v for k, v in d.items() if key.lower() in k.lower()]
        return " ".join(out)
    ps = set()
    for part in re.findall(r"\d+(?:[–-]\d+)?", loc):
        a, _, b = re.split(r"([–-])", part)[0], None, None
        rng = re.split(r"[–-]", part); a = int(rng[0]); b = int(rng[-1])
        ps |= set(range(a, b+1))
    return " ".join(d.get(p, "") for p in ps)
CITE = re.compile(r"〔(S0\d) ((?:p\.|§)[^〕]+)〕")
def zh_score(body, src):
    s = re.sub(r"[^一-鿿]", "", body); src = re.sub(r"\s", "", src)
    bg = {s[i:i+2] for i in range(len(s)-1)}
    return (sum(g in src for g in bg)/len(bg)) if bg else 1.0, []
ALIAS = {"WHO": "World Health Organization", "MCI": "mass casualty", "MCIs": "mass casualty",
         "8": "eight", "5": "five", "4": "4", "2": "2"}
def en_score(body, src):
    body = re.sub(r"S0\d", "", body)                 # 來源代號
    body = re.sub(r"^\s*(?:[-*]|\d+\.)\s*", "", body)  # 清單編號
    body = re.sub(r"§\w+", "", body)
    # 引號內的中文翻譯不算；只取數字與英文 token
    nums = set(re.findall(r"\d+(?:\.\d+)?", body))
    words = {w for w in re.findall(r"[A-Za-z][A-Za-z\-]{2,}", body)} - {"Wiki"}
    def has(t): return t.lower() in src.lower() or (t in ALIAS and ALIAS[t].lower() in src.lower())
    miss = [n for n in nums if not has(n)] + [w for w in words if not has(w)]
    tot = len(nums) + len(words)
    return (1 - len(miss)/tot) if tot else 1.0, miss
only = set(sys.argv[1:])
n = low = 0
for f in sorted(g for g in glob.glob("wiki/**/*.md", recursive=True) if not g.endswith("log.md")):
    for i, ln in enumerate(open(f, encoding="utf-8"), 1):
        cites = CITE.findall(ln)
        if not cites: continue
        sids = {c[0] for c in cites}
        if only and not (sids & only): continue
        body = CITE.sub("", ln)
        body = re.sub(r"\[\[.*?\]\]", "", body)
        for sid in sids:
            if only and sid not in only: continue
            # 英文來源：同一行混引多個來源時，數字／術語可來自任一所引來源
            src = " ".join(src_text(s, loc) for s, loc in cites if s == sid or LANG.get(sid) != "zh")
            n += 1
            sc, miss = (zh_score if LANG.get(sid) == "zh" else en_score)(body, src)
            if sc < (0.45 if LANG.get(sid) == "zh" else 1.0):
                low += 1
                print(f"{sc:.2f} {sid} {f.split('/')[-1]}:{i} miss={miss[:6]} :: {ln.strip()[:80]}")
print(f"checked={n} flagged={low}")
