"""フェーズ4の確認：提供食×喫食割合、経腸栄養剤・輸液の合算、寿司"""
import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
OUT='/home/claude/eiyo-keisan/src/.out'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,locale='ja-JP')
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(URL); await pg.click('[data-tab="my"]')
        await pg.click('#newDiet'); await pg.fill('#d_name','常食 昼'); await pg.fill('#d_main0','250'); await pg.fill('#d_main1','4'); await pg.fill('#d_side0','350'); await pg.fill('#d_side1','20'); await pg.fill('#d_side5','2.5'); await pg.screenshot(path=f'{OUT}/p4-diet.png'); await pg.click('#done')
        await pg.click('#newCu'); await pg.fill('#c_name','経腸栄養剤X'); await pg.click('dialog label:has-text("100 mLあたり")'); await pg.fill('#c_v0','100'); await pg.fill('#c_v1','4'); await pg.fill('#c_v20','85'); await pg.click('dialog label:has-text("経腸栄養")'); await pg.click('#done')
        await pg.screenshot(path=f'{OUT}/p4-my.png',full_page=True)
        await pg.click('[data-tab="rec"]'); await pg.click('#newRec')
        await pg.fill('[data-add="new-1"]','常食'); await pg.wait_for_selector('[data-sug="new-1"] [data-pick]'); await pg.press('[data-add="new-1"]','Enter'); await pg.wait_for_selector('#pvM'); await pg.select_option('#pvM','0.5'); await pg.select_option('#pvS','0.8'); await pg.screenshot(path=f'{OUT}/p4-sheet.png'); await pg.click('#done')
        async def add(key,text):
            await pg.fill(f'[data-add="{key}"]',text); await pg.wait_for_selector(f'[data-sug="{key}"] [data-pick]'); await pg.press(f'[data-add="{key}"]','Enter')
        await add('new-2','経腸栄養剤X 400'); await add('new-0','寿司 8貫')
        print(await pg.evaluate("JSON.stringify(curDay().menus.map(m=>m.items.map(i=>[itemName(i),itemAmount(i),Math.round(calc(i).v[0]),Math.round(calc(i).v[1]*10)/10])))"))
        await pg.click('#confirm')
        print('route:',await pg.evaluate("[...document.querySelectorAll('#view section')].find(s=>s.textContent.includes('投与経路別')).innerText.replace(/\\n/g,' | ')"))
        print('total',await pg.evaluate("JSON.stringify(recAgg(curRec(),0).v.slice(0,2).map(x=>Math.round(x*10)/10))"),'overflow',await pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"))
        await pg.screenshot(path=f'{OUT}/p4-result.png',full_page=True)
        print('karte',await pg.evaluate("karteText().split('\\n').slice(-5).join(' // ')"),'errors',errs)
        await b.close()
asyncio.run(main())
