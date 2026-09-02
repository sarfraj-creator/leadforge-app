import datetime
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit, WebsiteAuditMetric, WebsiteIssue, WebsiteTechnology
from backend.app.models.contact import Contact, EmailVerificationRecord
from backend.app.models.campaign import CampaignLead, Campaign
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.models.provenance import FieldProvenanceRecord
from backend.app.models.crm import Activity, Task, Note
from backend.app.schemas.common import LeadBulkAction

router = APIRouter(prefix="/leads", tags=["Leads"])

class ReviewActionPayload(BaseModel):
    action: str # APPROVE, REJECT, NEEDS_RECHECK, MARK_DNC
    note: Optional[str] = None

@router.get("")
async def list_leads(
    search: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    lead_category: Optional[str] = None, # HAS_WEBSITE_REDESIGN | NO_WEBSITE_NEW_BUILD | BUYER_INTENT_POST
    pipeline_stage: Optional[str] = None,
    stage: Optional[str] = None,
    review_status: Optional[str] = None,
    review_queue: Optional[bool] = None,
    min_score: Optional[int] = None,
    min_quality_score: Optional[int] = None,
    opportunity_type: Optional[str] = None,
    freshness: Optional[str] = None,
    has_email: Optional[bool] = None,
    is_qualified: Optional[bool] = None,
    is_sales_ready: Optional[bool] = None,
    needs_review: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Lead)
        .join(Company, Lead.company_id == Company.id)
        .outerjoin(LeadScore, Lead.id == LeadScore.lead_id)
        .where(Lead.organization_id == org.id, Lead.is_archived == False)
    )
    
    if search:
        s = f"%{search.strip()}%"
        query = query.where(
            or_(
                Company.business_name.ilike(s),
                Company.city.ilike(s),
                Company.domain.ilike(s),
                Company.industry.ilike(s),
                Lead.primary_opportunity.ilike(s)
            )
        )
        
    if lead_category:
        if lead_category == "HAS_WEBSITE_REDESIGN":
            query = query.where(or_(Company.website.isnot(None), Company.domain.isnot(None)))
        elif lead_category == "NO_WEBSITE_NEW_BUILD":
            query = query.where(and_(Company.website.is_(None), Company.domain.is_(None)))
        elif lead_category == "BUYER_INTENT_POST":
            query = query.where(LeadScore.buying_intent != "UNKNOWN")

    if industry:
        query = query.where(Company.industry.ilike(f"%{industry}%"))
    if location:
        query = query.where(Company.city.ilike(f"%{location}%"))
    if pipeline_stage:
        query = query.where(Lead.pipeline_stage == pipeline_stage)
    if stage:
        query = query.where(Lead.stage == stage)
    if review_status:
        query = query.where(Lead.review_status == review_status)
    if review_queue:
        query = query.where(Lead.pipeline_stage == "SALES_READY", Lead.review_status == "PENDING")
    if min_score is not None:
        query = query.where(LeadScore.total_score >= min_score)
    if min_quality_score is not None:
        query = query.where(Lead.data_quality_score >= min_quality_score)
    if opportunity_type:
        query = query.where(Lead.primary_opportunity.ilike(f"%{opportunity_type}%"))
    if freshness:
        query = query.where(Lead.freshness_state == freshness)
    if is_qualified is not None:
        query = query.where(Lead.is_qualified == is_qualified)
    if is_sales_ready is not None:
        query = query.where(Lead.is_sales_ready == is_sales_ready)
    if needs_review is not None:
        query = query.where(Lead.needs_review == needs_review)
    if has_email is not None:
        if has_email:
            query = query.where(Company.business_email.isnot(None))
        else:
            query = query.where(Company.business_email.is_(None))
            
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total_count = total_res.scalar() or 0
    
    # Order by lead score descending
    query = query.order_by(desc(LeadScore.total_score), desc(Lead.created_at)).limit(limit).offset(offset)
    
    res = await db.execute(query)
    leads = res.scalars().all()
    
    # Enrich lead records with details
    results = []
    for l in leads:
        comp = await db.get(Company, l.company_id)
        score_res = await db.execute(select(LeadScore).where(LeadScore.lead_id == l.id))
        score_obj = score_res.scalar_one_or_none()
        cont_res = await db.execute(select(Contact).where(Contact.company_id == l.company_id))
        contacts = cont_res.scalars().all()
        web_res = await db.execute(select(Website).where(Website.company_id == l.company_id))
        web_obj = web_res.scalar_one_or_none()
        
        audit_dict = None
        if web_obj:
            aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(desc(WebsiteAudit.created_at)))
            aud_obj = aud_res.scalars().first()
            if aud_obj:
                audit_dict = {
                    "id": aud_obj.id,
                    "audit_status": getattr(aud_obj, "audit_status", "AUDIT_COMPLETE"),
                    "overall_score": aud_obj.overall_score,
                    "performance_score": aud_obj.performance_score,
                    "mobile_score": aud_obj.mobile_score,
                    "seo_score": aud_obj.seo_score,
                    "accessibility_score": aud_obj.accessibility_score,
                    "security_score": aud_obj.security_score,
                    "ux_score": aud_obj.ux_score,
                    "conversion_score": aud_obj.conversion_score,
                    "summary": aud_obj.summary,
                    "created_at": aud_obj.created_at.isoformat()
                }

        lead_cat = "NO_WEBSITE_NEW_BUILD" if not (comp.website or comp.domain) else ("BUYER_INTENT_POST" if (getattr(l, "buying_intent", None) or (score_obj and getattr(score_obj, "buying_intent", None) != "UNKNOWN")) else "HAS_WEBSITE_REDESIGN")

        results.append({
            "id": l.id,
            "organization_id": l.organization_id,
            "company_id": l.company_id,
            "lead_category": lead_cat,
            "pipeline_stage": getattr(l, "pipeline_stage", "DISCOVERED"),
            "is_qualified": l.is_qualified,
            "is_sales_ready": getattr(l, "is_sales_ready", False),
            "needs_review": l.needs_review,
            "review_status": getattr(l, "review_status", "PENDING"),
            "data_quality_score": getattr(l, "data_quality_score", 0),
            "is_do_not_contact": l.is_do_not_contact,
            "stage": l.stage,
            "primary_opportunity": l.primary_opportunity,
            "recommended_service": l.recommended_service,
            "freshness_state": l.freshness_state,
            "created_at": l.created_at.isoformat(),
            "company": {
                "id": comp.id,
                "business_name": comp.business_name,
                "industry": comp.industry,
                "city": comp.city,
                "country": comp.country,
                "phone": comp.phone,
                "normalized_phone_e164": getattr(comp, "normalized_phone_e164", None),
                "phone_validation_status": getattr(comp, "phone_validation_status", "UNVERIFIED"),
                "identity_verification_status": getattr(comp, "identity_verification_status", "UNVERIFIED"),
                "has_conflicts": getattr(comp, "has_conflicts", False),
                "business_email": comp.business_email,
                "website": comp.website,
                "domain": comp.domain,
                "source": comp.source,
                "source_url": comp.source_url,
                "confidence": comp.confidence,
                "website_reachable": getattr(web_obj, "website_reachable", False) if web_obj else False,
                "website_official_verified": getattr(web_obj, "website_official_verified", False) if web_obj else False,
                "website_verification_status": getattr(web_obj, "website_verification_status", "UNVERIFIED") if web_obj else "UNVERIFIED",
                "verification_score": getattr(web_obj, "verification_score", 0) if web_obj else 0,
                "last_checked_at": comp.last_checked_at.isoformat() if comp.last_checked_at else None
            },
            "score": {
                "total_score": score_obj.total_score if score_obj else 0,
                "category": score_obj.category if score_obj else "LOW",
                "data_confidence_score": getattr(score_obj, "data_confidence_score", 0) if score_obj else 0,
                "business_fit_score": getattr(score_obj, "business_fit_score", 0) if score_obj else 0,
                "opportunity_score": getattr(score_obj, "opportunity_score", 0) if score_obj else 0,
                "intent_score": getattr(score_obj, "intent_score", 0) if score_obj else 0,
                "buying_intent": getattr(score_obj, "buying_intent", "UNKNOWN") if score_obj else "UNKNOWN",
                "contactability_score": getattr(score_obj, "contactability_score", 0) if score_obj else 0,
                "explanation": score_obj.explanation if score_obj else None,
            } if score_obj else None,
            "contacts": [
                {
                    "id": c.id,
                    "full_name": c.full_name,
                    "job_title": c.job_title,
                    "is_decision_maker": c.is_decision_maker,
                    "email": c.email,
                    "phone": c.phone,
                    "normalized_phone_e164": getattr(c, "normalized_phone_e164", None),
                    "phone_validation_status": getattr(c, "phone_validation_status", "UNVERIFIED"),
                    "email_status": getattr(c, "email_status", "UNVERIFIED")
                }
                for c in contacts
            ],
            "audit": audit_dict
        })
        
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "leads": results
    }

@router.get("/{lead_id}")
async def get_lead_detail(
    lead_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    lead = await db.get(Lead, lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    comp = await db.get(Company, lead.company_id)
    
    # Source provenance
    sp_res = await db.execute(select(LeadSourceRecord).where(LeadSourceRecord.company_id == comp.id))
    sources = sp_res.scalars().all()
    
    # Field-level provenance records
    fp_res = await db.execute(select(FieldProvenanceRecord).where(FieldProvenanceRecord.organization_id == org.id, FieldProvenanceRecord.entity_id.in_([comp.id, lead.id])))
    provenance_records = fp_res.scalars().all()
    
    # Score
    score_res = await db.execute(select(LeadScore).where(LeadScore.lead_id == lead.id))
    score_obj = score_res.scalar_one_or_none()
    
    # Opportunities
    opp_res = await db.execute(select(LeadOpportunity).where(LeadOpportunity.lead_id == lead.id))
    opportunities = opp_res.scalars().all()

    # Service Need Evidence (9 Core Services)
    sn_res = await db.execute(select(ServiceNeedEvidence).where(ServiceNeedEvidence.lead_id == lead.id))
    service_needs = sn_res.scalars().all()
    
    # Contacts & Verifications
    cont_res = await db.execute(select(Contact).where(Contact.company_id == comp.id))
    contacts = cont_res.scalars().all()
    
    # Website & Deep Audit
    web_res = await db.execute(select(Website).where(Website.company_id == comp.id))
    web_obj = web_res.scalar_one_or_none()
    
    audit_data = None
    if web_obj:
        aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(desc(WebsiteAudit.created_at)))
        aud_obj = aud_res.scalars().first()
        if aud_obj:
            m_res = await db.execute(select(WebsiteAuditMetric).where(WebsiteAuditMetric.audit_id == aud_obj.id))
            metrics = m_res.scalars().all()
            
            iss_res = await db.execute(select(WebsiteIssue).where(WebsiteIssue.audit_id == aud_obj.id))
            issues = iss_res.scalars().all()
            
            tech_res = await db.execute(select(WebsiteTechnology).where(WebsiteTechnology.audit_id == aud_obj.id))
            technologies = tech_res.scalars().all()
            
            audit_data = {
                "id": aud_obj.id,
                "audit_status": getattr(aud_obj, "audit_status", "AUDIT_COMPLETE"),
                "overall_score": aud_obj.overall_score,
                "performance_score": aud_obj.performance_score,
                "mobile_score": aud_obj.mobile_score,
                "seo_score": aud_obj.seo_score,
                "accessibility_score": aud_obj.accessibility_score,
                "security_score": aud_obj.security_score,
                "ux_score": aud_obj.ux_score,
                "conversion_score": aud_obj.conversion_score,
                "summary": aud_obj.summary,
                "created_at": aud_obj.created_at.isoformat(),
                "metrics": [{"category": m.category, "metric_name": m.metric_name, "value": m.value, "score": m.score} for m in metrics],
                "issues": [{"category": i.category, "title": i.title, "severity": i.severity, "evidence": i.evidence, "recommendation": i.recommendation} for i in issues],
                "technologies": [{"name": t.name, "category": t.category, "version": t.version, "confidence": t.confidence} for t in technologies]
            }

    # Timeline Activities
    act_res = await db.execute(select(Activity).where(Activity.lead_id == lead.id).order_by(desc(Activity.created_at)))
    activities = act_res.scalars().all()
    
    # Tasks
    task_res = await db.execute(select(Task).where(Task.lead_id == lead.id).order_by(desc(Task.created_at)))
    tasks = task_res.scalars().all()
    
    # Notes
    note_res = await db.execute(select(Note).where(Note.lead_id == lead.id).order_by(desc(Note.created_at)))
    notes = note_res.scalars().all()

    # Score detail breakdown
    score_rules = json.loads(score_obj.rules_applied) if score_obj and score_obj.rules_applied else []
    data_quality_breakdown = json.loads(lead.data_quality_breakdown_json) if getattr(lead, "data_quality_breakdown_json", None) else {}
    identity_signals = json.loads(comp.identity_signals_json) if getattr(comp, "identity_signals_json", None) else []
    verification_reasons = json.loads(web_obj.verification_reasons_json) if web_obj and getattr(web_obj, "verification_reasons_json", None) else []

    lead_cat = "NO_WEBSITE_NEW_BUILD" if not (comp.website or comp.domain) else ("BUYER_INTENT_POST" if (getattr(lead, "buying_intent", None) or (score_obj and getattr(score_obj, "buying_intent", None) != "UNKNOWN")) else "HAS_WEBSITE_REDESIGN")

    return {
        "id": lead.id,
        "organization_id": lead.organization_id,
        "company_id": lead.company_id,
        "lead_category": lead_cat,
        "pipeline_stage": getattr(lead, "pipeline_stage", "DISCOVERED"),
        "is_qualified": lead.is_qualified,
        "is_sales_ready": getattr(lead, "is_sales_ready", False),
        "needs_review": lead.needs_review,
        "review_status": getattr(lead, "review_status", "PENDING"),
        "data_quality_score": getattr(lead, "data_quality_score", 0),
        "data_quality_breakdown": data_quality_breakdown,
        "is_do_not_contact": lead.is_do_not_contact,
        "stage": lead.stage,
        "primary_opportunity": lead.primary_opportunity,
        "recommended_service": lead.recommended_service,
        "freshness_state": lead.freshness_state,
        "review_notes": getattr(lead, "review_notes", None),
        "review_history": json.loads(lead.review_history_json) if getattr(lead, "review_history_json", None) else [],
        "created_at": lead.created_at.isoformat(),
        "company": {
            "id": comp.id,
            "business_name": comp.business_name,
            "industry": comp.industry,
            "discovered_industry": getattr(comp, "discovered_industry", comp.industry),
            "verified_industry": getattr(comp, "verified_industry", comp.industry),
            "operating_status": getattr(comp, "operating_status", "UNKNOWN"),
            "operating_status_evidence": json.loads(comp.operating_status_evidence_json) if getattr(comp, "operating_status_evidence_json", None) else [],
            "address": comp.address,
            "city": comp.city,
            "country": comp.country,
            "postal_code": comp.postal_code,
            "phone": comp.phone,
            "normalized_phone_e164": getattr(comp, "normalized_phone_e164", None),
            "phone_validation_status": getattr(comp, "phone_validation_status", "UNVERIFIED"),
            "identity_verification_status": getattr(comp, "identity_verification_status", "UNVERIFIED"),
            "identity_signals": identity_signals,
            "has_conflicts": getattr(comp, "has_conflicts", False),
            "conflict_count": getattr(comp, "conflict_count", 0),
            "business_email": comp.business_email,
            "website": comp.website,
            "domain": comp.domain,
            "source": comp.source,
            "source_url": comp.source_url,
            "confidence": comp.confidence,
            "discovered_at": comp.discovered_at.isoformat() if comp.discovered_at else None,
            "last_checked_at": comp.last_checked_at.isoformat() if comp.last_checked_at else None,
            "website_reachable": getattr(web_obj, "website_reachable", False) if web_obj else False,
            "website_official_verified": getattr(web_obj, "website_official_verified", False) if web_obj else False,
            "website_verification_status": getattr(web_obj, "website_verification_status", "UNVERIFIED") if web_obj else "UNVERIFIED",
            "verification_score": getattr(web_obj, "verification_score", 0) if web_obj else 0,
            "verification_reasons": verification_reasons,
            "canonical_url": getattr(web_obj, "canonical_url", comp.website) if web_obj else comp.website,
            "ssl_valid": getattr(web_obj, "ssl_valid", None) if web_obj else None,
            "source_records": [
                {
                    "id": s.id,
                    "source_name": s.source_name,
                    "source_record_id": s.source_record_id,
                    "source_url": s.source_url,
                    "discovered_at": s.discovered_at.isoformat() if getattr(s, "discovered_at", None) else None
                }
                for s in sources
            ]
        },
        "field_provenance": [
            {
                "id": fp.id,
                "field_name": fp.field_name,
                "value": fp.value,
                "source_type": fp.source_type,
                "source_url": fp.source_url,
                "verification_method": fp.verification_method,
                "verification_status": fp.verification_status,
                "confidence_score": fp.confidence_score,
                "observed_at": fp.observed_at.isoformat()
            }
            for fp in provenance_records
        ],
        "service_need_evidence": [
            {
                "id": sn.id,
                "service_type": sn.service_type,
                "need_score": sn.need_score,
                "evidence": json.loads(sn.evidence_json) if sn.evidence_json else [],
                "source_url": sn.source_url,
                "confidence": sn.confidence,
                "observed_at": sn.observed_at.isoformat()
            }
            for sn in service_needs
        ],
        "score": {
            "total_score": score_obj.total_score if score_obj else 0,
            "category": score_obj.category if score_obj else "LOW",
            "data_confidence_score": getattr(score_obj, "data_confidence_score", 0) if score_obj else 0,
            "business_fit_score": getattr(score_obj, "business_fit_score", 0) if score_obj else 0,
            "opportunity_score": getattr(score_obj, "opportunity_score", 0) if score_obj else 0,
            "intent_score": getattr(score_obj, "intent_score", 0) if score_obj else 0,
            "buying_intent": getattr(score_obj, "buying_intent", "UNKNOWN") if score_obj else "UNKNOWN",
            "contactability_score": getattr(score_obj, "contactability_score", 0) if score_obj else 0,
            "rules_applied": score_rules,
            "explanation": score_obj.explanation if score_obj else None,
            "calculated_at": score_obj.calculated_at.isoformat() if score_obj else None
        } if score_obj else None,
        "opportunities": [
            {
                "id": o.id,
                "opportunity_type": o.opportunity_type,
                "confidence": o.confidence,
                "observed_evidence": o.observed_evidence,
                "inferred_benefit": o.inferred_benefit
            }
            for o in opportunities
        ],
        "contacts": [
            {
                "id": c.id,
                "full_name": c.full_name,
                "job_title": c.job_title,
                "is_decision_maker": c.is_decision_maker,
                "email": c.email,
                "phone": c.phone,
                "normalized_phone_e164": getattr(c, "normalized_phone_e164", None),
                "phone_validation_status": getattr(c, "phone_validation_status", "UNVERIFIED"),
                "source": c.source,
                "email_status": getattr(c, "email_status", "UNVERIFIED"),
                "email_verified_at": c.email_verified_at.isoformat() if getattr(c, "email_verified_at", None) else None
            }
            for c in contacts
        ],
        "audit": audit_data,
        "activities": [
            {
                "id": a.id,
                "activity_type": a.activity_type,
                "title": getattr(a, "title", a.activity_type),
                "description": a.description,
                "created_at": a.created_at.isoformat()
            }
            for a in activities
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "is_completed": t.is_completed,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ],
        "notes": [
            {
                "id": n.id,
                "content": n.content,
                "created_at": n.created_at.isoformat()
            }
            for n in notes
        ]
    }

async def recalculate_sales_ready(lead: Lead, db: AsyncSession) -> bool:
    """
    SALES_READY strictly requires ALL:
    1. QUALIFIED (is_qualified == True)
    2. contactability_score >= 50
    3. review_status == 'APPROVED'
    """
    if not lead.is_qualified or getattr(lead, "review_status", "PENDING") != "APPROVED":
        return False
    
    score_stmt = select(LeadScore).where(LeadScore.lead_id == lead.id)
    score_res = await db.execute(score_stmt)
    lead_score = score_res.scalar_one_or_none()
    
    contactability = lead_score.contactability_score if lead_score else 0
    return contactability >= 50

@router.patch("/{lead_id}/review")
async def review_lead(
    lead_id: int,
    payload: ReviewActionPayload,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    lead = await db.get(Lead, lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    old_status = lead.review_status
    act = payload.action.upper()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if act == "APPROVE":
        lead.review_status = "APPROVED"
        lead.needs_review = False
        
        # Outreach Gate: Only strictly qualified leads with contactability >= 50 become SALES_READY
        is_sr = await recalculate_sales_ready(lead, db)
        if is_sr:
            lead.is_sales_ready = True
            lead.pipeline_stage = "SALES_READY"
            lead.stage = "Sales Ready"
        else:
            lead.is_sales_ready = False
            if lead.is_qualified:
                lead.pipeline_stage = "QUALIFIED"
                lead.stage = "Qualified"
    elif act == "REJECT":
        lead.review_status = "REJECTED"
        lead.needs_review = False
        lead.is_qualified = False
        lead.is_sales_ready = False
        lead.stage = "Lost"
    elif act == "NEEDS_RECHECK":
        lead.review_status = "NEEDS_RECHECK"
        lead.needs_review = True
        lead.is_sales_ready = False
    elif act == "MARK_DNC":
        lead.review_status = "REJECTED"
        lead.is_do_not_contact = True
        lead.is_sales_ready = False
        lead.stage = "Do Not Contact"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported review action: {act}")

    lead.review_notes = payload.note

    # Update Review History JSON
    history = json.loads(lead.review_history_json) if lead.review_history_json else []
    history.append({
        "reviewer": "Review Officer",
        "timestamp": now_iso,
        "old_status": old_status,
        "new_status": act,
        "notes": payload.note or ""
    })
    lead.review_history_json = json.dumps(history)

    if payload.note:
        note_obj = Note(lead_id=lead.id, content=f"Review [{act}]: {payload.note}")
        db.add(note_obj)

    # Record Activity
    db.add(Activity(
        organization_id=org.id,
        lead_id=lead.id,
        activity_type="HUMAN_REVIEW",
        title=f"Lead Human Review: {act}",
        description=f"Reviewer updated status from {old_status} to {act}. Notes: {payload.note or 'None'}."
    ))

    await db.commit()
    return {
        "success": True,
        "lead_id": lead.id,
        "review_status": lead.review_status,
        "is_qualified": lead.is_qualified,
        "is_sales_ready": lead.is_sales_ready,
        "pipeline_stage": lead.pipeline_stage
    }

@router.post("/bulk")
async def bulk_action(
    payload: LeadBulkAction,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    if not payload.lead_ids:
        return {"success": False, "message": "No lead IDs provided"}
        
    stmt = select(Lead).where(Lead.id.in_(payload.lead_ids), Lead.organization_id == org.id)
    res = await db.execute(stmt)
    leads = res.scalars().all()
    
    updated_count = 0
    for l in leads:
        if payload.action == "change_stage" and payload.target_stage:
            l.stage = payload.target_stage
            updated_count += 1
        elif payload.action == "mark_dnc":
            l.is_do_not_contact = True
            l.stage = "Do Not Contact"
            updated_count += 1
        elif payload.action == "approve":
            l.needs_review = False
            l.review_status = "APPROVED"
            is_sr = await recalculate_sales_ready(l, db)
            if is_sr:
                l.is_sales_ready = True
                l.pipeline_stage = "SALES_READY"
                l.stage = "Sales Ready"
            else:
                l.is_sales_ready = False
            updated_count += 1
        elif payload.action == "archive":
            l.is_archived = True
            updated_count += 1
        elif payload.action == "add_to_campaign" and payload.campaign_id:
            # Only strictly SALES_READY leads can enter outreach campaigns!
            if l.is_sales_ready:
                cl = CampaignLead(
                    campaign_id=payload.campaign_id,
                    lead_id=l.id,
                    status="QUEUED"
                )
                db.add(cl)
                updated_count += 1
            
    await db.commit()
    return {"success": True, "updated_count": updated_count}

@router.post("/{lead_id}/recheck")
async def recheck_lead(
    lead_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    On-Demand Recheck Endpoint:
    Re-runs identity verification, website reachability, DNS/MX, contact validation,
    deterministic website audit, service need evidence, intent, and lead scoring.
    Preserves historical audits and activity logs.
    """
    from backend.app.services.crawler.safe_crawler import safe_crawler
    from backend.app.services.verification.website_verifier import WebsiteVerifier
    from backend.app.services.verification.identity_verifier import BusinessIdentityVerifier
    from backend.app.services.domain.domain_intel import DomainIntelligence
    from backend.app.services.contact.verifier import email_verifier
    from backend.app.services.contact.phone_verifier import phone_verifier
    from backend.app.services.contact.decision_maker import decision_maker_finder
    from backend.app.services.audit.engine import audit_engine
    from backend.app.services.scoring.opportunity_engine import opportunity_engine
    from backend.app.services.scoring.service_need_engine import service_need_engine
    from backend.app.services.scoring.lead_scorer import lead_scorer
    from backend.app.services.scoring.data_quality_scorer import data_quality_scorer
    from backend.app.services.conflict.contradiction_detector import contradiction_detector
    from backend.app.services.intent.intent_engine import BuyingIntentEngine

    lead = await db.get(Lead, lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    comp = await db.get(Company, lead.company_id)
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # 1. Re-normalize Phone
    phone_norm = phone_verifier.verify_and_normalize(comp.phone)
    comp.normalized_phone_e164 = phone_norm["normalized_e164"]
    comp.phone_validation_status = phone_norm["validation_status"]
    comp.last_checked_at = now_utc

    # 2. Website Crawl & Re-verification
    audit_res = None
    crawl = None
    intent_info = {"buying_intent": "UNKNOWN", "intent_score": 0, "signals": []}
    web_verify_res = {"website_verification_status": "UNVERIFIED", "verification_score": 0, "verification_reasons": [], "is_verified": False}
    identity_res = {"status": "UNVERIFIED", "score": 0, "signals": [], "is_verified": False}

    if comp.website:
        crawl = await safe_crawler.crawl_site(
            target_url=comp.website,
            business_name=comp.business_name,
            city=comp.city
        )

        web_verify_res = WebsiteVerifier.verify_website(
            business_name=comp.business_name,
            website_url=comp.website,
            html_content=crawl.raw_html,
            status_code=crawl.http_status,
            phone=comp.phone,
            city=comp.city
        )

        if crawl.website_reachable and crawl.raw_html:
            identity_res = BusinessIdentityVerifier.verify_identity(
                business_name=comp.business_name,
                website_url=comp.website,
                domain=comp.domain,
                title=crawl.title,
                h1_tags=crawl.h1_tags,
                html_content=crawl.raw_html,
                visible_text=getattr(crawl, "visible_text", "") or "",
                address=comp.address,
                city=comp.city,
                country=comp.country,
                phone=comp.phone
            )
            intent_info = BuyingIntentEngine.detect_intent(
                html_content=crawl.raw_html,
                source_url=comp.website
            )

        comp.identity_verification_status = identity_res["status"]
        comp.identity_signals_json = json.dumps(identity_res["signals"])

        # Update Website record
        w_stmt = select(Website).where(Website.company_id == comp.id)
        web_res = await db.execute(w_stmt)
        web_obj = web_res.scalar_one_or_none()
        if web_obj:
            web_obj.website_reachable = crawl.website_reachable
            web_obj.website_official_verified = web_verify_res["is_verified"]
            web_obj.website_verification_status = web_verify_res["website_verification_status"]
            web_obj.verification_score = web_verify_res["verification_score"]
            web_obj.verification_reasons_json = json.dumps(web_verify_res["verification_reasons"])
            web_obj.http_status = crawl.http_status
            web_obj.last_crawled_at = now_utc
            web_obj.last_audited_at = now_utc

        # 3. New Audit Record
        audit_res = audit_engine.audit(crawl)
        w_audit = WebsiteAudit(
            website_id=web_obj.id if web_obj else 0,
            audit_status=audit_res.status,
            overall_score=audit_res.overall_score,
            performance_score=audit_res.performance_score,
            mobile_score=audit_res.mobile_score,
            seo_score=audit_res.seo_score,
            accessibility_score=audit_res.accessibility_score,
            security_score=audit_res.security_score,
            ux_score=audit_res.ux_score,
            conversion_score=audit_res.conversion_score,
            summary=audit_res.summary
        )
        if web_obj:
            db.add(w_audit)

    # 4. Service Needs & Lead Scoring
    service_items = service_need_engine.evaluate_services(
        has_website=bool(comp.website),
        audit=audit_res,
        source_url=comp.website
    )

    opps, primary_service = opportunity_engine.evaluate(
        has_website=bool(comp.website),
        audit=audit_res,
        has_contact_email=bool(comp.business_email),
        has_phone=bool(comp.phone),
        is_fresh=True
    )

    score_info = lead_scorer.calculate_score(
        has_website=bool(comp.website),
        audit=audit_res,
        opportunities=opps,
        has_email=bool(comp.business_email),
        email_status="DOMAIN_MAIL_ENABLED" if comp.business_email else None,
        has_phone=bool(comp.phone),
        has_form=bool(crawl and len(crawl.forms) > 0),
        is_fresh=True,
        website_reachable=bool(crawl and crawl.website_reachable),
        website_official_verified=bool(crawl and crawl.website_official_verified),
        intent_info=intent_info,
        has_source_provenance=True
    )

    data_quality_res = data_quality_scorer.calculate_data_quality(
        source_name=comp.source,
        identity_status=comp.identity_verification_status,
        website_status=web_verify_res["website_verification_status"],
        email_status="DOMAIN_MAIL_ENABLED" if comp.business_email else None,
        phone_status=comp.phone_validation_status,
        freshness_state="FRESH",
        has_conflicts=comp.has_conflicts
    )

    # Update Lead
    lead.data_quality_score = data_quality_res["total_score"]
    lead.data_quality_breakdown_json = json.dumps(data_quality_res["breakdown"])
    lead.freshness_state = "FRESH"
    lead.primary_opportunity = opps[0].opportunity_type if opps else "Website Build"
    lead.recommended_service = primary_service

    # Canonical Qualification Check
    has_verified_identity = bool(comp.identity_verification_status in ["HIGH", "MEDIUM", "LOW"])
    has_verified_website = bool(web_verify_res["is_verified"] or not comp.website)
    has_complete_audit = bool((audit_res and audit_res.status == "AUDIT_COMPLETE") or not comp.website)
    has_qualifying_opportunity = bool(score_info["opportunity_score"] >= 60)
    has_qualifying_quality = bool(data_quality_res["total_score"] >= 70)

    canonical_qualified = (
        has_verified_identity
        and has_verified_website
        and has_complete_audit
        and has_qualifying_opportunity
        and has_qualifying_quality
    )
    lead.is_qualified = canonical_qualified

    # Pipeline Stage Transition
    if canonical_qualified and getattr(lead, "review_status", "PENDING") == "APPROVED" and score_info["contactability_score"] >= 50:
        lead.is_sales_ready = True
        lead.pipeline_stage = "SALES_READY"
        lead.stage = "Sales Ready"
    elif canonical_qualified:
        lead.is_sales_ready = False
        lead.pipeline_stage = "QUALIFIED"
        lead.stage = "Qualified"
    elif (comp.business_email or len((await db.scalars(select(Contact.id).where(Contact.company_id == comp.id))).all()) > 0) and score_info["contactability_score"] >= 50:
        lead.is_sales_ready = False
        lead.pipeline_stage = "CONTACTABLE"
    elif len(service_items) > 0 and audit_res and audit_res.status == "AUDIT_COMPLETE":
        lead.is_sales_ready = False
        lead.pipeline_stage = "OPPORTUNITY_DETECTED"
    elif audit_res and audit_res.status == "AUDIT_COMPLETE":
        lead.is_sales_ready = False
        lead.pipeline_stage = "AUDITED"
    elif web_verify_res["is_verified"]:
        lead.is_sales_ready = False
        lead.pipeline_stage = "WEBSITE_VERIFIED"
    elif comp.identity_verification_status in ["HIGH", "MEDIUM"]:
        lead.is_sales_ready = False
        lead.pipeline_stage = "IDENTITY_VERIFIED"
    else:
        lead.is_sales_ready = False
        lead.pipeline_stage = "DISCOVERED"

    # Update Score
    s_stmt = select(LeadScore).where(LeadScore.lead_id == lead.id)
    s_res = await db.execute(s_stmt)
    score_obj = s_res.scalar_one_or_none()
    if score_obj:
        score_obj.total_score = score_info["total_score"]
        score_obj.category = score_info["category"]
        score_obj.data_confidence_score = score_info["data_confidence_score"]
        score_obj.business_fit_score = score_info["business_fit_score"]
        score_obj.opportunity_score = score_info["opportunity_score"]
        score_obj.intent_score = score_info["intent_score"]
        score_obj.buying_intent = score_info["buying_intent"]
        score_obj.contactability_score = score_info["contactability_score"]
        score_obj.rules_applied = json.dumps(score_info["rules_applied"])
        score_obj.explanation = score_info["explanation"]
        score_obj.calculated_at = now_utc

    # Log Activity
    db.add(Activity(
        organization_id=org.id,
        lead_id=lead.id,
        activity_type="LEAD_RECHECK",
        title="Live Data Recheck Completed",
        description=f"Re-verified identity: {comp.identity_verification_status}, Website: {web_verify_res['website_verification_status']}, Quality Score: {data_quality_res['total_score']}."
    ))

    await db.commit()
    return {
        "success": True,
        "lead_id": lead.id,
        "data_quality_score": lead.data_quality_score,
        "identity_status": comp.identity_verification_status,
        "website_status": web_verify_res["website_verification_status"],
        "pipeline_stage": lead.pipeline_stage,
        "is_qualified": lead.is_qualified,
        "is_sales_ready": lead.is_sales_ready
    }

