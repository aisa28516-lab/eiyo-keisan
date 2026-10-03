"""聞き取りでよく出る90語の成績表。候補ゼロの数、量が決まった数、1位が期待どおりの数を出す。
期待する1位は src/tests/words90_expect.json（Claude が成分表の食品名を見て決めた案。確認して直したら、このファイルを書き換える）。"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
URL='file://'+os.path.join(os.path.dirname(HERE),'.out','local.html')
WORDS="ごはん 茶碗1杯|ご飯 大盛り|食パン 6枚切り1枚|食パン 1枚|味噌汁 1杯|みそ汁|納豆 1パック|卵 1個|目玉焼き|卵焼き|バナナ 1本|りんご 1/2個|牛乳 コップ1杯|ヨーグルト 1個|コーヒー 1杯|缶コーヒー 1本|ビール 350ml|焼酎 1合|日本酒 1合|カレーライス|ラーメン|うどん 1玉|そば 1玉|おにぎり 1個|唐揚げ 3個|とんかつ|焼き魚|鮭 1切れ|さば 1切れ|刺身|サラダ|キャベツ 1/2個|キャベツ 千切り|トマト 1個|きゅうり 1本|にんじん 1本|玉ねぎ 1個|じゃがいも 1個|豆腐 半丁|マヨネーズ 大さじ1|醤油 小さじ1|サラダ油 大さじ1|砂糖 大さじ1|バター 10g|ドレッシング 大さじ1|ポテトチップス 1袋|チョコレート|アイスクリーム 1個|せんべい 2枚|まんじゅう 1個|菓子パン|メロンパン 1個|あんぱん|カップラーメン|コーラ 500ml|野菜ジュース 200ml|スポーツドリンク 500ml|ウインナー 3本|ハム 2枚|ベーコン|チーズ 1個|鶏むね肉 100g|豚バラ 100g|ひき肉 100g|牛丼|餃子 5個|ハンバーグ|コロッケ 1個|天ぷら|寿司|お茶漬け|漬物|梅干し 1個|のり|ふりかけ|エンシュア|プロテイン|みかん 1個|いちご 5個|もち 1個|パスタ 100g|スパゲッティ|ミートソース|シチュー|肉じゃが|煮物|ひじき|きんぴら|ほうれん草 おひたし|冷奴".split('|')
JS="""q=>{MODE='i';const R=search(q),o=R.out[0];if(!o)return{q,top:null,qty:!!R.P.qty,g:null};
 let name,code='',g=null;
 if(o.ch!=null){name=extName(extOf(o.ch,o.mi));code='chain';g=R.P.qty?'品':null}
 else if(o.dish){name=(S.recipes.find(x=>x.id===o.dish)||{}).name;code='recipe';g='人分'}
 else if(o.cu){name='my';code='my'}
 else{name=dispName(o.idx);code=F[o.idx][0];const r=resolveQty(R.P.qty,o.idx);g=r?r.g:null}
 return{q,top:name,code,qty:!!R.P.qty,g}}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(); await pg.goto(URL)
        rs=[await pg.evaluate(JS,w) for w in WORDS]; await b.close()
    ep=os.path.join(HERE,'words90_expect.json'); exp=json.load(open(ep,encoding='utf-8')) if os.path.exists(ep) else {}; exp={k:v for k,v in exp.items() if not k.startswith('_')}
    zero=[r['q'] for r in rs if r['top'] is None]; withq=[r for r in rs if r['qty']]; solved=[r for r in withq if r['g'] is not None]
    ok=[r for r in rs if r['q'] in exp and r['code'] in exp[r['q']]]; ng=[r for r in rs if r['q'] in exp and r['code'] not in exp[r['q']]]
    if '-v' in sys.argv:
        for r in rs: print(f"{r['q']} => {r['top']} [{r.get('code','')}] {'' if not r['qty'] else ('量 '+str(r['g']) if r['g'] is not None else '量は未解決')}")
    print(f"成績表：候補ゼロ {len(zero)}／90　量が決まった {len(solved)}／{len(withq)}　1位が期待どおり {len(ok)}／{len(exp)}")
    print('候補ゼロ:', '、'.join(zero)); print('量が未解決:', '、'.join(r['q'] for r in withq if r['g'] is None))
    if ng: print('1位が期待と違う:', '、'.join(f"{r['q']}→{r['top']}" for r in ng))
asyncio.run(main())
