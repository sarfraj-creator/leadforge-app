import urllib.request
import json

def check_apis():
    # 1. Leads API
    req = urllib.request.Request("http://127.0.0.1:8000/api/leads?limit=5")
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode('utf-8'))
        print(f"Leads API Total: {data['total']}, Returned: {len(data['leads'])}")
        for l in data['leads']:
            print(f" - [{l['company']['source']}] {l['company']['business_name']} ({l['company']['city']}) | Score: {l['score']['total_score']} | Web: {l['company']['website']}")

    # 2. Analytics Dashboard API
    req2 = urllib.request.Request("http://127.0.0.1:8000/api/analytics/dashboard")
    with urllib.request.urlopen(req2) as res:
        d = json.loads(res.read().decode('utf-8'))
        print(f"\nDashboard API: fresh_leads={d['fresh_leads_count']}, qualified={d['qualified_leads_count']}, hot={d['hot_leads_count']}, audits={d['websites_audited_count']}")

if __name__ == "__main__":
    check_apis()
