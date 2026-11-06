"""Optional manual browser smoke test. `pip install playwright`; Chromium binary required.

This test injects the committed static site assets into a blank browser document.
No public Pages deployment, YouTube access or remote navigation is assumed.
Run: python3 tests/e2e_browser.py
"""
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path': which('chromium')} if which('chromium') else {}))
    for width,height in ((1440,900),(390,844)):
        page=browser.new_page(viewport={'width':width,'height':height})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'docs/index.html').read_text(encoding='utf-8'))
        page.add_style_tag(content=(ROOT/'docs/assets/style.css').read_text(encoding='utf-8'))
        page.add_script_tag(content=(ROOT/'docs/assets/data.js').read_text(encoding='utf-8'))
        page.add_script_tag(content=(ROOT/'docs/assets/app.js').read_text(encoding='utf-8'))
        assert page.locator('.guide-card').count()==36
        assert page.locator('.idea-row').count()==36
        page.locator('#guideSearch').fill('前 30 秒')
        assert page.locator('.guide-card').count()>0
        page.locator('#guideSearch').fill('')
        page.locator('#clinicImpressions').fill('2000')
        page.locator('#clinicCtr').fill('3')
        page.locator('#clinicClicks').fill('30')
        page.locator('#clinicLeads').fill('0')
        page.locator('#clinicForm button').click()
        assert '资源点击' in page.locator('#clinicFeedback').inner_text()
        page.locator('#clinicFormat').select_option('short')
        assert page.locator('#clinicCtr').is_disabled()
        for k,v in [('econViews','10000'),('econClick','1'),('econLead','5'),('econClose','20'),
                    ('econPrice','400'),('econVariable','100'),('econFixed','200')]:
            page.locator('#'+k).fill(v)
        page.locator('#economyForm button').click()
        content=page.locator('#econEquation').inner_text()
        assert all(s in content for s in ['10,000 次观看','¥400','¥300','¥100']),content
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
        assert not errors,errors
        print(f'PASS {width}×{height}: guides, topics, clinic, calculator, responsive layout')
        page.close()
    browser.close()
