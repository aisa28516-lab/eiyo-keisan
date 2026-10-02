"""冷蔵庫タブの確認"""
import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
OUT='/home/claude/eiyo-keisan/src/.out'
async def run(b,name,vp,mobile):
    ctx=await b.new_context(viewport=vp,has_touch=mobile,is_mobile=mobile,locale='ja-JP')
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    await pg.goto(URL); await pg.click('[data-tab="set"]'); await pg.click('#modeSw'); await pg.wait_for_timeout(1100)
    await pg.click('[data-tab="fr"]')
    await pg.fill('[data-add="fridge"]','キャベツ 300'); await pg.wait_for_selector('[data-sug="fridge"] [data-pick]'); await pg.press('[data-add="fridge"]','Enter')
    await pg.fill('[data-add="fridge"]','牛乳'); await pg.wait_for_selector('[data-sug="fridge"] [data-pick]'); await pg.press('[data-add="fridge"]','Enter')
    await pg.wait_for_selector('dialog[open] #amt'); await pg.fill('#amt','500'); await pg.click('[data-fuse="3"]'); await pg.screenshot(path=f'{OUT}/fridge-{name}-sheet.png'); await pg.click('#done')
    await pg.fill('#fIn','鶏むね肉 250 | 2026-01-05\nたまご 6個\nにんじん 2本\nうどん 2玉\nなぞの食べ物 100\n豚こま 200 | あした')
    await pg.click('#fImp')
    print(name,'msg:',await pg.inner_text('#fMsg'))
    print(name,'left in box:',repr(await pg.input_value('#fIn')))
    print(name,await pg.evaluate("JSON.stringify(S.fridge.map(x=>[itemName(x),x.g,x.pl||'',x.use,x.t]))"))
    print(name,'sections',await pg.evaluate("[...document.querySelectorAll('#view .ghead span:first-child')].map(e=>e.textContent)"))
    await pg.screenshot(path=f'{OUT}/fridge-{name}.png',full_page=True)
    ov=await pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth")
    n0=await pg.evaluate("S.fridge.length"); await pg.locator('.swipe>.row').first.click(); await pg.click('#del'); n1=await pg.evaluate("S.fridge.length")
    await pg.reload(); await pg.click('[data-tab="day"]')
    await pg.fill('[data-add="new-0"]','ごはん 150'); await pg.wait_for_selector('[data-sug="new-0"] [data-pick]'); await pg.press('[data-add="new-0"]','Enter')
    print(name,'delete',n0,'->',n1,'after reload',await pg.evaluate("S.fridge.length"),'meal ok',await pg.evaluate("curDay().menus[0].items[0].t"),'overflow',ov,'errors',errs)
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        await run(b,'phone',{'width':390,'height':844},True); await run(b,'desk',{'width':1280,'height':800},False)
        await b.close()
asyncio.run(main())
