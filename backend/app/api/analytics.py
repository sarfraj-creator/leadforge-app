from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact
from backend.app.models.email import EmailThread, EmailMessage
from backend.app.models.crm import Deal, Activity
from backend.app.models.provenance import FieldProvenanceRecord
from backend.app.models.service_need import ServiceNeedEvidence

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])

@router.get("/dashboard")
async def get_dashboard_stats(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    # 1. Lead counts
    fresh_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.freshness_state == "FRESH")
    fresh_count = (await db.execute(fresh_q)).scalar() or 0
    
    qual_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.is_qualified == True)
    qual_count = (await db.execute(qual_q)).scalar() or 0

    sales_ready_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.is_sales_ready == True)
    sales_ready_count = (await db.execute(sales_ready_q)).scalar() or 0
    
    hot_q = (
        select(func.count(Lead.id))
        .join(LeadScore, Lead.id == LeadScore.lead_id)
        .where(Lead.organization_id == org.id, LeadScore.category == "HOT")
    )
    hot_count = (await db.execute(hot_q)).scalar() or 0
    
    aud_q = (
        select(func.count(WebsiteAudit.id))
        .join(Website, WebsiteAudit.website_id == Website.id)
        .join(Company, Website.company_id == Company.id)
        .where(Company.organization_id == org.id)
    )
    aud_count = (await db.execute(aud_q)).scalar() or 0

    # Total companies & quality verification rates
    comp_count_q = select(func.count(Company.id)).where(Company.organization_id == org.id)
    total_companies = (await db.execute(comp_count_q)).scalar() or 0

    web_found_q = select(func.count(Company.id)).where(Company.organization_id == org.id, Company.website.isnot(None))
    web_found_count = (await db.execute(web_found_q)).scalar() or 0

    web_reachable_q = (
        select(func.count(Website.id))
        .join(Company, Website.company_id == Company.id)
        .where(Company.organization_id == org.id, Website.website_reachable == True)
    )
    web_reachable_count = (await db.execute(web_reachable_q)).scalar() or 0

    web_verified_q = (
        select(func.count(Website.id))
        .join(Company, Website.company_id == Company.id)
        .where(Company.organization_id == org.id, Website.website_official_verified == True)
    )
    web_verified_count = (await db.execute(web_verified_q)).scalar() or 0

    total_contacts_q = (
        select(func.count(Contact.id))
        .join(Company, Contact.company_id == Company.id)
        .where(Company.organization_id == org.id)
    )
    total_contacts = (await db.execute(total_contacts_q)).scalar() or 0

    mx_verified_q = (
        select(func.count(Contact.id))
        .join(Company, Contact.company_id == Company.id)
        .where(Company.organization_id == org.id, Contact.email_status.in_(["DOMAIN_MAIL_ENABLED", "MAILBOX_VERIFIED", "VALID"]))
    )
    mx_verified_count = (await db.execute(mx_verified_q)).scalar() or 0

    # Calculate rates
    discovery_rate = round((web_found_count / total_companies * 100), 1) if total_companies > 0 else 0.0
    reachable_rate = round((web_reachable_count / web_found_count * 100), 1) if web_found_count > 0 else 0.0
    verification_rate = round((web_verified_count / web_reachable_count * 100), 1) if web_reachable_count > 0 else 0.0
    email_rate = round((mx_verified_count / total_contacts * 100), 1) if total_contacts > 0 else 0.0
    
    # 2. Email metrics
    sent_q = (
        select(func.count(EmailMessage.id))
        .join(EmailThread, EmailMessage.thread_id == EmailThread.id)
        .where(EmailThread.organization_id == org.id, EmailMessage.direction == "OUTBOUND")
    )
    sent_count = (await db.execute(sent_q)).scalar() or 0
    
    replies_q = select(func.count(EmailThread.id)).where(
        EmailThread.organization_id == org.id,
        EmailThread.reply_classification.isnot(None)
    )
    replies_count = (await db.execute(replies_q)).scalar() or 0
    
    pos_replies_q = select(func.count(EmailThread.id)).where(
        EmailThread.organization_id == org.id,
        EmailThread.reply_classification.in_(["Interested", "Meeting Request", "Pricing Request"])
    )
    pos_replies_count = (await db.execute(pos_replies_q)).scalar() or 0
    
    # 3. Pipeline Stages & Deals
    meetings_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.stage == "Meeting")
    meetings_count = (await db.execute(meetings_q)).scalar() or 0
    
    proposals_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.stage == "Proposal")
    proposals_count = (await db.execute(proposals_q)).scalar() or 0
    
    won_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.stage == "Won")
    won_count = (await db.execute(won_q)).scalar() or 0
    
    val_q = select(func.sum(Deal.value)).where(Deal.organization_id == org.id, Deal.stage != "Lost")
    pipeline_val = (await db.execute(val_q)).scalar() or 0.0
    
    # 4. Recent Activities
    act_q = select(Activity).where(Activity.organization_id == org.id).order_by(desc(Activity.created_at)).limit(10)
    act_res = await db.execute(act_q)
    activities = act_res.scalars().all()
    
    return {
        "fresh_leads_count": fresh_count,
        "qualified_leads_count": qual_count,
        "sales_ready_count": sales_ready_count,
        "hot_leads_count": hot_count,
        "websites_audited_count": aud_count,
        "website_discovery_rate": discovery_rate,
        "website_reachable_rate": reachable_rate,
        "website_verification_rate": verification_rate,
        "email_verification_rate": email_rate,
        "emails_sent_count": sent_count,
        "replies_count": replies_count,
        "positive_replies_count": pos_replies_count,
        "meetings_count": meetings_count,
        "proposals_count": proposals_count,
        "won_deals_count": won_count,
        "pipeline_value": float(pipeline_val),
        "recent_activities": [
            {
                "id": a.id,
                "lead_id": a.lead_id,
                "activity_type": a.activity_type,
                "title": getattr(a, "title", a.activity_type),
                "description": a.description,
                "created_at": a.created_at
            }
            for a in activities
        ]
    }

@router.get("/data-quality")
async def get_data_quality_dashboard(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Database Data Quality & Provenance Dashboard:
    Returns complete stage counts and quality ratios.
    """
    total_leads_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id)
    total_leads = (await db.execute(total_leads_q)).scalar() or 0

    identity_verified_q = (
        select(func.count(Lead.id))
        .join(Company, Lead.company_id == Company.id)
        .where(Lead.organization_id == org.id, Company.identity_verification_status.in_(["HIGH", "MEDIUM"]))
    )
    identity_verified_count = (await db.execute(identity_verified_q)).scalar() or 0

    web_verified_q = (
        select(func.count(Lead.id))
        .join(Company, Lead.company_id == Company.id)
        .join(Website, Website.company_id == Company.id)
        .where(Lead.organization_id == org.id, Website.website_official_verified == True)
    )
    website_verified_count = (await db.execute(web_verified_q)).scalar() or 0

    audit_complete_q = (
        select(func.count(Lead.id))
        .join(Company, Lead.company_id == Company.id)
        .join(Website, Website.company_id == Company.id)
        .join(WebsiteAudit, WebsiteAudit.website_id == Website.id)
        .where(Lead.organization_id == org.id, WebsiteAudit.audit_status == "AUDIT_COMPLETE")
    )
    audit_complete_count = (await db.execute(audit_complete_q)).scalar() or 0

    opp_detected_q = (
        select(func.count(func.distinct(ServiceNeedEvidence.lead_id)))
        .join(Lead, ServiceNeedEvidence.lead_id == Lead.id)
        .where(Lead.organization_id == org.id)
    )
    opp_detected_count = (await db.execute(opp_detected_q)).scalar() or 0

    intent_known_q = (
        select(func.count(Lead.id))
        .join(LeadScore, Lead.id == LeadScore.lead_id)
        .where(Lead.organization_id == org.id, LeadScore.buying_intent != "UNKNOWN")
    )
    intent_known_count = (await db.execute(intent_known_q)).scalar() or 0

    contactable_q = (
        select(func.count(Lead.id))
        .join(Company, Lead.company_id == Company.id)
        .outerjoin(Contact, Contact.company_id == Company.id)
        .where(Lead.organization_id == org.id, or_(Company.business_email.isnot(None), Contact.email.isnot(None)))
    )
    contactable_count = (await db.execute(contactable_q)).scalar() or 0

    qualified_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.is_qualified == True)
    qualified_count = (await db.execute(qualified_q)).scalar() or 0

    sales_ready_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.is_sales_ready == True)
    sales_ready_count = (await db.execute(sales_ready_q)).scalar() or 0

    # Ratios
    src_prov_q = (
        select(func.count(func.distinct(FieldProvenanceRecord.entity_id)))
        .where(FieldProvenanceRecord.organization_id == org.id, FieldProvenanceRecord.entity_type == "company")
    )
    src_prov_count = (await db.execute(src_prov_q)).scalar() or 0

    conflicts_q = (
        select(func.count(Company.id))
        .where(Company.organization_id == org.id, Company.has_conflicts == True)
    )
    conflicts_count = (await db.execute(conflicts_q)).scalar() or 0

    fresh_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.freshness_state == "FRESH")
    fresh_count = (await db.execute(fresh_q)).scalar() or 0

    stale_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.freshness_state.in_(["STALE", "EXPIRED"]))
    stale_count = (await db.execute(stale_q)).scalar() or 0

    recheck_q = select(func.count(Lead.id)).where(Lead.organization_id == org.id, Lead.review_status == "NEEDS_RECHECK")
    recheck_count = (await db.execute(recheck_q)).scalar() or 0

    # Percentage calculations
    def pct(val, denom):
        return round((val / denom * 100), 1) if denom > 0 else 0.0

    return {
        "total_discovered": total_leads,
        "identity_verified": identity_verified_count,
        "website_verified": website_verified_count,
        "audit_complete": audit_complete_count,
        "opportunity_detected": opp_detected_count,
        "intent_known": intent_known_count,
        "intent_unknown": max(0, total_leads - intent_known_count),
        "contactable": contactable_count,
        "qualified": qualified_count,
        "sales_ready": sales_ready_count,
        
        "percentages": {
            "source_provenance_rate": pct(src_prov_count, total_leads),
            "website_verification_rate": pct(website_verified_count, total_leads),
            "contact_provenance_rate": pct(contactable_count, total_leads),
            "fresh_rate": pct(fresh_count, total_leads),
            "stale_rate": pct(stale_count, total_leads),
            "conflicting_rate": pct(conflicts_count, total_leads),
            "recheck_rate": pct(recheck_count, total_leads)
        }
    }

@router.get("/opportunities-distribution")
async def get_opportunities_distribution(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Lead.primary_opportunity, func.count(Lead.id))
        .where(Lead.organization_id == org.id, Lead.primary_opportunity.isnot(None))
        .group_by(Lead.primary_opportunity)
    )
    res = await db.execute(query)
    rows = res.all()
    return [{"opportunity": opp or "Unknown", "count": count} for opp, count in rows]
@router.get("/source-coverage")
async def get_source_coverage(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Source Coverage & Adapter Health Dashboard:
    Tracks metrics per public discovery source.
    """
    from backend.app.models.discovery import DiscoveryJob, LeadSourceConfig

    # Fetch sources
    src_stmt = select(LeadSourceConfig).where(LeadSourceConfig.organization_id == org.id)
    sources = (await db.execute(src_stmt)).scalars().all()

    # Pre-populate default adapters if none registered
    if not sources:
        default_sources = [
            {"name": "OpenStreetMap Adapter", "source_type": "OpenStreetMap", "is_enabled": True, "rate_limit_per_min": 60},
            {"name": "Public Registries", "source_type": "Public Registries", "is_enabled": True, "rate_limit_per_min": 30},
            {"name": "Public Directories", "source_type": "Public Directories", "is_enabled": True, "rate_limit_per_min": 45},
            {"name": "RFP / Tender Pages", "source_type": "RFP / Tender Pages", "is_enabled": True, "rate_limit_per_min": 20}
        ]
        for ds in default_sources:
            sc = LeadSourceConfig(organization_id=org.id, **ds)
            db.add(sc)
        await db.commit()
        sources = (await db.execute(src_stmt)).scalars().all()

    coverage_list = []
    for s in sources:
        # Aggregate job stats for this source
        job_stmt = select(DiscoveryJob).where(DiscoveryJob.organization_id == org.id, DiscoveryJob.sources_used.ilike(f"%{s.source_type}%"))
        jobs = (await db.execute(job_stmt)).scalars().all()

        tot_disc = sum(j.discovered_count for j in jobs)
        tot_new = sum(j.new_businesses_count for j in jobs)
        tot_dups = sum(j.duplicates_count for j in jobs)
        tot_web = sum(j.websites_found_count for j in jobs)
        tot_web_ver = sum(getattr(j, "websites_verified_count", 0) for j in jobs)
        tot_cont = sum(j.contacts_found_count for j in jobs)
        tot_errs = sum(1 for j in jobs if j.status == "FAILED")

        last_success = max([j.completed_at for j in jobs if j.status == "COMPLETED" and j.completed_at], default=None)

        coverage_list.append({
            "source": s.source_type,
            "name": s.name,
            "is_enabled": s.is_enabled,
            "status": "OPERATIONAL" if s.is_enabled else "DISABLED",
            "records_discovered": tot_disc,
            "records_accepted": tot_new,
            "duplicates": tot_dups,
            "rejected": 0,
            "websites_found": tot_web,
            "websites_verified": tot_web_ver,
            "contacts_found": tot_cont,
            "errors": tot_errs,
            "last_successful_run": last_success.isoformat() if last_success else None,
            "last_checked": s.last_run_at.isoformat() if getattr(s, "last_run_at", None) else None,
            "rate_limit": f"{s.rate_limit_per_min} req/min"
        })

    return coverage_list

@router.get("/rejection-reasons")
async def get_rejection_reasons(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns aggregated breakdown of why discovered records did not reach Qualified/Sales-Ready.
    """
    from backend.app.models.discovery import DiscoveryJob
    stmt = select(DiscoveryJob).where(DiscoveryJob.organization_id == org.id)
    jobs = (await db.execute(stmt)).scalars().all()

    aggregated = {
        "NO_WEBSITE": 0,
        "BROKEN_WEBSITE": 0,
        "PARKED_DOMAIN": 0,
        "IDENTITY_MISMATCH": 0,
        "LOW_DATA_CONFIDENCE": 0,
        "AUDIT_FAILED": 0,
        "NO_SERVICE_EVIDENCE": 0,
        "NO_CONTACT": 0,
        "CONFLICT": 0,
        "STALE_DATA": 0
    }

    for j in jobs:
        if getattr(j, "rejection_reasons_json", None):
            try:
                r_dict = json.loads(j.rejection_reasons_json)
                for k, v in r_dict.items():
                    if k in aggregated:
                        aggregated[k] += v
            except Exception:
                pass

    return [{"reason": k, "count": v} for k, v in aggregated.items() if v > 0]

@router.get("/source-performance")
async def get_source_performance(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Source Performance Ranking:
    Computes yield rates per discovery adapter.
    """
    from backend.app.models.discovery import DiscoveryJob, LeadSourceConfig

    src_stmt = select(LeadSourceConfig).where(LeadSourceConfig.organization_id == org.id)
    sources = (await db.execute(src_stmt)).scalars().all()

    def pct(num, den):
        return round((num / den * 100), 1) if den > 0 else 0.0

    perf_list = []
    for s in sources:
        job_stmt = select(DiscoveryJob).where(DiscoveryJob.organization_id == org.id, DiscoveryJob.sources_used.ilike(f"%{s.source_type}%"))
        jobs = (await db.execute(job_stmt)).scalars().all()

        disc = sum(j.discovered_count for j in jobs)
        uniq = sum(j.new_businesses_count for j in jobs)
        web_ver = sum(getattr(j, "websites_verified_count", 0) for j in jobs)
        aud_comp = sum(getattr(j, "audits_completed_count", 0) for j in jobs)
        cont = sum(j.contacts_found_count for j in jobs)
        qual = sum(j.qualified_leads_count for j in jobs)
        sr = sum(getattr(j, "sales_ready_count", 0) for j in jobs)
        dups = sum(j.duplicates_count for j in jobs)

        perf_list.append({
            "source": s.source_type,
            "discovered_count": disc,
            "unique_count": uniq,
            "identity_verification_rate": pct(web_ver, uniq),
            "website_verification_rate": pct(web_ver, uniq),
            "audit_completion_rate": pct(aud_comp, uniq),
            "contact_rate": pct(cont, uniq),
            "qualification_rate": pct(qual, uniq),
            "sales_ready_rate": pct(sr, uniq),
            "duplicate_rate": pct(dups, disc)
        })

    return perf_list

@router.get("/geographic-coverage")
async def get_geographic_coverage(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns country and city distribution of verified leads.
    """
    stmt = (
        select(Company.country, func.count(Company.id))
        .where(Company.organization_id == org.id)
        .group_by(Company.country)
    )
    rows = (await db.execute(stmt)).all()
    return [{"country": r[0] or "Unknown", "count": r[1]} for r in rows]


