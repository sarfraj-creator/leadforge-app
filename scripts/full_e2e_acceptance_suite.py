import json
import time
import sys
from playwright.sync_api import sync_playwright

BASE_URL = 'http://localhost:3005'
API_BASE = 'http://localhost:8000/api'

console_logs = []
network_requests = []
network_errors = []
page_results = {}

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        # Listen to console
        def on_console(msg):
            entry = {'type': msg.type, 'text': msg.text, 'location': msg.location}
            console_logs.append(entry)
            if msg.type in ['error']:
                print(f"[{msg.type.upper()}] {msg.text}")

        page.on('console', on_console)

        # Listen to page errors
        page.on('pageerror', lambda err: console_logs.append({'type': 'pageerror', 'text': str(err)}))

        # Listen to network requests/responses
        def on_response(response):
            network_requests.append({
                'url': response.url,
                'status': response.status,
                'method': response.request.method,
                'ok': response.ok
            })
            if not response.ok and 'favicon' not in response.url and 'hot-reloader' not in response.url:
                network_errors.append({
                    'url': response.url,
                    'status': response.status,
                    'status_text': response.status_text,
                    'method': response.request.method
                })

        page.on('response', on_response)

        routes = [
            ('/', 'Dashboard'),
            ('/companies', 'Companies'),
            ('/leads', 'Leads'),
            ('/discovery', 'Discovery'),
            ('/crm', 'CRM / Kanban'),
            ('/tasks', 'Tasks'),
            ('/analytics', 'Analytics'),
            ('/inbox', 'Inbox'),
            ('/contacts', 'Contacts'),
            ('/settings', 'Settings'),
            ('/audits', 'Audits'),
            ('/data-quality', 'Data Quality'),
            ('/review', 'Review Queue'),
            ('/campaigns', 'Campaigns')
        ]

        print('=' * 80)
        print('1. AUDITING ALL FRONTEND ROUTES')
        print('=' * 80)

        for route, name in routes:
            url = BASE_URL + route
            t0 = time.time()
            try:
                resp = page.goto(url, wait_until='domcontentloaded', timeout=5000)
                page.wait_for_timeout(600)
                dur = (time.time() - t0) * 1000
                status_code = resp.status if resp else 0
                title = page.title()
                
                # Check for critical errors in DOM
                body_text = page.inner_text('body')
                has_runtime_error = 'Application error' in body_text or 'Unhandled Runtime Error' in body_text
                
                page_results[route] = {
                    'name': name,
                    'status': status_code,
                    'load_time_ms': dur,
                    'title': title,
                    'has_runtime_error': has_runtime_error,
                    'ok': status_code == 200 and not has_runtime_error
                }
                print(f"ROUTE: {route:<15} | {name:<18} | Status: {status_code} ({dur:.0f}ms) | RuntimeErr: {has_runtime_error}")
            except Exception as e:
                page_results[route] = {
                    'name': name,
                    'status': 'ERR',
                    'error': str(e),
                    'ok': False
                }
                print(f"ROUTE: {route:<15} | {name:<18} | EXCEPTION: {e}")

        print('\n' + '=' * 80)
        print('2. DEEP DOM VERIFICATION & WORKFLOWS')
        print('=' * 80)

        # 2A. DASHBOARD CHECKS
        print('\n--- 2A. DASHBOARD METRICS ---')
        page.goto(BASE_URL + '/', wait_until='domcontentloaded')
        page.wait_for_timeout(800)
        
        dashboard_text = page.inner_text('body')
        metric_cards = page.query_selector_all('div.p-4.rounded-lg.bg-white')
        for card in metric_cards:
            text = card.inner_text().replace('\n', ' | ')
            print(f"  Metric Card: {text}")

        # 2B. COMPANIES TAXONOMY & SEARCH
        print('\n--- 2B. COMPANIES TAXONOMY & SEARCH ---')
        page.goto(BASE_URL + '/companies', wait_until='domcontentloaded')
        page.wait_for_timeout(800)
        
        search_input = page.query_selector('input[type=\"text\"]')
        if search_input:
            search_input.fill('Toronto')
            page.wait_for_timeout(600)
            rows = page.query_selector_all('table tbody tr')
            print(f"  Toronto search returned {len(rows)} rows.")
            for i, r in enumerate(rows[:5]):
                cells = [c.inner_text().strip() for c in r.query_selector_all('td')]
                print(f"    Row {i+1}: {' | '.join(cells[:5])}")

        # 2C. LEADS & LEAD #42 VERIFICATION
        print('\n--- 2C. LEADS TABLE & LEAD #42 DEEP VERIFICATION ---')
        page.goto(BASE_URL + '/leads', wait_until='domcontentloaded')
        page.wait_for_timeout(800)
        
        if search_input := page.query_selector('input[type=\"text\"]'):
            search_input.fill('Schlitt')
            page.wait_for_timeout(600)
            
        rows = page.query_selector_all('table tbody tr')
        print(f"  Search 'Schlitt' returned {len(rows)} rows.")
        for r in rows:
            print("  Lead Row:", r.inner_text().replace('\n', ' | '))
            r.click()
            page.wait_for_timeout(800)
            break
        
        # Check Modal
        modal = page.query_selector('div[role=\"dialog\"], div.fixed.inset-0')
        if modal:
            modal_text = modal.inner_text()
            print("\n  Lead #42 Modal Details:")
            print("  --------------------------------------------------")
            for line in modal_text.split('\n')[:30]:
                if line.strip():
                    print(f"    {line.strip()}")
            print("  --------------------------------------------------")
            
            # Click tabs inside modal
            tabs = modal.query_selector_all('button')
            for btn in tabs:
                btn_name = btn.inner_text().strip()
                if any(t in btn_name.lower() for t in ['provenance', 'audit', 'score', 'overview', 'opportunity', 'evidence']):
                    try:
                        btn.click()
                        page.wait_for_timeout(300)
                        print(f"  Clicked Modal Tab: '{btn_name}'")
                    except:
                        pass
            
            close_btn = modal.query_selector('button:has-text(\"✕\"), button:has-text(\"Close\"), button svg')
            if close_btn:
                close_btn.click()
                page.wait_for_timeout(300)

        # 2D. DISCOVERY PAGE & NLP QUERY
        print('\n--- 2D. DISCOVERY PAGE & NLP QUERY ---')
        page.goto(BASE_URL + '/discovery', wait_until='domcontentloaded')
        page.wait_for_timeout(800)
        
        nlp_input = page.query_selector('input[placeholder*=\"Find restaurants\"], textarea, input[type=\"text\"]')
        nlp_btn = page.query_selector('button:has-text(\"Interpret\"), button:has-text(\"AI Translate\")')
        if nlp_input and nlp_btn:
            nlp_input.fill('High-end dentists in Boston with slow mobile load times')
            nlp_btn.click()
            page.wait_for_timeout(1000)
            print("  NLP Query submitted. Current criteria values:")
            loc_val = page.eval_on_selector('input[placeholder*=\"WORLDWIDE\"]', 'el => el.value') if page.query_selector('input[placeholder*=\"WORLDWIDE\"]') else 'N/A'
            ind_val = page.eval_on_selector('input[placeholder*=\"restaurant\"]', 'el => el.value') if page.query_selector('input[placeholder*=\"restaurant\"]') else 'N/A'
            print(f"    Location Parameter: {loc_val}")
            print(f"    Industry Parameter: {ind_val}")

        jobs_table_rows = page.query_selector_all('div.space-y-3 > div.p-4, table tbody tr')
        print(f"  Discovery Jobs list count: {len(jobs_table_rows)}")
        for i, row in enumerate(jobs_table_rows[:7]):
            print(f"    Job {i+1}: {row.inner_text().replace(chr(10), ' | ')[:120]}")

        # 2E. CRM / KANBAN
        print('\n--- 2E. CRM / KANBAN ---')
        page.goto(BASE_URL + '/crm', wait_until='domcontentloaded')
        page.wait_for_timeout(800)
        columns = page.query_selector_all('div.flex-1, div.w-72, div.bg-slate-50.rounded-lg')
        print(f"  Kanban columns count: {len(columns)}")
        for col in columns:
            col_text = col.inner_text().split('\n')
            if col_text:
                header = col_text[0]
                cards = [c for c in col_text[1:] if c.strip()]
                print(f"    Column: '{header}' -> {len(cards)} items")

        # 2F. CONTACTS
        print('\n--- 2F. CONTACTS ---')
        page.goto(BASE_URL + '/contacts', wait_until='domcontentloaded')
        page.wait_for_timeout(800)
        c_rows = page.query_selector_all('table tbody tr')
        print(f"  Contacts table row count: {len(c_rows)}")
        for i, r in enumerate(c_rows[:5]):
            cells = [c.inner_text().strip() for c in r.query_selector_all('td')]
            print(f"    Contact {i+1}: {' | '.join(cells)}")

        # 2G. SETTINGS
        print('\n--- 2G. SETTINGS (AI & SMTP) ---')
        page.goto(BASE_URL + '/settings', wait_until='domcontentloaded')
        page.wait_for_timeout(800)
        
        smtp_tab = page.query_selector('button:has-text(\"SMTP\"), button:has-text(\"Email\")')
        if smtp_tab:
            smtp_tab.click()
            page.wait_for_timeout(500)
            print("  Switched to SMTP Settings tab.")
            smtp_inputs = [inp.get_attribute('value') or inp.get_attribute('placeholder') for inp in page.query_selector_all('input')]
            print(f"  SMTP input values/placeholders: {smtp_inputs}")

        browser.close()

run_test()

print('\n' + '=' * 80)
print('3. NETWORK & CONSOLE AUDIT SUMMARY')
print('=' * 80)
print(f"Total Network Requests Captured: {len(network_requests)}")
print(f"Total Network Errors (4xx/5xx): {len(network_errors)}")
for err in network_errors:
    print(f"  FAILED REQUEST: {err['method']} {err['url']} -> HTTP {err['status']} {err['status_text']}")

print(f"\nTotal Console Errors: {len([c for c in console_logs if c['type'] in ['error', 'pageerror']])}")
for c in console_logs:
    if c['type'] in ['error', 'pageerror']:
        print(f"  CONSOLE {c['type'].upper()}: {c['text']}")

print('\n' + '=' * 80)
print('ALL E2E ACCEPTANCE TESTS FINISHED')
print('=' * 80)
