"""チェーン店メニューの確認"""
import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
OUT='/home/claude/eiyo-keisan/src/.out'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,locale='ja-JP')
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(URL); await pg.click('#newRec')
        for q in ['すき家 牛丼 並','牛丼','ごはん 150','すき家 からあげ 2']:
            print(q,'=>',await pg.evaluate("q=>search(q).out.map(o=>o.ch!=null?extName(extOf(o.ch,o.mi)):o.dish||o.cu||dispName(o.idx))",q))
        await pg.fill('[data-add="new-1"]','すき家 牛丼 並'); await pg.wait_for_selector('[data-sug="new-1"] [data-pick]'); await pg.press('[data-add="new-1"]','Enter')
        await pg.click('[data-chopen="2"]'); await pg.wait_for_selector('dialog[open] #chq'); await pg.fill('#chq','とん汁'); await pg.wait_for_timeout(100)
        await pg.screenshot(path=f'{OUT}/chain-sheet.png')
        await pg.click('[data-chadd]'); print('msg',await pg.inner_text('#chMsg')); await pg.click('#done')
        print(await pg.evaluate("JSON.stringify(curDay().menus.map(m=>[m.meal,m.name,m.items.map(i=>[itemName(i),i.g,Math.round(calc(i).v[0])])]))"))
        await pg.locator('.swipe>.row').first.click(); await pg.wait_for_selector('dialog[open] #amt'); await pg.fill('#amt','0.5'); await pg.click('#done')
        await pg.click('#confirm'); await pg.screenshot(path=f'{OUT}/chain-result.png',full_page=True)
        print('total',await pg.evaluate("JSON.stringify(recAgg(curRec(),0).v.slice(0,6).map(x=>Math.round(x*10)/10))"),'ext note',await pg.evaluate("document.body.innerText.includes('公表値がないため0')"),'errors',errs)
        await b.close()
asyncio.run(main())
