from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.campaign import Campaign, SequenceStep, CampaignLead
from backend.app.schemas.common import CampaignCreate, CampaignOut, SequenceStepOut
from backend.app.workers.sequence_runner import sequence_runner

router = APIRouter(prefix="/campaigns", tags=["Outreach Campaigns"])

class AutoEnrollRequest(BaseModel):
    category: Optional[str] = None # HAS_WEBSITE_REDESIGN | NO_WEBSITE_NEW_BUILD | BUYER_INTENT_POST | None (All)
    lead_ids: Optional[List[int]] = None

class AutoLaunchRequest(BaseModel):
    category: Optional[str] = "HAS_WEBSITE_REDESIGN"
    auto_dispatch_initial: bool = True

@router.get("", response_model=List[CampaignOut])
async def list_campaigns(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Campaign).where(Campaign.organization_id == org.id).order_by(desc(Campaign.created_at))
    res = await db.execute(stmt)
    campaigns = res.scalars().all()
    
    results = []
    for c in campaigns:
        # Load steps
        st_res = await db.execute(select(SequenceStep).where(SequenceStep.campaign_id == c.id).order_by(SequenceStep.step_number))
        steps = st_res.scalars().all()
        
        # Count enrolled leads
        enrolled_res = await db.execute(select(func.count(CampaignLead.id)).where(CampaignLead.campaign_id == c.id))
        enrolled_count = enrolled_res.scalar() or 0
        
        results.append(CampaignOut(
            id=c.id,
            name=c.name,
            description=c.description,
            status=c.status,
            daily_limit=c.daily_limit,
            hourly_limit=c.hourly_limit,
            approval_mode=c.approval_mode,
            enrolled_leads_count=enrolled_count,
            created_at=c.created_at,
            sequence_steps=[
                SequenceStepOut(
                    id=s.id,
                    step_number=s.step_number,
                    delay_days=s.delay_days,
                    subject_template=s.subject_template,
                    body_template=s.body_template,
                    use_ai_personalization=s.use_ai_personalization,
                    is_active=s.is_active
                )
                for s in steps
            ]
        ))
    return results

@router.post("", response_model=CampaignOut)
async def create_campaign(
    req: CampaignCreate,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    camp = Campaign(
        organization_id=org.id,
        name=req.name,
        description=req.description,
        daily_limit=req.daily_limit,
        hourly_limit=req.hourly_limit,
        approval_mode=req.approval_mode,
        status="RUNNING"
    )
    db.add(camp)
    await db.flush()
    
    # Add sequence steps
    if req.steps:
        for st in req.steps:
            db.add(SequenceStep(
                campaign_id=camp.id,
                step_number=st.step_number,
                delay_days=st.delay_days,
                subject_template=st.subject_template,
                body_template=st.body_template,
                use_ai_personalization=st.use_ai_personalization
            ))
    else:
        # Default 4-step sequence
        from backend.app.workers.sequence_runner import DEFAULT_SEQUENCE_STEPS
        for s in DEFAULT_SEQUENCE_STEPS:
            db.add(SequenceStep(
                campaign_id=camp.id,
                step_number=s["step_number"],
                delay_days=s["delay_days"],
                subject_template=s["subject_template"],
                body_template=s["body_template"],
                use_ai_personalization=s["use_ai_personalization"]
            ))
            
    await db.commit()
    await db.refresh(camp)
    
    st_res = await db.execute(select(SequenceStep).where(SequenceStep.campaign_id == camp.id).order_by(SequenceStep.step_number))
    steps = st_res.scalars().all()
    
    return CampaignOut(
        id=camp.id,
        name=camp.name,
        description=camp.description,
        status=camp.status,
        daily_limit=camp.daily_limit,
        hourly_limit=camp.hourly_limit,
        approval_mode=camp.approval_mode,
        enrolled_leads_count=0,
        created_at=camp.created_at,
        sequence_steps=[
            SequenceStepOut(
                id=s.id,
                step_number=s.step_number,
                delay_days=s.delay_days,
                subject_template=s.subject_template,
                body_template=s.body_template,
                use_ai_personalization=s.use_ai_personalization,
                is_active=s.is_active
            )
            for s in steps
        ]
    )

@router.post("/auto-enroll")
async def auto_enroll_campaign(
    req: AutoEnrollRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    1-Click enrolls leads by category into the default 4-step autonomous sequence (Day 0, 3, 7, 14).
    """
    res = await sequence_runner.auto_enroll_leads(
        session=db,
        org_id=org.id,
        lead_ids=req.lead_ids,
        category=req.category
    )
    return res

@router.post("/run-cycle")
async def run_sequence_cycle(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a processing pass of all due sequence steps with document attachments & CRM logging.
    """
    res = await sequence_runner.process_due_steps(session=db, org_id=org.id)
    return res

@router.post("/auto-launch")
async def auto_launch_autonomous_pipeline(
    req: AutoLaunchRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    End-to-End Autonomous AI Launcher:
    1. Enrolls filtered category leads into the 4-step sequence
    2. Immediately triggers initial Day 0 dispatch with attached R&D Audit Reports
    """
    enroll_res = await sequence_runner.auto_enroll_leads(
        session=db,
        org_id=org.id,
        category=req.category
    )
    
    dispatch_res = {"processed": 0, "sent": 0, "skipped": 0}
    if req.auto_dispatch_initial:
        dispatch_res = await sequence_runner.process_due_steps(session=db, org_id=org.id)
        
    return {
        "status": "SUCCESS",
        "category": req.category,
        "enrolled": enroll_res["enrolled_count"],
        "dispatched": dispatch_res["sent"],
        "message": f"Autonomous pipeline active: {enroll_res['enrolled_count']} leads enrolled in 4-step sequence (Day 0, 3, 7, 14)."
    }
