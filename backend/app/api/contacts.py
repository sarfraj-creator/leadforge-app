import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.contact import Contact, EmailVerificationRecord
from backend.app.models.company import Company
from backend.app.schemas.common import ContactOut, ContactCreate
from backend.app.services.contact.verifier import email_verifier

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.get("", response_model=List[ContactOut])
async def list_contacts(
    is_decision_maker: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    query = select(Contact).join(Company, Contact.company_id == Company.id).where(Company.organization_id == org.id)
    if is_decision_maker is not None:
        query = query.where(Contact.is_decision_maker == is_decision_maker)
        
    query = query.order_by(desc(Contact.created_at)).limit(limit).offset(offset)
    res = await db.execute(query)
    return res.scalars().all()

@router.post("", response_model=ContactOut)
async def create_contact(
    req: ContactCreate,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    comp = await db.get(Company, req.company_id)
    if not comp or comp.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Company not found")
        
    email_status = "UNKNOWN"
    verified_at = None
    if req.email:
        v_res = await email_verifier.verify(req.email)
        email_status = v_res["status"]
        verified_at = datetime.datetime.now(datetime.timezone.utc)
        
    contact = Contact(
        company_id=comp.id,
        full_name=req.full_name,
        job_title=req.job_title,
        email=req.email,
        phone=req.phone,
        linkedin_url=req.linkedin_url,
        is_decision_maker=req.is_decision_maker,
        email_status=email_status,
        email_verified_at=verified_at,
        source="Manual Entry"
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

@router.post("/{contact_id}/verify-email")
async def verify_contact_email(
    contact_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    if not contact.email:
        raise HTTPException(status_code=400, detail="Contact has no email address")
        
    res = await email_verifier.verify(contact.email)
    contact.email_status = res["status"]
    contact.email_verified_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.add(EmailVerificationRecord(
        contact_id=contact.id,
        email=contact.email,
        status=res["status"],
        reason=res.get("reason"),
        confidence=res.get("confidence", 1.0)
    ))
    
    await db.commit()
    return res
