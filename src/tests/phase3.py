"""フェーズ3の確認：対象者ごとの一覧、前回との差、カルテ用の文、CSV、同期の突き合わせ、自動バックアップ"""
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
        async def add(key,text):
            await pg.fill(f'[data-add="{key}"]',text); await pg.wait_for_selector(f'[data-sug="{key}"] [data-pick]'); await pg.press(f'[data-add="{key}"]','Enter')
        await pg.click('#newRec'); await pg.fill('#rlabel','A-012'); await pg.press('#rlabel','Tab'); await pg.fill('#rdate','2026-09-01'); await pg.press('#rdate','Tab'); await add('new-0','ごはん 150')
        await pg.click('#confirm'); await pg.click('#setTarget'); await pg.fill('#t_w','50'); await pg.fill('#t_kk','30'); await pg.click('#done'); await pg.click('[data-back="edit"]'); await pg.click('[data-back="list"]')
        await pg.click('section:has-text("A-012") [data-again]'); await add('new-0','ごはん 200'); await add('new-1','焼き鮭 80'); await pg.click('#confirm'); await pg.click('#setTarget'); await pg.fill('#t_w','48'); await pg.click('#done')
        print(await pg.evaluate("JSON.stringify(S.records.map(r=>[r.id,r.label,r.date,r.example,recDate(r)]))"),await pg.evaluate("String(prevRec(curRec())&&prevRec(curRec()).id)"))
        sec=await pg.evaluate("[...document.querySelectorAll('#view section')].find(s=>s.textContent.includes('との差')).innerText.replace(/\\n/g,' | ')")
        print('prev:',sec)
        print('karte:\n'+await pg.evaluate("karteText()"))
        csv=await pg.evaluate("csvOfRecord()"); print('csv lines',len(csv.split('\r\n')),'|',csv.split('\r\n')[1][:120])
        await pg.screenshot(path=f'{OUT}/p3-result.png',full_page=True); print('overflow',await pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"))
        await pg.emulate_media(media='print'); await pg.screenshot(path=f'{OUT}/p3-print.png',full_page=True); await pg.emulate_media(media='screen')
        await pg.click('[data-back="edit"]'); await pg.click('[data-back="list"]'); await pg.screenshot(path=f'{OUT}/p3-list.png')
        print('list:',await pg.evaluate("[...document.querySelectorAll('#view section')].map(s=>s.innerText.replace(/\\n/g,' ')).join(' || ')"))
        # 同期の突き合わせ（2台で別々の記録を足しても両方残る／消した記録は戻らない）
        r=await pg.evaluate("""()=>{const base=JSON.parse(JSON.stringify(S));const A=JSON.parse(JSON.stringify(base)),B=JSON.parse(JSON.stringify(base));const now=Date.now();
          A.records.push({id:'rA',label:'A',created:now,u:now,days:[]});A.updated=now;B.records.push({id:'rB',label:'B',created:now+1,u:now+1,days:[]});B.records[0].label='changed';B.records[0].u=now+5;B.updated=now+5;
          const m=Stamp.merge(A,B);const ok1=['rA','rB'].every(id=>m.records.some(x=>x.id===id))&&m.records[0].label==='changed';
          const C=JSON.parse(JSON.stringify(m));C.records=C.records.filter(x=>x.id!=='rA');C.del={rA:now+10};const m2=Stamp.merge(C,m);return [ok1,!m2.records.some(x=>x.id==='rA'),m2.records.length]}""")
        print('merge both kept / delete wins / count:',r)
        await pg.click('[data-tab="set"]'); print('backup rows',await pg.locator('[data-bak]').count(),'karte box',await pg.locator('#karteT').count(),'errors',errs)
        await b.close()
asyncio.run(main())
