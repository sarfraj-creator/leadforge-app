import asyncio
from sqlalchemy import select, func
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company
from backend.app.models.lead import Lead

async def check():
    async with AsyncSessionLocal() as session:
        jobs = (await session.execute(select(DiscoveryJob))).scalars().all()
        for j in jobs:
            print(f"Job #{j.id} ({j.name}): Status={j.status}, Progress={j.progress_percent}%, Discovered={j.discovered_count}, New={j.new_businesses_count}, Audits={j.audits_completed_count}, Qualified={j.qualified_leads_count}")
        comp_count = await session.scalar(select(func.count(Company.id)))
        lead_count = await session.scalar(select(func.count(Lead.id)))
        print(f"Companies: {comp_count}, Leads: {lead_count}")

if __name__ == "__main__":
    asyncio.run(check())
