import asyncio, json, http.server, threading, functools
from playwright.async_api import async_playwright
D='/home/claude/eiyo-keisan/src/.out/sitetest'
# 公開版を模擬サーバーで開き、認証と保存の通信を偽の応答に差し替えて同期の流れを確かめる
async def main():
    srv=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(http.server.SimpleHTTPRequestHandler,directory=D)); threading.Thread(target=srv.serve_forever,daemon=True).start()
    store={}; log=[]
    async with async_playwright() as p:
        b=await p.chromium.launch()
        async def mk():
            ctx=await b.new_context(viewport={'width':390,'height':844}); pg=await ctx.new_page(); errs=[]
            pg.on('pageerror',lambda e: errs.append(str(e)))
            async def auth(route):
                body=json.loads(route.request.post_data); log.append(('auth',route.request.url.split('accounts:')[1].split('?')[0],body['email']))
                if body['password']!='secret1': await route.fulfill(status=400,json={'error':{'message':'INVALID_LOGIN_CREDENTIALS'}}); return
                await route.fulfill(json={'idToken':'T','refreshToken':'R','localId':'U1','email':body['email'],'expiresIn':'3600'})
            async def fs(route):
                r=route.request; log.append((r.method,r.url.split('/documents/')[1],r.headers.get('authorization')))
                if r.method=='GET':
                    if 'doc' in store: await route.fulfill(json=store['doc'])
                    else: await route.fulfill(status=404,json={'error':{'status':'NOT_FOUND'}})
                else: store['doc']=json.loads(r.post_data); await route.fulfill(json=store['doc'])
            await pg.route('**/identitytoolkit.googleapis.com/**',auth); await pg.route('**/firestore.googleapis.com/**',fs)
            await pg.goto('http://127.0.0.1:8765/index.html'); return pg,errs
        A,ea=await mk()
        await A.click('[data-tab="set"]'); await A.fill('#sEmail','a@example.com'); await A.fill('#sPw','wrong'); await A.click('#sIn'); await A.wait_for_timeout(500)
        print('wrong pw msg:',await A.inner_text('#syncMsg'))
        await A.fill('#sPw','secret1'); await A.click('#sIn'); await A.wait_for_selector('#sOut'); await A.wait_for_timeout(500)
        await A.click('[data-tab="rec"]'); await A.click('#newRec'); await A.fill('#rlabel','SYNC-1'); await A.press('#rlabel','Tab')
        await A.fill('[data-add="new-0"]','ごはん 150'); await A.press('[data-add="new-0"]','Enter'); await A.wait_for_timeout(2200)
        print('A pushed doc bytes:',len(store['doc']['fields']['json']['stringValue']),'updated',store['doc']['fields']['updated']['integerValue'])
        B,eb=await mk()
        await B.click('[data-tab="set"]'); await B.fill('#sEmail','a@example.com'); await B.fill('#sPw','secret1'); await B.click('#sIn'); await B.wait_for_selector('#sOut'); await B.wait_for_timeout(500)
        print('B records after login:',await B.evaluate("S.records.map(r=>r.label)"))
        print('manifest ok:',await B.evaluate("fetch('manifest.webmanifest').then(r=>r.json()).then(j=>j.display)"),'sw:',await B.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r)"))
        print('log:',log[:8]); print('errors',ea,eb)
        await b.close()
asyncio.run(main())
