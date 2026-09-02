import asyncio
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.user import User, Organization, OrganizationMember
from backend.app.models.lead import Lead

async def check():
    async with AsyncSessionLocal() as session:
        users = (await session.execute(select(User))).scalars().all()
        for u in users:
            print(f"User: id={u.id}, email={u.email}")
        orgs = (await session.execute(select(Organization))).scalars().all()
        for o in orgs:
            print(f"Org: id={o.id}, name={o.name}, slug={o.slug}")
        mems = (await session.execute(select(OrganizationMember))).scalars().all()
        for m in mems:
            print(f"Member: user_id={m.user_id}, org_id={m.organization_id}")
        leads = (await session.execute(select(Lead))).scalars().all()
        org_ids = set(l.organization_id for l in leads)
        print(f"Total Leads: {len(leads)}, Org IDs in Leads: {org_ids}")

if __name__ == "__main__":
    asyncio.run(check())
