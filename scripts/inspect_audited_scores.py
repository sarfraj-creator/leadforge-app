import sys, os
sys.path.insert(0, os.path.abspath("."))
import asyncio
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.company import Company
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.service_need import ServiceNeedEvidence
from sqlalchemy import select

async def inspect_audited_leads():
    await init_db()
    async with AsyncSessionLocal() as session:
        leads = (await session.execute(select(Lead).order_by(Lead.id))).scalars().all()
        for l in leads:
            c = await session.get(Company, l.company_id)
            w = (await session.execute(select(Website).where(Website.company_id == c.id))).scalar_one_or_none()
            if w and w.website_official_verified:
                aud = (await session.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == w.id))).scalars().first()
                sc = (await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))).scalar_one_or_none()
                sne = (await session.execute(select(ServiceNeedEvidence).where(ServiceNeedEvidence.lead_id == l.id))).scalars().all()
                print(f"Lead #{l.id} - Company #{c.id} ({c.business_name}):")
                print(f"  Website: {c.website} | Web verified: {w.website_official_verified}")
                print(f"  Audit Status: {aud.audit_status if aud else None} | Overall: {aud.overall_score if aud else None} | Perf: {aud.performance_score if aud else None} | Mobile: {aud.mobile_score if aud else None} | SEO: {aud.seo_score if aud else None} | Conv: {aud.conversion_score if aud else None} | Sec: {aud.security_score if aud else None}")
                print(f"  Scores in DB -> Opp: {sc.opportunity_score if sc else None} | DQ: {l.data_quality_score} | Contact: {sc.contactability_score if sc else None} | Total: {sc.total_score if sc else None}")
                print(f"  Stage: {l.pipeline_stage} | is_qual: {l.is_qualified} | is_sales_ready: {l.is_sales_ready} | Review: {l.review_status}")
                needs_str = [f"{sn.service_type} ({sn.need_score})" for sn in sne]
                print(f"  Service Needs: {needs_str}")
                print('-'*80)

if __name__ == "__main__":
    asyncio.run(inspect_audited_leads())
