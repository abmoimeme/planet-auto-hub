import asyncio, json, http.server, threading, functools, os, sys
from playwright.async_api import async_playwright
R=[]
def ok(n,c,d=''): R.append(('PASS' if c else 'FAIL',n,str(d)[:240]))
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
def val(v):
    k=next(iter(v)); x=v[k]
    return [val(i) for i in x.get('values',[])] if k=='arrayValue' else int(x) if k=='integerValue' else x
def doc(body): return {k:val(v) for k,v in json.loads(body)['fields'].items()}
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--host-resolver-rules=MAP planetautohub.com 127.0.0.1,MAP www.planetautohub.com 127.0.0.1'])
        srv=http.server.ThreadingHTTPServer(('127.0.0.1',8793),functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT)); threading.Thread(target=srv.serve_forever,daemon=True).start()
        async def mk(ctxargs=None,ua='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari/604.1'):
            c=await b.new_context(viewport={'width':390,'height':844},locale='fr-FR',user_agent=ua,**(ctxargs or {})); hits=[]; errs=[]
            async def fs(route):
                r=route.request
                if r.method=='OPTIONS': await route.fulfill(status=204,headers={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'})
                else:
                    hits.append((r.url,r.post_data)); await route.fulfill(status=200,headers={'access-control-allow-origin':'*'},body='{}',content_type='application/json')
            await c.route('https://firestore.googleapis.com/**',fs)
            await c.route('https://wa.me/**',lambda r: r.fulfill(status=200,body='ok'))
            pg=await c.new_page(); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
            return c,pg,hits,errs
        c,pg,hits,errs=await mk()
        await pg.goto('http://planetautohub.com:8793/?utm_source=fb'); await pg.wait_for_timeout(2200)
        ok('Visit sends one record shortly after load',len(hits)==1,len(hits))
        u,body=hits[0]; d=doc(body)
        ok('Goes to the shop Firebase web_hits, keyed by visit id','/projects/jaay-69598/databases/(default)/documents/stores/pah/web_hits/'+d['sid'] in u and 'key=' in u,u[:150])
        ok('Fields: new visitor, phone, French, source fb, Africa tz or any tz',d['nv'] and d['dev']=='m' and d['lang']=='fr' and d['src']=='fb',d)
        ok('No personal data fields',set(d)<= {'sid','vid','day','ts','dur','depth','dev','w','lang','vl','tz','ref','src','nv','secs','clicks'},set(d))
        await pg.evaluate("document.querySelector('#vehicules').scrollIntoView()"); await pg.wait_for_timeout(400)
        await pg.click('.mk summary >> nth=0'); await pg.wait_for_timeout(200)
        await pg.evaluate("document.querySelector('#contact').scrollIntoView()"); await pg.wait_for_timeout(400)
        await pg.evaluate("document.querySelector('#contact a.line').addEventListener('click',e=>e.preventDefault())")
        await pg.click('#contact a.line >> nth=0'); await pg.wait_for_timeout(400)
        await pg.evaluate("document.querySelector('#contact a[href^=\"tel:\"]').addEventListener('click',e=>e.preventDefault())")
        await pg.click('#contact a[href^="tel:"] >> nth=0'); await pg.wait_for_timeout(400)
        ls=doc(hits[-1][1])
        ok('Same visit updates the same record',ls['sid']==d['sid'] and hits[-1][0].split('?')[0]==u.split('?')[0])
        ok('Clicks recorded: make opened, WhatsApp line 1 from contact, call',any(x.startswith('open:Toyota') for x in ls['clicks']) and 'wa1@contact' in ls['clicks'] and 'call@contact' in ls['clicks'],ls['clicks'])
        ok('Sections viewed include vehicles and contact',{'top','vehicules','contact'}<=set(ls['secs']),ls['secs'])
        ok('Scroll depth recorded',ls['depth']>50,ls['depth'])
        await pg.click('#lang'); await pg.wait_for_timeout(300)
        ok('At most 8 sends per visit',len(hits)<=8,len(hits))
        ok('No page or CSP errors (connect-src allows Firebase)',not errs,errs[:3])
        csp=await pg.evaluate("document.querySelector('meta[http-equiv=Content-Security-Policy]').content")
        ok('CSP only adds Firestore',"connect-src https://firestore.googleapis.com" in csp and "default-src 'none'" in csp,csp)
        ok('Cookies: none',len(await c.cookies())==0)
        ok('Privacy notice mentions the measurement','mesure d\'audience anonyme'.lower() in (await pg.inner_text('footer')).lower() or 'anonymous audience' in (await pg.inner_text('footer')).lower())
        await c.close()
        c,pg,hits,errs=await mk(); await pg.add_init_script("Object.defineProperty(navigator,'doNotTrack',{get:()=>'1'})")
        await pg.goto('http://planetautohub.com:8793/'); await pg.wait_for_timeout(2000); ok('Do Not Track: nothing sent',len(hits)==0); await c.close()
        c,pg,hits,errs=await mk(); await pg.goto('http://planetautohub.com:8793/?notrack'); await pg.wait_for_timeout(2000)
        await pg.goto('http://planetautohub.com:8793/'); await pg.wait_for_timeout(2000); ok('?notrack excludes this device now and later',len(hits)==0); await c.close()
        c,pg,hits,errs=await mk(ua='Mozilla/5.0 (compatible; Googlebot/2.1)'); await pg.goto('http://planetautohub.com:8793/'); await pg.wait_for_timeout(2000); ok('Bots ignored',len(hits)==0); await c.close()
        c,pg,hits,errs=await mk(); await pg.goto('http://127.0.0.1:8793/'); await pg.wait_for_timeout(2000); ok('Not the live domain (localhost, previews): nothing sent',len(hits)==0); await c.close()
        c,pg,hits,errs=await mk(); await pg.goto('http://planetautohub.com:8793/'); await pg.wait_for_timeout(1800); a=doc(hits[0][1]); await pg.goto('http://planetautohub.com:8793/'); await pg.wait_for_timeout(1800)
        b2=doc(hits[-1][1]); ok('Returning visitor: same visitor id, not new, new visit id',a['vid']==b2['vid'] and not b2['nv'] and a['sid']!=b2['sid']); await c.close()
        await b.close()
    for r in R: print(*r,sep=' | ')
    sys.exit(1 if any(r[0]=='FAIL' for r in R) else 0)
asyncio.run(main())
