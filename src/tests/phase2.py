"""フェーズ2の確認：PFCの方式、内訳、確からしさ、目標体重、表示の切り替え、追加の栄養素、定番料理"""
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
        await pg.fill('[data-add="new-0"]','ごはん 150、味噌汁 1杯、焼き鮭 80、ビール 350ml、野菜ジュース 200ml、ラーメン 200'); await pg.wait_for_selector('[data-multi]'); await pg.press('[data-add="new-0"]','Enter'); await pg.wait_for_timeout(200)
        print(await pg.evaluate("JSON.stringify(curDay().menus[0].items.map(i=>[itemName(i),i.g,!!i.tmp,i.pn||'',Math.round(calc(i).v[0])]))"))
        await pg.click('#confirm')
        ov=lambda: pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth")
        print('warn',await pg.evaluate("[...document.querySelectorAll('#view section')].find(s=>s.textContent.includes('確認が必要な点')).innerText.replace(/\\n/g,' / ')"))
        v=await pg.evaluate("JSON.stringify((()=>{const a=recAgg(curRec(),0).v;S.pfc='h8';const h=pfcOf(a).map(x=>Math.round(x*10)/10);S.pfc='old';const o=pfcOf(a).map(x=>Math.round(x*10)/10);S.pfc='h8';return {kcal:Math.round(a[0]),P:[a[1],a[24]].map(x=>Math.round(x*10)/10),F:[a[2],a[25]].map(x=>Math.round(x*10)/10),water:Math.round(a[20]),alc:Math.round(a[21]*10)/10,vk:Math.round(a[22]),cho:Math.round(a[23]*10)/10,h8:h,old:o}})())")
        print(v)
        await pg.click('#setTarget'); await pg.click('dialog label:has-text("女性")'); await pg.fill('#t_age','70'); await pg.fill('#t_h','150'); await pg.fill('#t_w','45'); await pg.click('dialog label:has-text("目標体重")'); await pg.fill('#t_bmi','23'); await pg.fill('#t_ef','27'); await pg.screenshot(path=f'{OUT}/p2-target.png'); await pg.click('#done')
        print('target',await pg.evaluate("JSON.stringify((t=>({kcal:Math.round(t.kcal),bmi:Math.round(t.bmi*10)/10,tw:Math.round(t.tw*10)/10,notes:t.notes}))(target(curRec())))"))
        for k in ['ckd','dm','lip','mal','std']:
            await pg.select_option('#viewSel',k); print(k,await pg.evaluate("[...document.querySelectorAll('#view .cols .group')][0].innerText.split('\\n').filter(x=>x&&!/^目標|^体重|^身長|^現体重/.test(x)&&!/%$/.test(x)).filter((x,i)=>i%2===0).join('、')"),'overflow',await ov())
        await pg.select_option('#cjSel','5'); print('salt top',await pg.evaluate("[...document.querySelectorAll('#view section')].find(s=>s.textContent.includes('どこから来ているか')).innerText.split('\\n').slice(2,8).join(' | ')"))
        await pg.click('label:has-text("従来の方法")'); print('pfc mode',await pg.evaluate("S.pfc"),'overflow',await ov())
        await pg.screenshot(path=f'{OUT}/p2-result.png',full_page=True)
        print('copy',await pg.evaluate("textOfRecord().split('\\n').slice(0,6).join(' // ')"))
        await pg.click('[data-tab="rcp"]'); print('recipes',await pg.evaluate("S.recipes.map(r=>r.name+(r.preset?'*':''))"),'errors',errs)
        await b.close()
asyncio.run(main())
