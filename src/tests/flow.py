import asyncio, json
from playwright.async_api import async_playwright
URL='file:///home/claude/eiyo-keisan/src/.out/local.html'
async def run(b,name,vp,scheme,mobile):
    errs=[]
    ctx=await b.new_context(viewport=vp,color_scheme=scheme,has_touch=mobile,is_mobile=mobile)
    await ctx.grant_permissions(['clipboard-read','clipboard-write'])
    pg=await ctx.new_page(); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto(URL)
    ov=lambda: pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth")
    await pg.screenshot(path=f'/home/claude/eiyo-keisan/src/.out/v4-{name}-list.png')
    # example record -> result
    await pg.click('[data-open]'); await pg.click('#confirm')
    print(name,'example kcal:',await pg.evaluate("Math.round(recAgg(curRec(),0).v[0]*10)/10"),'overflow',await ov())
    await pg.click('[data-back="edit"]'); await pg.click('[data-back="list"]')
    # new record
    await pg.click('#newRec'); await pg.fill('#rlabel','A-012'); await pg.press('#rlabel','Tab')
    async def add(key,text):
        await pg.fill(f'[data-add="{key}"]',text); await pg.wait_for_selector(f'[data-sug="{key}"] [data-pick]'); await pg.press(f'[data-add="{key}"]','Enter')
    await add('new-0','ごはん 150')
    mn=await pg.evaluate("curDay().menus[0].n")
    await pg.fill(f'[data-mname="{mn}"]','ごはん'); await pg.press(f'[data-mname="{mn}"]','Tab')
    await pg.click('[data-madd="0"]'); m2=await pg.evaluate("curDay().menus[1].n")
    await pg.fill(f'[data-mname="{m2}"]','野菜炒め'); await add(str(m2),'キャベツ 炒め 100'); await add(str(m2),'豚バラ 50'); await add(str(m2),'にんじん')
    await pg.wait_for_selector('dialog[open] #amt'); await pg.fill('#amt','30'); await pg.screenshot(path=f'/home/claude/eiyo-keisan/src/.out/v4-{name}-sheet.png'); await pg.click('#done')
    await add('new-1','ラーメン 200'); await add('new-2','焼き鮭 80'); await add('new-3','ポテチ 30')
    await pg.check('[data-chk="0"]')
    await pg.screenshot(path=f'/home/claude/eiyo-keisan/src/.out/v4-{name}-edit.png',full_page=True); print(name,'edit overflow',await ov())
    await pg.click('#addDay'); await add('new-0','食パン 60'); 
    await pg.click('#confirm'); await pg.click('#setTarget')
    await pg.click('dialog label:has-text("男性")'); await pg.fill('#t_age','60'); await pg.fill('#t_h','170'); await pg.fill('#t_w','65')
    await pg.click('dialog label:has-text("計算式")'); await pg.fill('#t_af','1.3'); await pg.fill('#t_pk','1.2'); await pg.click('#done')
    print(name, await pg.evaluate("JSON.stringify({t:target(curRec()),d1:recAgg(curRec(),0).v.slice(0,6).map(x=>Math.round(x*10)/10),avg:recAgg(curRec(),-1).v.slice(0,6).map(x=>Math.round(x*10)/10),pfc:pfcOf(recAgg(curRec(),0).v).map(x=>Math.round(x*10)/10),gg:recAgg(curRec(),0).gg,items:curRec().days[0].menus.map(m=>[m.name,m.meal,m.items.map(i=>[i.id,i.g,i.t,Math.round(calc(i).v[0]*10)/10])])})"))
    await pg.screenshot(path=f'/home/claude/eiyo-keisan/src/.out/v4-{name}-result.png',full_page=True); print(name,'result overflow',await ov())
    await pg.click('#copyRes'); 
    if name=='phone': print(await pg.evaluate("textOfRecord()"))
    # recipes & custom
    await pg.click('[data-tab="my"]'); await pg.click('#newCu'); await pg.fill('#c_name','コンビニおにぎり 鮭'); await pg.click('dialog label:has-text("1食あたり")'); await pg.fill('#c_unit','1個'); await pg.fill('#c_v0','180'); await pg.fill('#c_v1','4.5'); await pg.fill('#c_v5','1.2'); await pg.click('#done')
    await pg.click('[data-tab="rcp"]'); await pg.click('#newRcp'); await pg.fill('#rname','肉じゃが'); await pg.press('#rname','Tab')
    for q in ['じゃがいも 300','豚バラ 150','玉ねぎ 200','油 10']: await add('recipe',q)
    await pg.click('#rcpConfirm'); await pg.screenshot(path=f'/home/claude/eiyo-keisan/src/.out/v4-{name}-rcp.png',full_page=True)
    print(name,'recipe per serving kcal',await pg.evaluate("Math.round(sumItems(curRcp().items).v[0]/curRcp().servings*10)/10"),'overflow',await ov())
    await pg.click('[data-tab="rec"]'); await pg.click('[data-open]'); k=str(await pg.evaluate("curDay().menus.find(m=>m.meal==3).n")); await add(k,'肉じゃが'); await add(k,'コンビニおにぎり 2')
    print(name, await pg.evaluate("JSON.stringify(curDay().menus.filter(m=>m.meal==3).map(m=>m.items.map(i=>[itemName(i),itemAmount(i),Math.round(calc(i).v[0]*10)/10])))"))
    await pg.click('[data-tab="set"]'); await pg.click('#expBtn'); print(name,'export len',len(await pg.input_value('#io')))
    await pg.reload(); print(name,'after reload records',await pg.evaluate("S.records.length+' '+S.recipes.length+' '+S.custom.length"),'errors',errs)
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        await run(b,'phone',{'width':390,'height':844},'light',True)
        await run(b,'desk',{'width':1280,'height':800},'dark',False)
        await b.close()
asyncio.run(main())
