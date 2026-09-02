import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org, get_current_user
from backend.app.models.user import Organization, User
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.company import Company
from backend.app.models.contact import Contact
from backend.app.models.crm import CRMStage, Deal, Task, Note, Activity
from backend.app.schemas.common import DealCreate, DealOut, TaskCreate, TaskOut, NoteCreate, NoteOut

router = APIRouter(prefix="/crm", tags=["CRM & Pipeline"])

@router.get("/kanban")
async def get_kanban_board(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    # Fetch stages
    s_stmt = select(CRMStage).where(CRMStage.organization_id == org.id).order_by(CRMStage.order)
    s_res = await db.execute(s_stmt)
    stages = s_res.scalars().all()
    
    # If empty, create default stages
    if not stages:
        default_stages = [
            ("New", 0, "#64748B"),
            ("Qualified", 1, "#3B82F6"),
            ("Contacted", 2, "#8B5CF6"),
            ("Follow-up", 3, "#EC4899"),
            ("Interested", 4, "#F59E0B"),
            ("Meeting", 5, "#10B981"),
            ("Proposal", 6, "#06B6D4"),
            ("Won", 7, "#22C55E"),
            ("Lost", 8, "#EF4444"),
        ]
        for name, order, color in default_stages:
            db.add(CRMStage(
                organization_id=org.id,
                name=name,
                order=order,
                color_code=color,
                is_won_stage=(name == "Won"),
                is_lost_stage=(name == "Lost")
            ))
        await db.commit()
        s_res = await db.execute(s_stmt)
        stages = s_res.scalars().all()
        
    # Fetch all active leads in org
    l_stmt = select(Lead).where(Lead.organization_id == org.id, Lead.is_archived == False)
    l_res = await db.execute(l_stmt)
    leads = l_res.scalars().all()
    
    board = []
    for stage in stages:
        stage_leads = [l for l in leads if l.stage == stage.name or (stage.name == "Qualified" and l.stage in ["Qualified", "Sales Ready"])]
        cards = []
        for l in stage_leads:
            comp = await db.get(Company, l.company_id)
            score_res = await db.execute(select(LeadScore).where(LeadScore.lead_id == l.id))
            score_obj = score_res.scalar_one_or_none()
            
            cont_res = await db.execute(select(Contact).where(Contact.company_id == l.company_id).limit(1))
            cont = cont_res.scalar_one_or_none()
            
            cards.append({
                "id": l.id,
                "company_id": comp.id,
                "company_name": comp.business_name if comp else "Unknown",
                "city": comp.city if comp else None,
                "website": comp.website if comp else None,
                "opportunity": l.primary_opportunity,
                "recommended_service": l.recommended_service,
                "score": score_obj.total_score if score_obj else 0,
                "score_category": score_obj.category if score_obj else "LOW",
                "contact_name": cont.full_name if cont else None,
                "contact_email": cont.email if cont else None,
                "freshness_state": l.freshness_state,
                "created_at": l.created_at.isoformat()
            })
            
        board.append({
            "stage_id": stage.id,
            "name": stage.name,
            "color_code": stage.color_code,
            "order": stage.order,
            "count": len(cards),
            "cards": cards
        })
        
    return board

@router.get("/deals", response_model=List[DealOut])
async def list_deals(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Deal).where(Deal.organization_id == org.id).order_by(desc(Deal.created_at))
    res = await db.execute(stmt)
    deals = res.scalars().all()
    
    results = []
    for d in deals:
        lead = await db.get(Lead, d.lead_id)
        comp_name = None
        if lead:
            comp = await db.get(Company, lead.company_id)
            comp_name = comp.business_name if comp else None
            
        results.append(DealOut(
            id=d.id,
            lead_id=d.lead_id,
            title=d.title,
            value=d.value,
            currency=d.currency,
            stage=d.stage,
            expected_close_date=d.expected_close_date,
            notes=d.notes,
            company_name=comp_name
        ))
    return results

@router.post("/deals", response_model=DealOut)
async def create_deal(
    req: DealCreate,
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    lead = await db.get(Lead, req.lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    deal = Deal(
        organization_id=org.id,
        lead_id=lead.id,
        title=req.title,
        value=req.value,
        currency=req.currency,
        stage=req.stage,
        expected_close_date=datetime.datetime.combine(req.expected_close_date, datetime.time()) if req.expected_close_date else None,
        notes=req.notes,
        owner_user_id=user.id
    )
    db.add(deal)
    
    db.add(Activity(
        organization_id=org.id,
        lead_id=lead.id,
        activity_type="DEAL_CREATED",
        title=f"Deal Created: {req.title}",
        description=f"Value: {req.currency} {req.value:,.2f} · Stage: {req.stage}"
    ))
    
    await db.commit()
    await db.refresh(deal)
    
    comp = await db.get(Company, lead.company_id)
    return DealOut(
        id=deal.id,
        lead_id=deal.lead_id,
        title=deal.title,
        value=deal.value,
        currency=deal.currency,
        stage=deal.stage,
        expected_close_date=deal.expected_close_date,
        notes=deal.notes,
        company_name=comp.business_name if comp else None
    )

@router.get("/tasks", response_model=List[TaskOut])
async def list_tasks(
    status_filter: Optional[str] = None,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    query = select(Task).where(Task.organization_id == org.id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    query = query.order_by(Task.due_date)
    res = await db.execute(query)
    tasks = res.scalars().all()
    
    results = []
    for t in tasks:
        comp_name = None
        if t.lead_id:
            lead = await db.get(Lead, t.lead_id)
            if lead:
                comp = await db.get(Company, lead.company_id)
                comp_name = comp.business_name if comp else None
                
        results.append(TaskOut(
            id=t.id,
            lead_id=t.lead_id,
            title=t.title,
            description=t.description,
            task_type=t.task_type,
            due_date=t.due_date,
            priority=t.priority,
            status=t.status,
            created_at=t.created_at,
            company_name=comp_name
        ))
    return results

@router.post("/tasks", response_model=TaskOut)
async def create_task(
    req: TaskCreate,
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    task = Task(
        organization_id=org.id,
        lead_id=req.lead_id,
        title=req.title,
        description=req.description,
        task_type=req.task_type,
        due_date=req.due_date,
        priority=req.priority,
        status="Pending",
        assigned_to_user_id=user.id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.patch("/tasks/{task_id}/toggle")
async def toggle_task_status(
    task_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    task = await db.get(Task, task_id)
    if not task or task.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = "Completed" if task.status == "Pending" else "Pending"
    await db.commit()
    return {"message": "Task updated", "status": task.status}

@router.post("/notes", response_model=NoteOut)
async def add_note(
    req: NoteCreate,
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    note = Note(
        lead_id=req.lead_id,
        author_user_id=user.id,
        content=req.content
    )
    db.add(note)
    
    db.add(Activity(
        organization_id=org.id,
        lead_id=req.lead_id,
        activity_type="NOTE_ADDED",
        title="Note Added",
        description=req.content[:150]
    ))
    
    await db.commit()
    await db.refresh(note)
    return note
