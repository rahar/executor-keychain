import asyncio, json
from playwright.async_api import async_playwright

INIT = '''window.__msgs = []; const pm = MessagePort.prototype.postMessage;
MessagePort.prototype.postMessage = function (m, ...r) { if (m && (m.t === 'press' || m.t === 'release')) window.__msgs.push(m.t + m.k); return pm.call(this, m, ...r); };'''
ST = '() => ({ msgs: window.__msgs.join(" "), lit: [...document.querySelectorAll(".btn")].map((b,i)=>b.classList.contains("on")?i+1:0).filter(Boolean) })'

def ev(k, typ, pid):
    return f"""() => {{ const b = document.querySelectorAll('.btn')[{k}]; const r = b.getBoundingClientRect();
      b.dispatchEvent(new PointerEvent('{typ}', {{bubbles:true, cancelable:true, pointerId:{pid}, pointerType:'touch', isPrimary:true, buttons:{1 if typ=='pointerdown' else 0}, clientX:r.x+5, clientY:r.y+5}})); }}"""

async def tap(pg, k, pid, hold_ms=0):
    await pg.evaluate(ev(k, 'pointerdown', pid))
    if hold_ms: await pg.wait_for_timeout(hold_ms)
    await pg.evaluate(ev(k, 'pointerup', pid))

async def main():
    async with async_playwright() as p:
        b = await p.webkit.launch()
        c = await b.new_context(**p.devices['iPhone 15'])
        await c.add_init_script(INIT)
        pg = await c.new_page(); pg.set_default_timeout(8000)
        await pg.goto('http://localhost:8000/executor.html')
        await pg.wait_for_timeout(300)
        out = {}
        await tap(pg, 0, 1)            # quick first tap on a fresh page
        await pg.wait_for_timeout(800); out['1_quick_tap_#1'] = await pg.evaluate(ST)
        await tap(pg, 4, 1, 300)       # tap #5
        await pg.wait_for_timeout(500); out['2_tap_#5'] = await pg.evaluate(ST)
        await tap(pg, 6, 1, 300)       # tap #7
        await pg.wait_for_timeout(500); out['3_tap_#7'] = await pg.evaluate(ST)
        for k, v in out.items(): print(k, json.dumps(v))
        await b.close()

asyncio.run(main())
