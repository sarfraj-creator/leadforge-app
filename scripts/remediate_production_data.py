import sys, os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import json
from sqlalchemy import select, update
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.lead import Lead, LeadScore
from backend.app.services.discovery.taxonomy import resolve_industry_from_source

async def apply_remediation():
    await init_db()
    async with AsyncSessionLocal() as session:
        print("=" * 80)
        print("APPLYING PRODUCTION INTEGRITY REMEDIATION")
        print("=" * 80)

        # 1. Remediate Lead #42 (The Schlitt Law Firm)
        lead_42 = await session.get(Lead, 42)
        if lead_42:
            print(f"Before Lead #42: Stage={lead_42.pipeline_stage}, is_qual={lead_42.is_qualified}, DQ={lead_42.data_quality_score}")
            lead_42.is_qualified = False
            lead_42.is_sales_ready = False
            lead_42.pipeline_stage = "OPPORTUNITY_DETECTED"
            lead_42.stage = "Discovered"
            print(f"After Lead #42:  Stage={lead_42.pipeline_stage}, is_qual={lead_42.is_qualified}, DQ={lead_42.data_quality_score}")

        # 2. Remediate Job #3 (NYC Law Firms)
        job_3 = await session.get(DiscoveryJob, 3)
        if job_3:
            print(f"Before Job #3: Qualified={job_3.qualified_leads_count}, Rejections={job_3.rejection_reasons_json}")
            job_3.qualified_leads_count = 0
            job_3.sales_ready_count = 0
            rej = json.loads(job_3.rejection_reasons_json or "{}")
            # 14 were rejected, now all 15 are rejected (Lead #42 rejected for LOW_DATA_CONFIDENCE since DQ=67 < 70)
            rej["LOW_DATA_CONFIDENCE"] = rej.get("LOW_DATA_CONFIDENCE", 0) + 1
            job_3.rejection_reasons_json = json.dumps(rej)
            print(f"After Job #3:  Qualified={job_3.qualified_leads_count}, Rejections={job_3.rejection_reasons_json}")

        # 3. Remediate Provenance-Backed Industry for Toronto Batch (Companies 46-60)
        print("\nRemediating Toronto taxonomy based on raw source OSM tags...")
        toronto_comps = (await session.execute(
            select(Company).where(Company.id.between(46, 60))
        )).scalars().all()
        
        for c in toronto_comps:
            src = (await session.execute(select(LeadSourceRecord).where(LeadSourceRecord.company_id == c.id))).scalars().first()
            raw_tags = json.loads(src.raw_data) if src and src.raw_data else {}
            old_ind = c.industry
            resolved_ind = resolve_industry_from_source(
                raw_tags=raw_tags,
                source_category=c.category,
                query_industry="real_estate"
            )
            c.industry = resolved_ind
            c.discovered_industry = resolved_ind
            c.verified_industry = resolved_ind
            print(f"  Company #{c.id} ({c.business_name}): '{old_ind}' -> '{c.industry}' (Source Amenity: {raw_tags.get('amenity')})")

        await session.commit()
        print("\nRemediation successfully committed to production database.")

if __name__ == "__main__":
    asyncio.run(apply_remediation())
