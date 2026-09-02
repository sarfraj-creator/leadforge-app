from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.lead import Lead
from backend.app.models.website import Website, WebsiteAudit, WebsiteAuditMetric, WebsiteIssue, WebsiteTechnology
from backend.app.models.company import Company
from backend.app.models.contact import Contact
from backend.app.schemas.common import WebsiteAuditOut
from backend.app.services.audit.report_generator import technical_report_generator

router = APIRouter(prefix="/audits", tags=["Website Intelligence & Audits"])

@router.get("/lead/{lead_id}/report")
async def get_lead_technical_report(
    lead_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns full structured R&D Website Audit Report for a specific lead.
    """
    lead = await db.get(Lead, lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    comp = await db.get(Company, lead.company_id)
    web_res = await db.execute(select(Website).where(Website.company_id == lead.company_id))
    web = web_res.scalar_one_or_none()
    
    aud = None
    metrics, issues, technologies = [], [], []
    if web:
        aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web.id).order_by(desc(WebsiteAudit.created_at)))
        aud = aud_res.scalars().first()
        if aud:
            m_res = await db.execute(select(WebsiteAuditMetric).where(WebsiteAuditMetric.audit_id == aud.id))
            metrics = m_res.scalars().all()
            iss_res = await db.execute(select(WebsiteIssue).where(WebsiteIssue.audit_id == aud.id))
            issues = iss_res.scalars().all()
            tech_res = await db.execute(select(WebsiteTechnology).where(WebsiteTechnology.audit_id == aud.id))
            technologies = tech_res.scalars().all()

    cont_res = await db.execute(select(Contact).where(Contact.company_id == lead.company_id))
    contacts = cont_res.scalars().all()
    
    report = technical_report_generator.generate_report_data(
        lead=lead,
        company=comp,
        audit=aud,
        contacts=contacts,
        metrics=metrics,
        issues=issues,
        technologies=technologies
    )
    return report

@router.get("/lead/{lead_id}/report/html")
async def get_lead_technical_report_html(
    lead_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns standalone, executive printable HTML / PDF-ready Technical R&D Audit document.
    """
    lead = await db.get(Lead, lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    comp = await db.get(Company, lead.company_id)
    web_res = await db.execute(select(Website).where(Website.company_id == lead.company_id))
    web = web_res.scalar_one_or_none()
    
    aud = None
    metrics, issues, technologies = [], [], []
    if web:
        aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web.id).order_by(desc(WebsiteAudit.created_at)))
        aud = aud_res.scalars().first()
        if aud:
            m_res = await db.execute(select(WebsiteAuditMetric).where(WebsiteAuditMetric.audit_id == aud.id))
            metrics = m_res.scalars().all()
            iss_res = await db.execute(select(WebsiteIssue).where(WebsiteIssue.audit_id == aud.id))
            issues = iss_res.scalars().all()
            tech_res = await db.execute(select(WebsiteTechnology).where(WebsiteTechnology.audit_id == aud.id))
            technologies = tech_res.scalars().all()

    cont_res = await db.execute(select(Contact).where(Contact.company_id == lead.company_id))
    contacts = cont_res.scalars().all()

    report = technical_report_generator.generate_report_data(
        lead=lead,
        company=comp,
        audit=aud,
        contacts=contacts,
        metrics=metrics,
        issues=issues,
        technologies=technologies
    )
    html_content = technical_report_generator.render_html_report(report)
    return Response(content=html_content, media_type="text/html")

@router.get("/{audit_id}", response_model=WebsiteAuditOut)
async def get_audit(
    audit_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    audit = await db.get(WebsiteAudit, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
        
    m_res = await db.execute(select(WebsiteAuditMetric).where(WebsiteAuditMetric.audit_id == audit.id))
    metrics = m_res.scalars().all()
    
    iss_res = await db.execute(select(WebsiteIssue).where(WebsiteIssue.audit_id == audit.id))
    issues = iss_res.scalars().all()
    
    tech_res = await db.execute(select(WebsiteTechnology).where(WebsiteTechnology.audit_id == audit.id))
    technologies = tech_res.scalars().all()
    
    return WebsiteAuditOut(
        id=audit.id,
        overall_score=audit.overall_score,
        performance_score=audit.performance_score,
        mobile_score=audit.mobile_score,
        seo_score=audit.seo_score,
        accessibility_score=audit.accessibility_score,
        security_score=audit.security_score,
        ux_score=audit.ux_score,
        conversion_score=audit.conversion_score,
        summary=audit.summary,
        created_at=audit.created_at,
        metrics=[{"category": m.category, "metric_name": m.metric_name, "value": m.value, "score": m.score} for m in metrics],
        issues=[{"category": i.category, "title": i.title, "severity": i.severity, "evidence": i.evidence, "recommendation": i.recommendation} for i in issues],
        technologies=[{"name": t.name, "category": t.category, "version": t.version, "confidence": t.confidence} for t in technologies]
    )
