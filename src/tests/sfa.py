"""飽和脂肪酸の確認：成分表（脂肪酸成分表編）の値で計算されること、収載値のない分の注記、脂質異常の表示、CSV・カルテ文"""
import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
OUT='/home/claude/eiyo-keisan/src/.out'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,locale='ja-JP')
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(URL)
        r=await pg.evaluate("""()=>{const one=c=>{const x=calc({id:c,g:100,t:'a'});return [c,+x.v[26].toFixed(2),+x.sx.toFixed(2)]};
          return {rows:['14017','11011','01088'].map(one),none:F.filter(f=>f[32]==null).length,all:F.length}}""")
        print(r); assert r['rows'][0][1]==50.45 and r['rows'][1][1]==19.81 and r['rows'][2][1]==0.1
        await pg.click('#newRec')
        await pg.fill('[data-add="new-0"]','ごはん 150、バター 10、すき家 牛丼 並盛'); await pg.wait_for_selector('[data-multi]'); await pg.press('[data-add="new-0"]','Enter'); await pg.wait_for_timeout(200)
        print(await pg.evaluate("JSON.stringify(curDay().menus[0].items.map(i=>[itemName(i),i.g,+calc(i).v[26].toFixed(2),+calc(i).sx.toFixed(1)]))"))
        await pg.click('#confirm'); await pg.select_option('#viewSel','lip')
        print('lip',await pg.evaluate("[...document.querySelectorAll('#view .cols .group')][0].innerText.replace(/\\n/g,' | ')"))
        print('note',await pg.evaluate("[...document.querySelectorAll('#view .cols .gfoot')][0].innerText.split('\\n').find(x=>x.includes('飽和脂肪酸'))"))
        print('overflow',await pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"))
        await pg.screenshot(path=f'{OUT}/sfa-lip.png',full_page=True)
        print('copy',[l for l in (await pg.evaluate("textOfRecord()")).split('\n') if '飽和脂肪酸' in l][0][:200])
        print('csv',(await pg.evaluate("csvOfRecord().split('\\n')[0]")).count('飽和脂肪酸'),'karte',await pg.evaluate("karteVars()['飽和脂肪酸']"),'errors',errs)
        await b.close()
asyncio.run(main())
