import asyncio
import json
import logging
import datetime
from sqlalchemy import select, func
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import Organization
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact
from backend.app.workers.task_runner import task_runner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("leadforge.production_retest")

INDUSTRIES_TO_RUN = [
    {"name": "Worldwide Restaurant Discovery", "industry": "restaurant", "limit": 100},
    {"name": "Worldwide Dentist Discovery", "industry": "dentist", "limit": 30},
    {"name": "Worldwide Law Firm Discovery", "industry": "lawyer", "limit": 30},
    {"name": "Worldwide Real Estate Discovery", "industry": "real_estate", "limit": 30},
    {"name": "Worldwide Hotel & Hospitality Discovery", "industry": "hotel", "limit": 30},
    {"name": "Worldwide Gym & Fitness Discovery", "industry": "gym", "limit": 30},
    {"name": "Worldwide E-Commerce & Retail Discovery", "industry": "clothes", "limit": 30},
]

async def run_industry_retest():
    await init_db()
    
    results_summary = []

    async with AsyncSessionLocal() as session:
        org = (await session.execute(select(Organization))).scalars().first()
        if not org:
            org = Organization(name="LeadForge Global Intelligence", slug="leadforge-global")
            session.add(org)
            await session.commit()
            await session.refresh(org)
        org_id = org.id

    for item in INDUSTRIES_TO_RUN:
        logger.info("================================================================")
        logger.info("STARTING LIVE DISCOVERY: %s (Industry: %s, Limit: %d)", item["name"], item["industry"], item["limit"])
        logger.info("================================================================")

        # 1. Create Job
        async with AsyncSessionLocal() as session:
            job = DiscoveryJob(
                organization_id=org_id,
                name=item["name"],
                location="WORLDWIDE",
                industry=item["industry"],
                freshness_days=7,
                min_lead_score=50,
                max_leads=item["limit"],
                sources_used="OpenStreetMap"
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            job_id = job.id

        # 2. Run Pipeline
        await task_runner.run_discovery_pipeline(job_id)

        # 3. Retrieve Exact Telemetry Metrics
        async with AsyncSessionLocal() as session:
            job = await session.get(DiscoveryJob, job_id)
            
            # Query exact database records for this industry in this run
            leads_q = (
                select(Lead)
                .join(Company, Lead.company_id == Company.id)
                .where(Company.industry == item["industry"])
            )
            leads = (await session.execute(leads_q)).scalars().all()
            
            discovered = job.discovered_count
            new_stored = job.new_businesses_count
            duplicates = job.duplicates_count
            web_found = job.websites_found_count
            web_reachable = job.websites_reachable_count
            web_verified = job.websites_verified_count
            audits_complete = job.audits_completed_count
            audits_incomplete = job.audits_incomplete_count
            contacts_found = job.contacts_found_count
            verified_emails = job.verified_emails_count
            qualified = job.qualified_leads_count
            sales_ready = job.sales_ready_count
            
            # Check intent count
            scores_q = (
                select(LeadScore)
                .join(Lead, LeadScore.lead_id == Lead.id)
                .join(Company, Lead.company_id == Company.id)
                .where(Company.industry == item["industry"])
            )
            scores = (await session.execute(scores_q)).scalars().all()
            intent_known = sum(1 for s in scores if s.buying_intent != "UNKNOWN")

            summary_row = {
                "industry": item["industry"],
                "target_limit": item["limit"],
                "discovered": discovered,
                "unique_businesses": new_stored,
                "duplicates": duplicates,
                "websites_found": web_found,
                "websites_reachable": web_reachable,
                "websites_verified": web_verified,
                "audits_complete": audits_complete,
                "audits_incomplete": audits_incomplete,
                "intent_known": intent_known,
                "contacts_found": contacts_found,
                "verified_emails": verified_emails,
                "qualified_leads": qualified,
                "sales_ready_leads": sales_ready
            }
            results_summary.append(summary_row)
            
            logger.info("COMPLETED: %s -> Discovered: %d, Reachable: %d, Verified: %d, Audits Complete: %d, Qualified: %d, Sales Ready: %d",
                        item["industry"], discovered, web_reachable, web_verified, audits_complete, qualified, sales_ready)

    # Save summary report to json
    report_file = "d:/ai-system-s/backend/scripts/hardening_retest_results.json"
    with open(report_file, "w") as f:
        json.dump(results_summary, f, indent=2)
    logger.info("All industry tests completed. Report saved to %s", report_file)
    print(json.dumps(results_summary, indent=2))

if __name__ == "__main__":
    asyncio.run(run_industry_retest())
