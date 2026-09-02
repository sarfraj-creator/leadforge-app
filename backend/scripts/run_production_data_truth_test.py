import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import logging
import json
from sqlalchemy import select, func, desc
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import Organization
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.provenance import FieldProvenanceRecord
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.workers.task_runner import task_runner
from backend.scripts.validate_sample_leads import validate_sample_leads

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("production_data_truth_test")

INDUSTRIES = [
    {"industry": "restaurant", "location": "London", "name": "London Restaurants Discovery"},
    {"industry": "dentist", "location": "Sydney", "name": "Sydney Dentists Discovery"},
    {"industry": "lawyer", "location": "New York", "name": "NYC Law Firms Discovery"},
    {"industry": "real_estate", "location": "Toronto", "name": "Toronto Real Estate Discovery"},
    {"industry": "hotel", "location": "Paris", "name": "Paris Hotels Discovery"},
    {"industry": "gym", "location": "Berlin", "name": "Berlin Gyms Discovery"},
    {"industry": "clothing", "location": "Los Angeles", "name": "LA E-Commerce / Retail Discovery"}
]

async def run_production_test():
    logger.info("Initializing Database for Multi-Industry Production Truth Test...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Get or create active test org
        org_res = await session.execute(select(Organization).limit(1))
        org = org_res.scalar_one_or_none()
        if not org:
            org = Organization(name="Global Digital Agency", slug="global-digital-agency")
            session.add(org)
            await session.commit()
            await session.refresh(org)
        org_id = org.id

    job_ids = []
    logger.info("Launching live discovery jobs across 7 diverse industries...")

    for ind_cfg in INDUSTRIES:
        async with AsyncSessionLocal() as session:
            job = DiscoveryJob(
                organization_id=org_id,
                name=ind_cfg["name"],
                location=ind_cfg["location"],
                industry=ind_cfg["industry"],
                freshness_days=7,
                min_lead_score=50,
                max_leads=15,
                sources_used="OpenStreetMap"
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            job_ids.append(job.id)

    # Run each job sequentially through the hardened pipeline
    for j_id in job_ids:
        logger.info("Processing pipeline for Job ID #%d...", j_id)
        await task_runner.run_discovery_pipeline(j_id)

    logger.info("All discovery jobs complete. Aggregating production truth metrics...")

    # Query statistics per industry
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

    # Run 50-lead independent validation
    logger.info("Executing 50-lead independent truth validation...")
    val_report = await validate_sample_leads(50)

    # Print Final Truth Report Table
    print("\n" + "="*115)
    print(f"{'INDUSTRY / VERTICAL':<30} | {'DISC':<5} | {'ID_VER':<6} | {'REACH':<5} | {'WEB_VER':<7} | {'AUDIT':<5} | {'CONT':<5} | {'MX_OK':<5} | {'QUAL':<5} | {'SALES_RDY':<9}")
    print("="*115)
    for row in industry_stats:
        print(f"{row['industry']:<30} | {row['discovered']:<5} | {row['identity_verified']:<6} | {row['reachable_sites']:<5} | {row['verified_sites']:<7} | {row['audits_completed']:<5} | {row['contacts']:<5} | {row['mx_verified']:<5} | {row['qualified']:<5} | {row['sales_ready']:<9}")
    print("="*115)

if __name__ == "__main__":
    asyncio.run(run_production_test())
