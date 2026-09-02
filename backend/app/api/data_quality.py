import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.company import Company
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead

router = APIRouter(prefix="/data-quality", tags=["Data Quality & Hygiene"])

@router.get("/summary")
async def get_data_quality_summary(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    # Total companies
    tot_comp_q = select(func.count(Company.id)).where(Company.organization_id == org.id)
    total_companies = (await db.execute(tot_comp_q)).scalar() or 0
    
    # Missing websites
    no_web_q = select(func.count(Company.id)).where(Company.organization_id == org.id, Company.website.is_(None))
    no_website = (await db.execute(no_web_q)).scalar() or 0
    
    # Missing business emails
    no_em_q = select(func.count(Company.id)).where(Company.organization_id == org.id, Company.business_email.is_(None))
    no_email = (await db.execute(no_em_q)).scalar() or 0
    
    # Stale leads (30+ days without recheck)
    stale_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.freshness_state == "STALE")
    stale_count = (await db.execute(stale_q)).scalar() or 0
    
    # Unverified contacts
    unver_q = (
        select(func.count(Contact.id))
        .join(Company, Contact.company_id == Company.id)
        .where(Company.organization_id == org.id, Contact.email_status == "UNKNOWN")
    )
    unverified_contacts = (await db.execute(unver_q)).scalar() or 0
    
    # Needs review queue count
    rev_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.needs_review == True)
    needs_review_count = (await db.execute(rev_q)).scalar() or 0
    
    return {
        "total_companies": total_companies,
        "missing_website_count": no_website,
        "missing_email_count": no_email,
        "stale_leads_count": stale_count,
        "unverified_contacts_count": unverified_contacts,
        "needs_review_count": needs_review_count,
        "data_health_score": max(50, 100 - (no_email * 2 + stale_count * 3))
    }
