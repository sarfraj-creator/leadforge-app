import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.discovery import DiscoveryJob, LeadSourceConfig
from backend.app.schemas.common import DiscoveryJobCreate, DiscoveryJobOut, NLPQueryRequest
from backend.app.workers.task_runner import task_runner
from backend.app.services.ai.prompt_engine import prompt_engine
from backend.app.services.discovery.registry import source_registry

router = APIRouter(prefix="/discovery", tags=["Discovery Engine"])

@router.get("/sources/health")
async def get_sources_health():
    """Returns live latency, connectivity, rate limits, and availability for all discovery adapters."""
    return await source_registry.check_all_health()

@router.post("/campaigns", response_model=DiscoveryJobOut)
async def create_discovery_campaign(
    req: DiscoveryJobCreate,
    bg_tasks: BackgroundTasks,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    sources_str = ",".join(req.sources_used) if req.sources_used else "OpenStreetMap"
    loc = req.location.strip() or "WORLDWIDE"
    
    job = DiscoveryJob(
        organization_id=org.id,
        name=req.name,
        location=loc,
        industry=req.industry.strip() or "restaurant",
        keywords=req.keywords,
        freshness_days=req.freshness_days,
        min_lead_score=req.min_lead_score,
        max_leads=req.max_leads,
        sources_used=sources_str,
        natural_language_query=req.natural_language_query,
        status="QUEUED"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Launch background discovery pipeline
    bg_tasks.add_task(task_runner.run_discovery_pipeline, job.id)
    
    return job

@router.get("/jobs", response_model=List[DiscoveryJobOut])
async def list_discovery_jobs(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DiscoveryJob).where(DiscoveryJob.organization_id == org.id).order_by(desc(DiscoveryJob.created_at))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/jobs/{job_id}", response_model=DiscoveryJobOut)
async def get_discovery_job(
    job_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(DiscoveryJob, job_id)
    if not job or job.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Discovery job not found")
    return job

from pydantic import BaseModel
from backend.app.services.discovery.intent_hunter import IntentPostHunter
from backend.app.models.company import Company
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore
from backend.app.core.deduplication import compute_dedup_hash, normalize_business_name
import datetime

class ImportIntentPostRequest(BaseModel):
    author_name: str
    author_title: Optional[str] = "Executive / Founder"
    author_linkedin_url: Optional[str] = None
    company_name: Optional[str] = None
    post_url: Optional[str] = None
    post_snippet: Optional[str] = None
    intent_tag: Optional[str] = "Web Development"
    urgency: Optional[str] = "HOT"
    pitch_hook: Optional[str] = None

@router.get("/intent-posts")
async def search_social_intent_posts(
    keyword: Optional[str] = "wordpress developer",
    category: Optional[str] = None,
    limit: int = 20
):
    """
    Searches live LinkedIn, Twitter/X, and Google Search indexes for buyer intent posts,
    extracting authors, quoted requests, and personalized icebreaker pitch hooks.
    """
    posts = await IntentPostHunter.search_posts(
        keyword=keyword or "web developer",
        category=category,
        limit=min(limit, 50)
    )
    return {
        "keyword": keyword,
        "category": category,
        "total": len(posts),
        "posts": posts
    }

@router.post("/intent-posts/import")
async def import_intent_post_to_crm(
    req: ImportIntentPostRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Imports a discovered social intent post directly into the CRM as a Qualified Hot Lead.
    Creates the Company, Contact with LinkedIn profile, LeadScore (HOT), and attaches the pitch hook.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    comp_name = req.company_name or f"{req.author_name}'s Business"
    if comp_name == "Prospective Client":
        comp_name = f"{req.author_name}'s Venture"

    dedup = compute_dedup_hash(business_name=comp_name)

    # 1. Company
    stmt = select(Company).where(
        Company.organization_id == org.id,
        Company.dedup_hash == dedup
    )
    res = await db.execute(stmt)
    company = res.scalar_one_or_none()

    if not company:
        company = Company(
            organization_id=org.id,
            business_name=comp_name,
            industry=req.intent_tag or "Digital Services",
            category=req.intent_tag or "Web Development",
            source="SocialIntent",
            source_url=req.post_url,
            confidence=0.95,
            dedup_hash=dedup,
            company_observed_at=now,
            discovered_at=now,
            last_seen_at=now,
            last_checked_at=now
        )
        db.add(company)
        await db.flush()

    # 2. Contact Person with LinkedIn URL
    first_name = req.author_name.split()[0] if req.author_name else "Contact"
    last_name = " ".join(req.author_name.split()[1:]) if len(req.author_name.split()) > 1 else ""

    contact = Contact(
        company_id=company.id,
        first_name=first_name,
        last_name=last_name,
        full_name=req.author_name,
        job_title=req.author_title or "Founder / Executive",
        is_decision_maker=True,
        linkedin_url=req.author_linkedin_url,
        source="SocialIntent",
        source_url=req.post_url,
        confidence=0.95,
        observed_at=now
    )
    db.add(contact)
    await db.flush()

    # 3. Create Lead in Qualified / Hot Stage
    lead = Lead(
        organization_id=org.id,
        company_id=company.id,
        pipeline_stage="QUALIFIED",
        stage="Qualified",
        review_status="APPROVED",
        needs_review=False,
        is_qualified=True,
        is_sales_ready=True,
        primary_opportunity=f"Live Request: {req.intent_tag}",
        recommended_service=req.intent_tag,
        data_quality_score=95,
        freshness_state="FRESH",
        review_notes=f"🔥 High Intent Signal ({req.urgency}): \"{req.post_snippet}\"\n\nSuggested Pitch: {req.pitch_hook}",
        created_at=now
    )
    db.add(lead)
    await db.flush()

    # 4. Lead Score
    score = LeadScore(
        lead_id=lead.id,
        total_score=95 if req.urgency == "HOT" else 88,
        category="HOT" if req.urgency == "HOT" else "HIGH",
        opportunity_score=95,
        intent_score=95,
        buying_intent="HIGH",
        contactability_score=90,
        business_fit_score=90,
        data_confidence_score=95,
        explanation=f"Live Buyer Intent Post: {req.post_snippet[:120]}...",
        calculated_at=now
    )
    db.add(score)
    await db.commit()

    return {
        "success": True,
        "lead_id": lead.id,
        "company_id": company.id,
        "contact_id": contact.id,
        "author_name": req.author_name,
        "message": f"Successfully imported {req.author_name} ({comp_name}) into CRM Leads as a HOT lead!"
    }

@router.post("/nlp-interpret")
async def interpret_nlp_query(req: NLPQueryRequest):
    """
    Translates natural language prospecting query into structured parameters with preview.
    """
    try:
        interpretation = await prompt_engine.interpret_natural_language_query(req.query)
        return {
            "query": req.query,
            "interpreted_criteria": interpretation,
            "ready_to_launch": True
        }
    except Exception as e:
        return {
            "query": req.query,
            "interpreted_criteria": {
                "industry": "restaurant",
                "location": "WORLDWIDE",
                "opportunity_type": "Website Modernization",
                "min_lead_score": 60,
                "freshness_days": 7,
                "max_leads": 50
            },
            "ready_to_launch": True
        }

