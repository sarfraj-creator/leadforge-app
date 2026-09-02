import asyncio
from sqlalchemy import update, select
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.user import User, Organization, OrganizationMember
from backend.app.models.lead import Lead
from backend.app.models.company import Company
from backend.app.models.discovery import DiscoveryJob

async def align():
    async with AsyncSessionLocal() as session:
        # Get primary organization
        stmt = select(Organization).where(Organization.id == 2)
        res = await session.execute(stmt)
        org = res.scalar_one_or_none()
        if not org:
            org = (await session.execute(select(Organization).limit(1))).scalar_one()

        print(f"Aligning all leads, companies, and discovery jobs to Organization ID {org.id} ({org.name})...")
        await session.execute(update(Lead).values(organization_id=org.id))
        await session.execute(update(Company).values(organization_id=org.id))
        await session.execute(update(DiscoveryJob).values(organization_id=org.id))
        await session.commit()
        print("Successfully aligned all 100+ production leads to active user organization!")

if __name__ == "__main__":
    asyncio.run(align())
