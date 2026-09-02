import sys, os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import json
from sqlalchemy import select, func, or_
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.service_need import ServiceNeedEvidence

async def inspect():
    await init_db()
    async with AsyncSessionLocal() as session:
        jobs = (await session.execute(select(DiscoveryJob).order_by(DiscoveryJob.id))).scalars().all()
        print(f"Total Discovery Jobs in DB: {len(jobs)}")
        print("="*80)
        for j in jobs:
            print(f"Job #{j.id}: {j.name}")
            print(f"  Industry: {j.industry} | Location: {j.location} | Status: {j.status}")
            print(f"  Discovered: {j.discovered_count} | Unique/New: {j.new_businesses_count} | Duplicates: {j.duplicates_count}")
            print(f"  Websites Found: {j.websites_found_count} | Reachable: {getattr(j, 'websites_reachable_count', 0)} | Verified: {getattr(j, 'websites_verified_count', 0)}")
            print(f"  Audits Completed: {getattr(j, 'audits_completed_count', 0)} | Audits Incomplete: {getattr(j, 'audits_incomplete_count', 0)}")
            print(f"  Contacts Found: {j.contacts_found_count} | Verified Emails: {j.verified_emails_count}")
            print(f"  Qualified Leads: {j.qualified_leads_count} | Sales Ready: {getattr(j, 'sales_ready_count', 0)}")
            print(f"  Started: {j.started_at} | Completed: {j.completed_at}")
            print(f"  Error: {j.error_message}")
            if getattr(j, "rejection_reasons_json", None):
                print(f"  Rejection reasons: {j.rejection_reasons_json}")
            print("-" * 60)

        # Global aggregate stats
        comps_count = (await session.execute(select(func.count(Company.id)))).scalar() or 0
        leads_count = (await session.execute(select(func.count(Lead.id)))).scalar() or 0
        qual_count = (await session.execute(select(func.count(Lead.id)).where(Lead.is_qualified == True))).scalar() or 0
        sales_ready_count = (await session.execute(select(func.count(Lead.id)).where(Lead.is_sales_ready == True))).scalar() or 0
        audits_count = (await session.execute(select(func.count(WebsiteAudit.id)))).scalar() or 0
        
        print("\n" + "="*80)
        print("GLOBAL DATABASE AGGREGATE:")
        print(f"  Total Companies: {comps_count}")
        print(f"  Total Leads: {leads_count}")
        print(f"  Qualified Leads: {qual_count}")
        print(f"  Sales Ready Leads: {sales_ready_count}")
        print(f"  Total Audits: {audits_count}")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(inspect())
