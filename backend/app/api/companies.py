from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.schemas.common import CompanyOut

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=List[CompanyOut])
async def list_companies(
    search: Optional[str] = None,
    industry: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    query = select(Company).where(Company.organization_id == org.id)
    if search:
        s = f"%{search.strip()}%"
        query = query.where(
            or_(
                Company.business_name.ilike(s),
                Company.city.ilike(s),
                Company.domain.ilike(s),
                Company.industry.ilike(s)
            )
        )
    if industry:
        query = query.where(Company.industry.ilike(f"%{industry}%"))
    if city:
        query = query.where(Company.city.ilike(f"%{city}%"))
        
    query = query.order_by(desc(Company.discovered_at)).limit(limit).offset(offset)
    res = await db.execute(query)
    companies = res.scalars().all()
    
    # Load source records
    results = []
    for c in companies:
        sp_res = await db.execute(select(LeadSourceRecord).where(LeadSourceRecord.company_id == c.id))
        source_recs = sp_res.scalars().all()
        results.append(
            CompanyOut(
                id=c.id,
                business_name=c.business_name,
                legal_name=c.legal_name,
                industry=c.industry,
                category=c.category,
                description=c.description,
                country=c.country,
                state=c.state,
                city=c.city,
                address=c.address,
                postal_code=c.postal_code,
                phone=c.phone,
                business_email=c.business_email,
                website=c.website,
                domain=c.domain,
                source=c.source,
                source_url=c.source_url,
                confidence=c.confidence,
                discovered_at=c.discovered_at,
                last_seen_at=c.last_seen_at,
                last_checked_at=c.last_checked_at,
                source_records=[
                    {
                        "id": s.id,
                        "source_name": s.source_name,
                        "source_record_id": s.source_record_id,
                        "source_url": s.source_url,
                        "confidence": s.confidence,
                        "discovered_at": s.discovered_at,
                        "collected_at": s.collected_at
                    }
                    for s in source_recs
                ]
            )
        )
    return results

@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    comp = await db.get(Company, company_id)
    if not comp or comp.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Company not found")
        
    sp_res = await db.execute(select(LeadSourceRecord).where(LeadSourceRecord.company_id == comp.id))
    source_recs = sp_res.scalars().all()
    
    return CompanyOut(
        id=comp.id,
        business_name=comp.business_name,
        legal_name=comp.legal_name,
        industry=comp.industry,
        category=comp.category,
        description=comp.description,
        country=comp.country,
        state=comp.state,
        city=comp.city,
        address=comp.address,
        postal_code=comp.postal_code,
        phone=comp.phone,
        business_email=comp.business_email,
        website=comp.website,
        domain=comp.domain,
        source=comp.source,
        source_url=comp.source_url,
        confidence=comp.confidence,
        discovered_at=comp.discovered_at,
        last_seen_at=comp.last_seen_at,
        last_checked_at=comp.last_checked_at,
        source_records=[
            {
                "id": s.id,
                "source_name": s.source_name,
                "source_record_id": s.source_record_id,
                "source_url": s.source_url,
                "confidence": s.confidence,
                "discovered_at": s.discovered_at,
                "collected_at": s.collected_at
            }
            for s in source_recs
        ]
    )
