"""モード切り替えと自分用の食事記録の確認"""
import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
OUT='/home/claude/eiyo-keisan/src/.out'
async def run(b,name,vp,mobile):
    ctx=await b.new_context(viewport=vp,has_touch=mobile,is_mobile=mobile)
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    await pg.goto(URL)
    tabs=lambda: pg.evaluate("[...document.querySelectorAll('#tabs button')].map(b=>b.textContent)")
    print(name,'pro tabs',await tabs())
    await pg.click('[data-tab="set"]'); await pg.screenshot(path=f'{OUT}/mode-{name}-set.png')
    await pg.click('#modeSw'); await pg.wait_for_timeout(150)
    print(name,'loading shown',await pg.evaluate("!document.getElementById('modeLoad').hidden"),await pg.inner_text('#modeMsg'))
    await pg.screenshot(path=f'{OUT}/mode-{name}-load.png')
    await pg.wait_for_timeout(1000)
    print(name,'self tabs',await tabs(),'loading hidden',await pg.evaluate("document.getElementById('modeLoad').hidden"))
    async def add(key,text):
        await pg.fill(f'[data-add="{key}"]',text); await pg.wait_for_selector(f'[data-sug="{key}"] [data-pick]'); await pg.press(f'[data-add="{key}"]','Enter')
    await add('new-0','ごはん 150'); await add('new-1','うどん 250')
    await pg.click('#setTarget'); await pg.check('input[name="sex"][value="f"]',force=True); await pg.fill('#t_age','30'); await pg.fill('#t_w','50'); await pg.fill('#t_kk','30'); await pg.click('#done')
    print(name,'self day',await pg.evaluate("JSON.stringify([Object.keys(S.me.days).length,Math.round(dayAgg(curDay()).v[0]),target(curRec()).kcal,S.records.length])"))
    await pg.screenshot(path=f'{OUT}/mode-{name}-self.png',full_page=True)
    ov=await pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth")
    await pg.click('#confirm'); t=await pg.inner_text('h1'); await pg.click('[data-back="edit"]')
    await pg.click('#dPrev'); d1=await pg.evaluate("curDay().menus.length"); await pg.click('#dToday'); d2=await pg.evaluate("curDay().menus.length")
    print(name,'result title',t,'| prev day menus',d1,'today menus',d2,'overflow',ov)
    await pg.reload(); print(name,'after reload',await tabs(),await pg.evaluate("JSON.stringify([S.mode,Object.keys(S.me.days).length])"))
    await pg.click('[data-tab="set"]'); await pg.click('#modeSw'); await pg.wait_for_timeout(1100)
    print(name,'back to pro',await tabs(),await pg.evaluate("JSON.stringify([S.mode,S.tab,S.records.length,Object.keys(S.me.days).length])"),'errors',errs)
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        await run(b,'phone',{'width':390,'height':844},True); await run(b,'desk',{'width':1280,'height':800},False)
        await b.close()
asyncio.run(main())
