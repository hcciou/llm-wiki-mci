import re,sys,html
md=open(sys.argv[1],encoding="utf-8").read(); h=open(sys.argv[2],encoding="utf-8").read()
# HTML 可見文字＋講者備註
t=re.sub(r"<script.*?</script>|<style.*?</style>","",h,flags=re.S)
t=html.unescape(re.sub(r"<[^>]+>","",t))
norm=lambda s: re.sub(r"[\s*「」（）()：:；;，,。、…→|｜—\-]","",s)
T=norm(t)
miss=0;n=0
for ln in md.splitlines():
    if not ln.startswith("- "): continue
    b=re.sub(r"【.+?】","",ln[2:]).replace("（示例）","").replace("（歸納）","").replace("（台灣教材）","台灣教材")
    b=re.sub(r"^講者備註：","",b); b=b.replace("**","")
    if b.startswith(("標題：","副標：","講者：","答案頁：","參考資料：")): b=b.split("：",1)[1]
    n+=1
    if norm(b) not in T:
        # 允許拆成多段：檢查 8 字以上片段覆蓋率
        segs=[s for s in re.split(r"[；;，,：:→（）()]",b) if len(norm(s))>=4]
        bad=[s for s in segs if norm(s) not in T]
        if bad: miss+=1; print("MISSING:",b[:70],"\n   片段：",bad)
print(f"bullets={n} missing={miss}")
