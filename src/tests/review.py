"""自分用モードの確認：体重とメモの記録、振り返り（週の平均・日ごとのエネルギー・体重の推移）、目標体重の欄がないこと、日ごとの同期の突き合わせ"""
import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
OUT='/home/claude/eiyo-keisan/src/.out'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for name,vp in [('phone',{'width':390,'height':844}),('desk',{'width':1200,'height':800})]:
            ctx=await b.new_context(viewport=vp,has_touch=name=='phone',is_mobile=name=='phone',locale='ja-JP')
            pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
            await pg.goto(URL)
            # 自分用モードにして、過去10日ぶんの食事・体重・メモを入れる
            await pg.evaluate("""()=>{S.mode='self';S.tab='day';V.screen='list';const t=dkey(new Date());
              for(let i=0;i<10;i++){const k=addDays(t,-i);if(i===3)continue;const d=S.me.days[k]=newDay();
                d.menus.push({n:S.seq++,meal:0,name:'',items:[{n:S.seq++,id:'01088',g:150+i*20,t:'a'},{n:S.seq++,id:'12004',g:50,t:'a'}]});
                if(i%2===0)d.w=Math.round((62-i*0.1+(i%4?0.3:0))*10)/10;if(i===1)d.memo='外食。夜おそくなった';}
              S.me.target={sex:'f',age:35,h:158,w:62,em:'tw',ef:28};fixS();V.date=t;save();render()}""")
            print(name,'tabs',await pg.evaluate("[...document.querySelectorAll('#tabs button')].map(b=>b.textContent)"),'target em',await pg.evaluate("S.me.target.em"))
            await pg.fill('#dw','61.4'); await pg.press('#dw','Tab'); await pg.fill('#dmemo','よく眠れた。昼は軽め'); await pg.press('#dmemo','Tab'); await pg.wait_for_timeout(100)
            print(name,'today',await pg.evaluate("JSON.stringify([meDay().w,meDay().memo,!!meDay().u])"))
            await pg.screenshot(path=f'{OUT}/rev-day-{name}.png',full_page=True)
            await pg.click('#setTarget'); print(name,'target methods',await pg.evaluate("[...document.querySelectorAll('#sheet input[name=em]')].map(i=>i.parentElement.textContent)"),'has 目標体重',await pg.evaluate("$('sheet').textContent.includes('目標体重')")); await pg.click('#cancel')
            await pg.click('#revOpen'); await pg.wait_for_timeout(100)
            txt=await pg.evaluate("document.querySelector('#view').innerText")
            print(name,'review',' | '.join([l for l in txt.split('\n') if l.strip()][:22])[:900])
            print(name,'svg',await pg.evaluate("[...document.querySelectorAll('#view svg')].map(s=>s.getAttribute('aria-label').slice(0,120))"),'overflow',await pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth"),'目標体重' in txt)
            await pg.screenshot(path=f'{OUT}/rev-{name}.png',full_page=True)
            await pg.click('label:has-text("3か月")'); await pg.click('#wPrev'); await pg.wait_for_timeout(100)
            print(name,'prev week',await pg.evaluate("document.querySelector('#view .inline .headline').textContent"),await pg.evaluate("[...document.querySelectorAll('#view .row')].slice(0,1).map(r=>r.innerText.replace(/\\n/g,' '))"))
            await pg.evaluate("document.querySelector('#view svg g[data-goday]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(100)
            print(name,'go day',await pg.evaluate("[V.screen,V.date===weekStart(V.date)]"))
            # 同期の突き合わせ：別の端末で別の日を変えても両方残る
            print(name,'merge',await pg.evaluate("""()=>{const t=dkey(new Date()),y=addDays(t,-1);const L=JSON.parse(JSON.stringify(S)),R=JSON.parse(JSON.stringify(S));
              L.me.days[t].w=60;L.me.days[t].u=Date.now()+5;L.updated=Date.now()+5;R.me.days[y].memo='相手側のメモ';R.me.days[y].u=Date.now()+9;R.updated=Date.now()+9;
              const m=Stamp.merge(L,R);return [m.me.days[t].w,m.me.days[y].memo]}"""),'errors',errs)
            await ctx.close()
        await b.close()
asyncio.run(main())
