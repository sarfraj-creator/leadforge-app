import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.email import EmailThread, EmailMessage, EmailEvent, UnsubscribeRecord
from backend.app.models.lead import Lead
from backend.app.models.company import Company
from backend.app.models.crm import Activity
from backend.app.models.campaign import CampaignLead
from backend.app.services.ai.prompt_engine import prompt_engine
from backend.app.services.email.sender import email_sender

router = APIRouter(prefix="/inbox", tags=["Unified Inbox"])

@router.get("/threads")
async def list_threads(
    folder: str = Query("inbox", enum=["inbox", "sent", "replies", "bounces", "unsubscribes"]),
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    query = select(EmailThread).where(EmailThread.organization_id == org.id)
    
    if folder == "replies":
        query = query.where(EmailThread.reply_classification.isnot(None))
    elif folder == "unsubscribes":
        query = query.where(EmailThread.reply_classification == "Unsubscribe")
    elif folder == "bounces":
        query = query.where(EmailThread.status == "BOUNCED")
        
    query = query.order_by(desc(EmailThread.last_message_at))
    res = await db.execute(query)
    threads = res.scalars().all()
    
    results = []
    for t in threads:
        comp_name = None
        if t.lead_id:
            lead = await db.get(Lead, t.lead_id)
            if lead:
                comp = await db.get(Company, lead.company_id)
                comp_name = comp.business_name if comp else None
                
        # Load messages
        m_res = await db.execute(select(EmailMessage).where(EmailMessage.thread_id == t.id).order_by(EmailMessage.created_at))
        messages = m_res.scalars().all()
        
        results.append({
            "id": t.id,
            "lead_id": t.lead_id,
            "company_name": comp_name,
            "subject": t.subject,
            "recipient_email": t.recipient_email,
            "status": t.status,
            "reply_classification": t.reply_classification,
            "reply_sentiment_score": t.reply_sentiment_score,
            "last_message_at": t.last_message_at.isoformat(),
            "messages": [
                {
                    "id": m.id,
                    "direction": m.direction,
                    "from_email": m.from_email,
                    "to_email": m.to_email,
                    "subject": m.subject,
                    "body_text": m.body_text,
                    "status": m.status,
                    "sent_at": m.sent_at.isoformat() if m.sent_at else None,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ]
        })
    return results

@router.post("/threads/{thread_id}/simulate-inbound")
async def simulate_inbound_reply(
    thread_id: int,
    payload: Dict[str, str],
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Simulates receiving an inbound email reply to demonstrate the AI classification
    and automatic sequence stopping workflow.
    """
    thread = await db.get(EmailThread, thread_id)
    if not thread or thread.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    inbound_text = payload.get("body_text", "Yes, we are interested in discussing a website redesign. Please send over your availability for a call.")
    
    # 1. AI Reply Classification
    classification_res = await prompt_engine.classify_reply(
        inbound_body=inbound_text,
        subject=thread.subject
    )
    
    category = classification_res.get("classification", "Interested")
    sentiment = float(classification_res.get("sentiment", 0.8))
    
    # 2. Record Message
    msg = EmailMessage(
        thread_id=thread.id,
        direction="INBOUND",
        from_email=thread.recipient_email,
        to_email=email_sender.from_email,
        subject="Re: " + thread.subject,
        body_text=inbound_text,
        status="DELIVERED",
        sent_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(msg)
    
    thread.reply_classification = category
    thread.reply_sentiment_score = sentiment
    thread.last_message_at = datetime.datetime.now(datetime.timezone.utc)
    thread.status = "REPLIED"
    
    # 3. CRM Workflow & Sequence Stopping
    if thread.lead_id:
        lead = await db.get(Lead, thread.lead_id)
        if lead:
            # Automatically Stop Campaign Sequences
            c_leads = await db.execute(select(CampaignLead).where(CampaignLead.lead_id == lead.id))
            for cl in c_leads.scalars().all():
                cl.status = "REPLIED" if category in ["Interested", "Meeting Request", "Question"] else "COMPLETED"
                
            if category in ["Interested", "Meeting Request", "Pricing Request"]:
                lead.stage = "Interested"
                lead.needs_review = False
                db.add(Activity(
                    organization_id=org.id,
                    lead_id=lead.id,
                    activity_type="EMAIL_REPLY",
                    title=f"Positive Reply Received ({category})",
                    description=f"Prospect responded positively: '{inbound_text[:100]}...'. Lead stage updated to 'Interested' and outreach sequence stopped."
                ))
            elif category == "Unsubscribe":
                lead.is_do_not_contact = True
                lead.stage = "Do Not Contact"
                db.add(UnsubscribeRecord(
                    organization_id=org.id,
                    email=thread.recipient_email,
                    reason="Opted out via reply"
                ))
                db.add(Activity(
                    organization_id=org.id,
                    lead_id=lead.id,
                    activity_type="UNSUBSCRIBE",
                    title="Prospect Opted Out",
                    description="Sequence stopped and added to Do Not Contact list."
                ))
                
    await db.commit()
    return {
        "message": "Inbound reply processed",
        "classification": category,
        "sentiment": sentiment,
        "lead_stage": lead.stage if thread.lead_id and lead else None
    }
