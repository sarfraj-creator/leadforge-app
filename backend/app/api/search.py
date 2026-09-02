from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.company import Company
from backend.app.models.lead import Lead
from backend.app.models.contact import Contact
from backend.app.models.campaign import Campaign
from backend.app.models.crm import Task

router = APIRouter(prefix="/search", tags=["Global Search"])

@router.get("")
async def global_search(
    q: str = Query(..., min_length=2),
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    query_str = f"%{q.strip()}%"
    
    # 1. Search Companies & Leads
    comp_q = select(Company).where(
        Company.organization_id == org.id,
        or_(
            Company.business_name.ilike(query_str),
            Company.domain.ilike(query_str),
            Company.city.ilike(query_str),
            Company.industry.ilike(query_str)
        )
    ).limit(5)
    comp_res = await db.execute(comp_q)
    companies = comp_res.scalars().all()
    
    # 2. Search Contacts
    cont_q = (
        select(Contact)
        .join(Company, Contact.company_id == Company.id)
        .where(
            Company.organization_id == org.id,
            or_(
                Contact.full_name.ilike(query_str),
                Contact.email.ilike(query_str),
                Contact.job_title.ilike(query_str)
            )
        )
        .limit(5)
    )
    cont_res = await db.execute(cont_q)
    contacts = cont_res.scalars().all()
    
    # 3. Search Campaigns
    camp_q = select(Campaign).where(
        Campaign.organization_id == org.id,
        Campaign.name.ilike(query_str)
    ).limit(5)
    camp_res = await db.execute(camp_q)
    campaigns = camp_res.scalars().all()
    
    # 4. Search Tasks
    task_q = select(Task).where(
        Task.organization_id == org.id,
        Task.title.ilike(query_str)
    ).limit(5)
    task_res = await db.execute(task_q)
    tasks = task_res.scalars().all()
    
    results = []
    for c in companies:
        results.append({
            "type": "company",
            "id": c.id,
            "title": c.business_name,
            "subtitle": f"{c.city or ''} · {c.industry or ''}",
            "link": f"/leads?search={c.business_name}"
        })
    for ct in contacts:
        results.append({
            "type": "contact",
            "id": ct.id,
            "title": ct.full_name,
            "subtitle": f"{ct.job_title or 'Contact'} · {ct.email or ''}",
            "link": f"/contacts"
        })
    for cp in campaigns:
        results.append({
            "type": "campaign",
            "id": cp.id,
            "title": cp.name,
            "subtitle": f"Status: {cp.status}",
            "link": f"/campaigns"
        })
    for t in tasks:
        results.append({
            "type": "task",
            "id": t.id,
            "title": t.title,
            "subtitle": f"Priority: {t.priority} · {t.status}",
            "link": f"/tasks"
        })
        
    return results
