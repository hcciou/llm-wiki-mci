import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg=await b.new_page(viewport={"width":1280,"height":720})
        await pg.goto("file:///mnt/user-data/outputs/index.html")
        n=await pg.evaluate("document.querySelectorAll('.slide').length")
        for k in range(n):

            if k>0: await pg.keyboard.press("ArrowRight")
            if k==7: await pg.keyboard.press("a")
            await pg.wait_for_timeout(150)
            # 溢出偵測：投影片內任何元素底部超過 696（保留頁尾），或右側超過 1240
            over=await pg.evaluate("""()=>{const s=document.querySelector('.slide.active');const r0=s.getBoundingClientRect();const sc=r0.width/1280;
              let out=[];s.querySelectorAll('*').forEach(e=>{if(e.closest('aside')||e.classList.contains('src')||e.classList.contains('pageno'))return;const r=e.getBoundingClientRect();if(!r.width)return;
              const b=(r.bottom-r0.top)/sc, rt=(r.right-r0.left)/sc; if(b>676||rt>1222) out.push(e.tagName+'.'+e.className+' b='+Math.round(b)+' r='+Math.round(rt)+' '+(e.textContent||'').slice(0,20));});return out.slice(0,5)}""")
            cur=await pg.evaluate("[...document.querySelectorAll('.slide')].findIndex(x=>x.classList.contains('active'))+1")
            print(k+1, "顯示第",cur,"頁", "OK" if not over else over)
            await pg.screenshot(path=f"/home/claude/check/s{k+1:02d}.png")
        await b.close()
asyncio.run(main())
