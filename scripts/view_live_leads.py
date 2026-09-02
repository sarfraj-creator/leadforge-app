import asyncio
from sqlalchemy import select, desc
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.company import Company
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.lead import Lead, LeadScore

async def view_live():
    async with AsyncSessionLocal() as session:
        stmt = select(Company, LeadScore, WebsiteAudit).join(Lead, Lead.company_id == Company.id).outerjoin(LeadScore, LeadScore.lead_id == Lead.id).outerjoin(Website, Website.company_id == Company.id).outerjoin(WebsiteAudit, WebsiteAudit.website_id == Website.id).order_by(desc(Company.id)).limit(8)
        res = await session.execute(stmt)
        rows = res.all()
        print(f"--- LATEST INGESTED REAL LEADS ({len(rows)}) ---")
        for comp, score, audit in rows:
            print(f"Company: {comp.business_name} | City: {comp.city} | Country: {comp.country}")
            print(f"  Website: {comp.website} | Domain: {comp.domain} | Source Record: {comp.source_url}")
            print(f"  Lead Score: {score.total_score if score else 'N/A'}/100 ({score.category if score else ''}) | Audit Health: {audit.overall_score if audit else 'N/A'}/100")
            print("-" * 60)

if __name__ == "__main__":
    asyncio.run(view_live())
