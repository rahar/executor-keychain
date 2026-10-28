import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.webkit.launch()
        c = await b.new_context(**p.devices['iPhone 15'])
        pg = await c.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:' + m.text) if m.type in ('error', 'warning') else None)
        await pg.goto('http://localhost:8000/executor.html')
        await pg.wait_for_timeout(500)
        for k in range(8):
            btn = pg.locator('.btn').nth(k)
            await btn.tap()
            await pg.wait_for_timeout(700)
            r = await pg.evaluate('''() => { let d; return ({state: (d=window.__execDebug()).ctx && d.ctx.state, worklet: !!d.node, sp: !!d.sp, sr: d.ctx && d.ctx.sampleRate,
                 peak: Math.max(...Array.from(d.scopeP).map(Math.abs)), tap: document.getElementById('tap').style.display,
                 session: navigator.audioSession ? navigator.audioSession.type : "n/a"}); }''')
            print(k, json.dumps(r))
        print('errors:', errs)
        await b.close()

asyncio.run(main())
