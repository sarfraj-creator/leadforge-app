import sys, os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import json
from sqlalchemy import select, func, or_, and_, desc
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit, WebsitePage
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.models.provenance import FieldProvenanceRecord

async def reconcile_all():
    await init_db()
    async with AsyncSessionLocal() as session:
        # 1. Inspect ALL Discovery Jobs in DB
        all_jobs = (await session.execute(select(DiscoveryJob).order_by(DiscoveryJob.id))).scalars().all()
        print("=== ALL DISCOVERY JOBS IN DB ===")
        for j in all_jobs:
            print(f"Job #{j.id}: Name='{j.name}', Industry='{j.industry}', Location='{j.location}', Discovered={j.discovered_count}, Unique={j.new_businesses_count}, Status={j.status}")
            if j.rejection_reasons_json:
                print(f"  Rejections JSON: {j.rejection_reasons_json}")

        # 2. Inspect ALL Companies in DB
        all_comps = (await session.execute(select(Company).order_by(Company.id))).scalars().all()
        print(f"\n=== TOTAL COMPANIES IN DB: {len(all_comps)} ===")
        for c in all_comps:
            print(f"Company #{c.id}: '{c.business_name}' | Ind='{c.industry}' | Cat='{c.category}' | City='{c.city}' | Country='{c.country}' | Website='{c.website}' | Source='{c.source}' | SourceURL='{c.source_url}'")

        # 3. Inspect ALL Leads and their scores
        all_leads = (await session.execute(select(Lead).order_by(Lead.id))).scalars().all()
        print(f"\n=== TOTAL LEADS IN DB: {len(all_leads)} ===")
        for l in all_leads:
            c = await session.get(Company, l.company_id)
            w = (await session.execute(select(Website).where(Website.company_id == c.id))).scalar_one_or_none()
            sc = (await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))).scalar_one_or_none()
            conts = (await session.execute(select(Contact).where(Contact.company_id == c.id))).scalars().all()
            aud = (await session.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == w.id))).scalars().all() if w else []
            
            # Print details for any lead with a verified website or high DQ
            if (w and w.website_official_verified) or l.is_qualified or l.data_quality_score >= 60:
                print(f"Lead #{l.id} (Company #{c.id} '{c.business_name}'):")
                print(f"  Stage={l.pipeline_stage}, is_qual={l.is_qualified}, is_sales_ready={l.is_sales_ready}, review_status='{l.review_status}'")
                print(f"  DQ_score={l.data_quality_score}, Opp_score={sc.opportunity_score if sc else None}, Contactability_score={sc.contactability_score if sc else None}, Total_score={sc.total_score if sc else None}")
                print(f"  Identity_status='{c.identity_verification_status}', Operating_status='{c.operating_status}', Conflicts={c.has_conflicts}")
                print(f"  Website='{c.website}', Web_status='{getattr(w, 'website_verification_status', None)}', Web_verified={getattr(w, 'website_official_verified', None)}")
                print(f"  Audits count={len(aud)}, Audit_status={[a.audit_status for a in aud]}")
                print(f"  Phone='{c.phone}' ({c.phone_validation_status}), Email='{c.business_email}'")
                for ct in conts:
                    print(f"    Contact: '{ct.full_name}' | Email='{ct.email}' ({ct.email_status})")
                print("-" * 60)

if __name__ == "__main__":
    asyncio.run(reconcile_all())
