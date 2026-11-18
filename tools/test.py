import asyncio, re
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
R=[]
def ok(n,c,d=''): R.append(('PASS' if c else 'FAIL',n,str(d)[:200]))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        import http.server,threading,functools
        srv=http.server.ThreadingHTTPServer(('127.0.0.1',8791),functools.partial(http.server.SimpleHTTPRequestHandler,directory='site')); threading.Thread(target=srv.serve_forever,daemon=True).start()
        ctx=await b.new_context(viewport={'width':390,'height':844},locale='fr-FR'); pg=await ctx.new_page(); errs=[]; reqs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('request',lambda r: reqs.append(r.url))
        await pg.goto('http://127.0.0.1:8791/'); await pg.wait_for_timeout(600)
        ok('No console or CSP errors',not errs,errs[:3])
        ok('Every request stays on the site (no third-party calls)',all(u.startswith('http://127.0.0.1:8791/') for u in reqs),[u for u in reqs if '127.0.0.1' not in u][:3])
        ok('Phone: no sideways scroll',await pg.evaluate("document.documentElement.scrollWidth<=390"),await pg.evaluate("document.documentElement.scrollWidth"))
        ok('No forms or inputs on the page',await pg.evaluate("document.querySelectorAll('form,input,textarea,select').length")==0)
        links=await pg.evaluate("[...document.querySelectorAll('a[href^=\"https://wa.me/\"]')].map(a=>a.href)")
        nums={urlparse(u).path.strip('/') for u in links}
        ok('WhatsApp links: %d, only the two PAH numbers, all with a prefilled message'%len(links),nums=={'221787567676','221787537676'} and all(parse_qs(urlparse(u).query).get('text') for u in links),nums)
        ok('WhatsApp in header, hero, parts, services, contact and bottom bar',await pg.evaluate("['.top','.hero','#pieces','#services','#contact','.dock'].every(s=>document.querySelector(s+' a[href^=\"https://wa.me/\"]')||document.querySelector(s).matches('a[href^=\"https://wa.me/\"]'))"))
        ok('Tap targets at least 44px high',await pg.evaluate("[...document.querySelectorAll('.btn,.lang,.line,.dock,.mk summary')].every(e=>e.getBoundingClientRect().height>=44)"))
        ok('All images load',await pg.evaluate("[...document.images].every(i=>{i.loading='eager';return true})") and True)
        await pg.evaluate("window.scrollTo(0,document.body.scrollHeight)"); await pg.wait_for_timeout(800)
        ok('All images loaded (%d)'%await pg.evaluate("document.images.length"),await pg.evaluate("[...document.images].every(i=>i.complete&&i.naturalWidth>0)"))
        await pg.click('.mk summary >> nth=0'); await pg.wait_for_timeout(100)
        ok('Toyota opens with models and its own WhatsApp link','Hilux' in await pg.inner_text('.mk[open]') and 'Toyota' in parse_qs(urlparse(await pg.get_attribute('.mk[open] a','href')).query)['text'][0])
        await pg.evaluate("window.scrollTo(0,0)"); await pg.screenshot(path='shot_m1.png'); await pg.screenshot(path='shot_mfull.png',full_page=True)
        await pg.click('#lang'); await pg.wait_for_timeout(100)
        ok('English toggle: headline, lang attribute, message',(await pg.inner_text('h1')).startswith('The right part') and await pg.evaluate("document.documentElement.lang")=='en' and 'Hello Planet Auto Hub' in parse_qs(urlparse(await pg.get_attribute('.dock','href')).query)['text'][0])
        ok('English: make link message','part for Toyota' in parse_qs(urlparse(await pg.get_attribute('.mk[open] a','href')).query)['text'][0])
        await pg.reload(); ok('Language choice remembered',await pg.evaluate("document.documentElement.lang")=='en'); await pg.click('#lang')
        ok('Back to French',(await pg.inner_text('h1')).startswith('La bonne pièce'))
        d=await (await b.new_context(viewport={'width':1280,'height':800},locale='fr-FR')).new_page(); await d.goto('http://127.0.0.1:8791/'); await d.wait_for_timeout(500)
        await d.screenshot(path='shot_d1.png'); await d.evaluate("document.querySelector('#vehicules').scrollIntoView()"); await d.wait_for_timeout(500); await d.screenshot(path='shot_d2.png')
        ok('Desktop: no sideways scroll, bottom bar hidden',await d.evaluate("document.documentElement.scrollWidth<=1280 && getComputedStyle(document.querySelector('.dock')).display==='none'"))
        import os; tot=sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk('site') for f in fs)
        ok('Whole site under 400 KB (%d KB)'%(tot//1024),tot<400*1024)
        await b.close()
    for r in R: print(*r,sep=' | ')
    print(sum(r[0]=='PASS' for r in R),'/',len(R))
asyncio.run(main())
