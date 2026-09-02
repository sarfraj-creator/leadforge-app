import asyncio
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.user import User, Organization, OrganizationMember
from backend.app.models.lead import Lead
from backend.app.models.company import Company
from backend.app.api.leads import list_leads, get_lead_detail
from backend.app.api.companies import list_companies
from backend.app.api.crm import get_crm_kanban, list_tasks
from fastapi import HTTPException
from sqlalchemy import select

async def test_org_isolation():
    async with AsyncSessionLocal() as session:
        # Check org 1
        org1 = await session.get(Organization, 1)
        assert org1 is not None, 'Default Organization 1 must exist'

        # Check or create org 2
        stmt = select(Organization).where(Organization.id == 2)
        res = await session.execute(stmt)
        org2 = res.scalar_one_or_none()
        if not org2:
            org2 = Organization(id=2, name='Isolated Org 2', slug='isolated-org-2')
            session.add(org2)
            await session.commit()
            await session.refresh(org2)

        print(f'Testing with Org 1 (ID: {org1.id}) and Org 2 (ID: {org2.id})...')

        # 1. Org 1 Leads vs Org 2 Leads
        leads_org1 = await list_leads(org=org1, db=session)
        leads_org2 = await list_leads(org=org2, db=session)
        print(f'Org 1 Leads Count: {leads_org1[\"total\"]}')
        print(f'Org 2 Leads Count: {leads_org2[\"total\"]}')
        assert leads_org1['total'] > 0, 'Org 1 should have production leads'
        assert leads_org2['total'] == 0, 'Org 2 must NOT see Org 1 leads'

        # 2. Org 1 Companies vs Org 2 Companies
        comps_org1 = await list_companies(org=org1, db=session)
        comps_org2 = await list_companies(org=org2, db=session)
        print(f'Org 1 Companies Count: {len(comps_org1)}')
        print(f'Org 2 Companies Count: {len(comps_org2)}')
        assert len(comps_org1) > 0, 'Org 1 should have companies'
        assert len(comps_org2) == 0, 'Org 2 must NOT see Org 1 companies'

        # 3. Direct Lead Detail Access Scoping (Lead #42 belongs to Org 1)
        lead42 = await get_lead_detail(42, org=org1, db=session)
        assert lead42['id'] == 42
        
        try:
            await get_lead_detail(42, org=org2, db=session)
            raise AssertionError('Org 2 should NOT be allowed to access Lead #42')
        except HTTPException as e:
            assert e.status_code == 404, f'Expected 404 Not Found for cross-org access, got {e.status_code}'
            print('Cross-Org Lead Detail Access properly blocked with HTTP 404 Not Found')

        # 4. Kanban Scoping
        kanban_org2 = await get_crm_kanban(org=org2, db=session)
        total_kanban_leads_org2 = sum(len(col['leads']) for col in kanban_org2)
        print(f'Org 2 Kanban Total Leads: {total_kanban_leads_org2}')
        assert total_kanban_leads_org2 == 0, 'Org 2 Kanban board must be empty'

        print('=' * 80)
        print('ORGANIZATION ISOLATION & MULTI-TENANT SECURITY: 100% PASS')
        print('=' * 80)

asyncio.run(test_org_isolation())
