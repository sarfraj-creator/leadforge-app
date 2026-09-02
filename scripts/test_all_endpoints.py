import asyncio
import httpx
import time

endpoints = [
    "/api/analytics/dashboard",
    "/api/companies",
    "/api/leads",
    "/api/crm/kanban",
    "/api/crm/tasks",
    "/api/crm/deals",
    "/api/analytics/data-quality",
    "/api/analytics/opportunities-distribution",
    "/api/analytics/source-coverage",
    "/api/analytics/rejection-reasons",
    "/api/inbox/threads",
    "/api/contacts",
    "/api/settings/ai",
    "/api/settings/smtp",
    "/api/discovery/jobs"
]

async def check_endpoints():
    print(f"Testing {len(endpoints)} API endpoints against http://127.0.0.1:8000 ...\n")
    headers = {"X-Organization-Id": "1"}
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=10.0) as client:
        for ep in endpoints:
            start = time.perf_counter()
            try:
                resp = await client.get(ep, headers=headers)
                elapsed_ms = (time.perf_counter() - start) * 1000
                data = resp.json() if resp.status_code == 200 else {}
                count_info = ""
                if isinstance(data, list):
                    count_info = f"{len(data)} items"
                elif isinstance(data, dict):
                    if "total" in data:
                        count_info = f"total: {data['total']}"
                    elif "total_leads" in data:
                        count_info = f"total_leads: {data['total_leads']}"
                    else:
                        count_info = f"{len(data)} keys"
                status_str = f"HTTP {resp.status_code}"
                res_tag = "PASS" if resp.status_code == 200 else "FAIL"
                print(f"{ep:44s} | {status_str:10s} | {elapsed_ms:6.1f}ms | {count_info:20s} | {res_tag}")
            except Exception as e:
                print(f"{ep:44s} | ERROR      | {str(e)[:30]:20s} | FAIL")

asyncio.run(check_endpoints())
