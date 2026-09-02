import asyncio
import datetime
import time
import json
from sqlalchemy import select, func
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import Organization
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.workers.task_runner import task_runner

async def main():
    print("=" * 60)
    print("LEADFORGE — REAL PRODUCTION GLOBAL DISCOVERY ACCEPTANCE RUN")
    print("=" * 60)
    start_time = datetime.datetime.now(datetime.timezone.utc)
    print(f"Start Timestamp: {start_time.isoformat()}")

    await init_db()

    async with AsyncSessionLocal() as session:
        # Get or create active organization
        res = await session.execute(select(Organization).limit(1))
        org = res.scalar_one_or_none()
        if not org:
            org = Organization(name="LeadForge Global Agency", slug="leadforge-global")
            session.add(org)
            await session.commit()
            await session.refresh(org)

        # 1. Create Production Discovery Job
        job = DiscoveryJob(
            organization_id=org.id,
            name="Worldwide Restaurant Production Ingestion",
            location="WORLDWIDE",
            industry="restaurant",
            freshness_days=7,
            min_lead_score=50,
            max_leads=100,
            sources_used="OpenStreetMap",
            status="QUEUED"
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        job_id = job.id
        print(f"Created Discovery Job #{job_id}: '{job.name}' (Location: WORLDWIDE, Industry: restaurant, Source: OpenStreetMap)")

    # 2. Run Real Discovery Pipeline against Overpass & Live Web
    print("\nExecuting real Overpass query and live website audit pipeline...")
    await task_runner.run_discovery_pipeline(job_id)

    # 3. Fetch exact database verification numbers
    async with AsyncSessionLocal() as session:
        job = await session.get(DiscoveryJob, job_id)
        
        # Count total records in DB
        total_companies = await session.scalar(select(func.count(Company.id)).where(Company.organization_id == org.id))
        total_sources = await session.scalar(select(func.count(LeadSourceRecord.id)))
        total_websites = await session.scalar(select(func.count(Website.id)))
        total_audits = await session.scalar(select(func.count(WebsiteAudit.id)))
        total_contacts = await session.scalar(select(func.count(Contact.id)))
        total_leads = await session.scalar(select(func.count(Lead.id)).where(Lead.organization_id == org.id))
        total_qual = await session.scalar(select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.is_qualified == True))

        # Sample 3 real companies to verify provenance
        comp_res = await session.execute(select(Company).where(Company.organization_id == org.id).limit(5))
        sample_companies = comp_res.scalars().all()

        end_time = datetime.datetime.now(datetime.timezone.utc)
        duration_sec = (end_time - start_time).total_seconds()

        print("\n" + "=" * 60)
        print("REAL DISCOVERY ACCEPTANCE RESULTS (100% EVIDENCE-BASED)")
        print("=" * 60)
        print(f"Job Status:              {job.status}")
        print(f"Execution Duration:      {duration_sec:.2f} seconds")
        print(f"Raw Records Discovered:  {job.discovered_count}")
        print(f"Total Companies Stored:  {total_companies}")
        print(f"Source Records (OSM):    {total_sources}")
        print(f"Duplicates Deduped:      {job.duplicates_count}")
        print(f"Websites Found:          {job.websites_found_count}")
        print(f"Websites Crawled:        {job.websites_crawled_count}")
        print(f"Audits Completed:        {total_audits}")
        print(f"Contacts Discovered:     {total_contacts}")
        print(f"Verified Emails:         {job.verified_emails_count}")
        print(f"Total Leads Created:     {total_leads}")
        print(f"Qualified Leads:         {total_qual}")
        print("-" * 60)
        print("SAMPLE DISCOVERED BUSINESSES WITH REAL OSM PROVENANCE:")
        for c in sample_companies:
            print(f" - [{c.source}] {c.business_name} ({c.city}, {c.country}) | Website: {c.website} | Source URL: {c.source_url}")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

