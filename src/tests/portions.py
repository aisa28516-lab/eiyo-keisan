import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
QS=['うどん 1玉','うどん 2玉','ごはん 茶碗1杯','ごはん 小盛り1杯','ご飯 お茶碗2杯','ごはん 150','ごはん150g','卵 1個','卵 2個','ゆで卵 1個','豆腐 1/2丁','豆腐 半丁','納豆 1パック','チーズ スライス2枚','みかん 2個','りんご 1/2個','牛乳 コップ1杯','牛乳 200ml','牛乳 瓶1本','ビール 350ml','ビール 中ジョッキ','ビール 大びん1本','ビール 缶2本','日本酒 1合','日本酒 おちょこ3杯','酒 お猪口2杯','ワイン グラス2杯','赤ワイン ボトル1本','ウイスキー ダブル','焼酎 コップ1杯','しょうゆ 大さじ1','醤油 小さじ1/2','油 大さじ1','砂糖 大さじ2','みそ 大さじ1','米 1合','小麦粉 カップ1','塩 小さじ1','コーヒー 200ml','キャベツ 1/2個','鶏むね 1枚','ラーメン 1玉','マヨネーズ 大さじ1','はちみつ 大さじ1','カップ麺 1個','バター 10g','鮭 1切れ','食パン 1枚','じゃがいも 1.5kg']
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); errs=[]
        pg=await (await b.new_context(viewport={'width':390,'height':844})).new_page()
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(URL)
        res=await pg.evaluate("""qs=>qs.map(q=>{const r=search(q);const o=r.out[0];if(!o)return q+' => ×なし';const R=resolveQty(r.P.qty,o.idx);const it={id:F[o.idx][0],g:null,t:'a',r:false};if(R)applyPortion(it,R);return q+' => '+F[IDX[it.id]][0]+' '+dispName(IDX[it.id])+' '+stateOf(IDX[it.id])+' | '+(R?(it.pl||'')+' = '+it.g+' g t='+it.t+(it.r?' 廃棄込み':'')+(it.pn?' ※'+it.pn:'')+' → '+Math.round(calc(it).v[0])+' kcal':'量は未解決')})""",QS)
        print('\n'.join(res))
        # UI: sheet chips
        await pg.click('#newRec'); await pg.fill('[data-add="new-0"]','うどん'); await pg.press('[data-add="new-0"]','Enter'); await pg.wait_for_selector('dialog[open] [data-bp]')
        await pg.click('dialog [data-bp="0"]'); await pg.click('dialog [data-bp="0"]'); await pg.screenshot(path='/home/claude/eiyo-keisan/src/.out/v6-sheet.png'); await pg.click('#done')
        await pg.fill('[data-add]:not([data-add^="new"])','ビール 中ジョッキ2杯'); await pg.wait_for_timeout(300); await pg.screenshot(path='/home/claude/eiyo-keisan/src/.out/v6-sug.png')
        print(await pg.evaluate("JSON.stringify(curDay().menus[0].items.map(i=>[i.id,i.g,i.pl,i.t]))"),'errors',errs)
        await b.close()
asyncio.run(main())
