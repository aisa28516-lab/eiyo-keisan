"""フェーズ0〜1の確認：取り消し、まとめて追加、覚える目安量、食べた割合、複製"""
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
        items=lambda: pg.evaluate("JSON.stringify(curDay().menus.map(m=>[m.meal,m.items.map(i=>[itemName(i),i.g,i.pl||'',i.fr==null?1:i.fr])]))")
        # まとめて追加
        await pg.fill('[data-add="new-0"]','ごはん 茶碗1杯、味噌汁 1杯、卵 1個, コロッケ 1個'); await pg.wait_for_selector('[data-multi]'); await pg.screenshot(path=f'{OUT}/p1-multi.png')
        await pg.press('[data-add="new-0"]','Enter'); await pg.wait_for_timeout(200)
        mn=await pg.evaluate("curDay().menus[0].n")
        print('multi',await items()); print('left:',repr(await pg.input_value(f'[data-add="{mn}"]')),'|',await pg.inner_text(f'[data-st="{mn}"]'))
        await pg.fill(f'[data-add="{mn}"]','')
        # 覚える目安量：コロッケ 1個 → 100 g を入れて完了
        n=await pg.evaluate("curDay().menus[0].items.find(i=>i.g==null).n"); await pg.click(f'[data-edit="{n}"]'); await pg.wait_for_selector('#learnP'); await pg.fill('#amt','100'); await pg.screenshot(path=f'{OUT}/p1-learn.png'); await pg.click('#done')
        print('learned',await pg.evaluate("JSON.stringify(S.portions)"),await pg.evaluate("q=>{const R=search(q);return JSON.stringify(resolveQty(R.P.qty,R.out[0].idx))}",'コロッケ 2個'))
        # 食べた割合 30%
        n0=await pg.evaluate("curDay().menus[0].items[0].n"); await pg.click(f'[data-edit="{n0}"]'); await pg.evaluate("(a=>{const r=document.querySelector(a[0]);r.value=a[1];r.dispatchEvent(new Event('input',{bubbles:true}));r.dispatchEvent(new Event('change',{bubbles:true}))})",['#frR',30]); await pg.click('#done')
        print('fr',await pg.evaluate("[curDay().menus[0].items[0].fr,Math.round(calc(curDay().menus[0].items[0]).v[0])]"),await pg.inner_text(f'[data-edit="{n0}"]'))
        # 取り消し
        c0=await pg.evaluate("curDay().menus[0].items.length"); await pg.click(f'[data-edit="{n0}"]'); await pg.click('#del'); c1=await pg.evaluate("curDay().menus[0].items.length")
        await pg.screenshot(path=f'{OUT}/p1-undo.png'); await pg.click('#undoBtn'); c2=await pg.evaluate("curDay().menus[0].items.length")
        await pg.click('#delRec'); await pg.click('[data-a="0"]'); r1=await pg.evaluate("S.records.length"); await pg.click('#undoBtn'); r2=await pg.evaluate("S.records.length")
        print('undo row',c0,c1,c2,'record',r1,r2)
        # 複製
        await pg.click('[data-open]:first-child'); 
        await pg.click('[data-mdup]'); m1=await pg.evaluate("curDay().menus.length")
        await pg.click('#dupOpen'); await pg.screenshot(path=f'{OUT}/p1-dup.png'); await pg.click('[data-dupmeal="0-2"]'); await pg.click('#dupDay')
        print('dup menus',m1,await pg.evaluate("JSON.stringify(curRec().days.map(d=>d.menus.map(m=>m.meal)))"),'ids unique',await pg.evaluate("(()=>{const a=curRec().days.flatMap(d=>d.menus.flatMap(m=>[m.n,...m.items.map(i=>i.n)]));return new Set(a).size===a.length})()"))
        await pg.screenshot(path=f'{OUT}/p1-edit.png',full_page=True)
        print('overflow',await pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"),'errors',errs)
        await b.close()
asyncio.run(main())
