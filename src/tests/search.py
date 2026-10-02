import asyncio
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
QS='ごはん 150|鶏むね 200|鶏肉 もも|豚肉 ロース|卵|ゆで卵|牛乳|食パン|鮭|焼き鮭|オーツ|インスタントラーメン|おこわ|カップ麺|厚揚げ|高野豆腐|ツナ缶|さば缶|唐揚げ|餃子 5|カレー|ハンバーグ|牡蠣|柿|かき|南瓜|蓮根|牛蒡|茄子 焼き|小豆|大豆|胡麻|薩摩芋|馬鈴薯|米酢|米|玉蜀黍|ねぎ|長ネギ|えび 天ぷら|ビール 350|赤ワイン|お茶|コーヒー|チョコ|ポテチ|せんべい|みそ汁|味噌|塩 1|ほんだし|サラダ油|オリーブオイル|バター 10|マヨネーズ|ケチャップ|ポン酢|納豆|豆腐|絹豆腐|もやし 炒め|キャベツ ゆで|ブロッコリー|アボカド|バナナ|ヨーグルト|チーズ|スライスチーズ|おにぎり|おかゆ|うどん|そば|ラーメン|パスタ|もち|さつまいも|じゃがいも|里芋|こんにゃく|しいたけ|わかめ|のり|ひじき|レバー|砂肝|ウインナー|ベーコン|ハム|まぐろ|刺身|さんま 焼き|あじ フライ|うなぎ|しらす|たこ|いか|あさり|肉じゃが|筑前煮|きんぴら|豚汁|コロッケ|メンチカツ|春巻き|酢豚|麻婆豆腐|チャーハン|グラタン|プリン|アイス|大福|どら焼き|メロンパン|クリームパン|飴|はちみつ|ジャム|梅干し|キムチ|たくあん|とろろ|合いびき肉|豚こま|サラダチキン'.split('|')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); errs=[]
        pg=await (await b.new_context(viewport={'width':390,'height':844})).new_page()
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(URL)
        res=await pg.evaluate("""qs=>qs.map(q=>{const r=search(q);const o=r.out[0];return q+' => '+(o?(o.dish?'dish':F[o.idx][0]+' '+dispName(o.idx)+' '+stateOf(o.idx)+(o.tmp?'[仮]':''))+' ('+r.out.length+')':'×なし')})""",QS)
        print('\n'.join(res)); print('alias keys',await pg.evaluate("Object.keys(ALIAS).length"),'errors',errs)
        await b.close()
asyncio.run(main())
