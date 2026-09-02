import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob
from backend.scripts.validate_sample_leads import validate_sample_leads

async def report():
    await init_db()
    job_ids = [42, 43, 44, 45, 46, 47, 48]
    industry_stats = []
    async with AsyncSessionLocal() as session:
        for j_id in job_ids:
            job = await session.get(DiscoveryJob, j_id)
            if not job:
                continue
            industry_stats.append({
                "industry": job.name.replace(" Discovery", ""),
                "discovered": job.discovered_count,
                "identity_verified": getattr(job, "websites_verified_count", 0),
                "reachable_sites": getattr(job, "websites_reachable_count", 0),
                "verified_sites": getattr(job, "websites_verified_count", 0),
                "audits_completed": getattr(job, "audits_completed_count", 0),
                "contacts": job.contacts_found_count,
                "mx_verified": getattr(job, "verified_emails_count", 0),
                "qualified": job.qualified_leads_count,
                "sales_ready": getattr(job, "sales_ready_count", 0)
            })

    print("\n" + "="*115)
    print(f"{'INDUSTRY / VERTICAL':<30} | {'DISC':<5} | {'ID_VER':<6} | {'REACH':<5} | {'WEB_VER':<7} | {'AUDIT':<5} | {'CONT':<5} | {'MX_OK':<5} | {'QUAL':<5} | {'SALES_RDY':<9}")
    print("="*115)
    for row in industry_stats:
        print(f"{row['industry']:<30} | {row['discovered']:<5} | {row['identity_verified']:<6} | {row['reachable_sites']:<5} | {row['verified_sites']:<7} | {row['audits_completed']:<5} | {row['contacts']:<5} | {row['mx_verified']:<5} | {row['qualified']:<5} | {row['sales_ready']:<9}")
    print("="*115)

    print("\nExecuting 50-Lead Truth Validation Pass...")
    await validate_sample_leads(50)

if __name__ == "__main__":
    asyncio.run(report())
