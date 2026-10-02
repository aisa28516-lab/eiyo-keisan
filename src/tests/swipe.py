"""行のスワイプ削除の確認（タッチ操作をCDPで再現）"""
import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.click('[data-open]')
        cdp=await ctx.new_cdp_session(pg)
        async def swipe(sel,dx):
            bx=await pg.locator(sel).first.bounding_box(); x=bx['x']+bx['width']/2; y=bx['y']+bx['height']/2
            await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
            for i in range(1,11):
                await cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+dx*i/10,'y':y}]})
            await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            await pg.wait_for_timeout(400)
        n0=await pg.locator('.swipe').count()
        await swipe('.swipe>.row',-120)
        print('left open:',await pg.locator('.swipe.open-l').count(),'sheet:',await pg.locator('dialog[open]').count())
        await pg.screenshot(path='/home/claude/eiyo-keisan/src/.out/swipe-left.png')
        await pg.locator('.swipe.open-l .swdel.t').tap(); await pg.wait_for_timeout(200)
        n1=await pg.locator('.swipe').count(); print('rows',n0,'->',n1)
        await swipe('.swipe>.row',120)
        print('right open:',await pg.locator('.swipe.open-r').count())
        await pg.screenshot(path='/home/claude/eiyo-keisan/src/.out/swipe-right.png')
        await pg.locator('.swipe>.row').nth(1).tap(); await pg.wait_for_timeout(400)
        print('after tap elsewhere open:',await pg.locator('.swipe.open-r').count(),'sheet:',await pg.locator('dialog[open]').count())
        assert await pg.locator('dialog[open]').count()==0
        await swipe('.swipe>.row',-30)
        print('short swipe open:',await pg.locator('.swipe.open-l,.swipe.open-r').count())
        await pg.locator('.swipe>.row').first.tap(); await pg.wait_for_timeout(300)
        print('tap opens sheet:',await pg.locator('dialog[open]').count(),'errors',errs)
        await b.close()
asyncio.run(main())
