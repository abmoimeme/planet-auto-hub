"""Slow-phone journey test: land on planetautohub.com -> reach a make -> tap WhatsApp.
Usage: python3 tools/perf.py label [runs]   (writes tools/perf_<label>.json)
Phone: 360x740 Android Chrome UA, CPU 4x slower. Network: 3G-class (300 ms RTT, 700 kbit/s down, 300 kbit/s up). Cold cache every run."""
import asyncio, json, os, sys, http.server, threading, functools, gzip, mimetypes, statistics as st
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UA = 'Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
NET = dict(offline=False, latency=300, downloadThroughput=int(700 * 1024 / 8), uploadThroughput=int(300 * 1024 / 8))
INIT = """window.__m={fcp:null,lcp:0,cls:0,tbt:0};
new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(e.name==='first-contentful-paint')__m.fcp=e.startTime})).observe({type:'paint',buffered:true});
new PerformanceObserver(l=>l.getEntries().forEach(e=>__m.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)__m.cls+=e.value})).observe({type:'layout-shift',buffered:true});
new PerformanceObserver(l=>l.getEntries().forEach(e=>{__m.tbt+=Math.max(0,e.duration-50)})).observe({type:'longtask',buffered:true});"""
class H(http.server.BaseHTTPRequestHandler):
    """Serves the site like GitHub Pages does: text files compressed, images and fonts as they are, long cache headers."""
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path.split('?')[0].lstrip('/') or 'index.html'; f = os.path.join(ROOT, p)
        if not os.path.isfile(f): self.send_response(404); self.end_headers(); return
        body = open(f, 'rb').read(); ct = mimetypes.guess_type(f)[0] or 'application/octet-stream'; self.send_response(200); self.send_header('Content-Type', ct)
        if ct.startswith('text/') or ct in ('application/javascript', 'image/svg+xml', 'application/json'): body = gzip.compress(body, 6); self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control', 'max-age=600'); self.end_headers(); self.wfile.write(body)
async def one(b, port):
    ctx = await b.new_context(viewport={'width': 360, 'height': 740}, device_scale_factor=2, is_mobile=True, has_touch=True, user_agent=UA, locale='fr-FR')
    async def fs(r):
        h = {'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*'}
        await (r.fulfill(status=204, headers=h) if r.request.method == 'OPTIONS' else r.fulfill(status=200, headers=h, body='{}', content_type='application/json'))
    await ctx.route('https://firestore.googleapis.com/**', fs)
    await ctx.route('https://wa.me/**', lambda r: r.fulfill(status=200, body='ok'))
    if os.environ.get('BLOCK'):
        await ctx.route(lambda u: any(k in u for k in os.environ['BLOCK'].split(',')), lambda r: r.abort())
    pg = await ctx.new_page(); await pg.add_init_script(INIT)
    cdp = await ctx.new_cdp_session(pg)
    await cdp.send('Network.enable'); await cdp.send('Network.emulateNetworkConditions', NET); await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    reqs = {}
    cdp.on('Network.requestWillBeSent', lambda e: reqs.setdefault(e['requestId'], {'url': e['request']['url'], 't0': e['timestamp']}))
    def fin(e):
        r = reqs.get(e['requestId']);
        if r: r.update(t1=e['timestamp'], bytes=e['encodedDataLength'])
    cdp.on('Network.loadingFinished', fin)
    await pg.goto(f'http://planetautohub.com:{port}/', wait_until='commit')
    now = lambda: pg.evaluate('performance.now()')
    T = {}
    await pg.wait_for_selector('a[href^="https://wa.me/"]', state='visible', timeout=120000); T['cta_visible'] = await now()
    await pg.evaluate("document.querySelector('#vehicules').scrollIntoView()")
    await pg.wait_for_selector('#vehicules details.mk summary', state='visible', timeout=120000); T['make_list_visible'] = await now()
    await pg.evaluate("document.querySelector('#vehicules details.mk summary').click()"); await pg.wait_for_selector('#vehicules details.mk[open] a[href^="https://wa.me/"]', state='visible', timeout=120000)
    T['wa_link_visible'] = await now()
    T['imgs_missing_in_view'] = await pg.evaluate("[...document.images].filter(i=>{const r=i.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight&&!(i.complete&&i.naturalWidth>0)}).length")
    await pg.evaluate("document.querySelector('#vehicules details.mk[open] a[href^=\"https://wa.me/\"]').click()"); T['wa_tapped'] = await now()
    await pg.wait_for_load_state('load'); await pg.wait_for_timeout(1500)
    m = await pg.evaluate('window.__m'); nav = await pg.evaluate("(()=>{const n=performance.getEntriesByType('navigation')[0];return {load:n.loadEventEnd, dcl:n.domContentLoadedEventEnd}})()")
    base = min(r['t0'] for r in reqs.values())
    wf = sorted([{'url': r['url'].split('planetautohub.com:%d/' % port)[-1] or '/', 'kb': round(r.get('bytes', 0) / 1024, 1), 'start': round((r['t0'] - base) * 1000), 'end': round((r.get('t1', r['t0']) - base) * 1000)} for r in reqs.values() if 'googleapis' not in r['url'] and 'wa.me' not in r['url']], key=lambda x: x['start'])
    await ctx.close()
    ms = lambda name: next((w['end'] for w in wf if name in w['url']), None)
    return dict(logo_ms=ms('assets/logo.webp'), font_ms=ms('montserrat'), fcp=m['fcp'], lcp=m['lcp'], cls=round(m['cls'], 3), tbt=round(m['tbt']), load=nav['load'], **T, requests=len(wf), kb=round(sum(w['kb'] for w in wf), 1), wf=wf)
async def main():
    label = sys.argv[1]; runs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8795), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--host-resolver-rules=MAP planetautohub.com 127.0.0.1'])
        rs = []
        for i in range(runs): rs.append(await one(b, 8795)); print('run', i + 1, {k: (round(v) if isinstance(v, float) and k != 'cls' else v) for k, v in rs[-1].items() if k != 'wf'}, flush=True)
        await b.close()
    keys = [k for k in rs[0] if k != 'wf']; med = {k: round(st.median(r[k] for r in rs), 3 if k == 'cls' else 0) for k in keys}
    json.dump(dict(label=label, median=med, runs=[{k: v for k, v in r.items() if k != 'wf'} for r in rs], waterfall=rs[len(rs) // 2]['wf']), open(f'tools/perf_{label}.json', 'w'), indent=1)
    print('MEDIAN', med)
asyncio.run(main())
