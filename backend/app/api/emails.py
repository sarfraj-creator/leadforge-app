import datetime
import re
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.lead import Lead, LeadOpportunity
from backend.app.models.company import Company
from backend.app.models.contact import Contact
from backend.app.models.website import Website, WebsiteAudit, WebsiteAuditMetric, WebsiteIssue, WebsiteTechnology
from backend.app.models.email import EmailThread, EmailMessage, EmailEvent, UnsubscribeRecord
from backend.app.models.crm import Activity
from backend.app.schemas.common import EmailSendRequest, AIOutreachGenerateRequest
from backend.app.services.email.sender import email_sender
from backend.app.services.email.formatter import email_formatter
from backend.app.services.audit.report_generator import technical_report_generator
from backend.app.services.ai.prompt_engine import prompt_engine

router = APIRouter(prefix="/emails", tags=["Email Outreach"])

@router.post("/send")
async def send_email_endpoint(
    req: EmailSendRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    lead = await db.get(Lead, req.lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if lead.is_do_not_contact:
        raise HTTPException(status_code=400, detail="Lead is marked Do Not Contact")
        
    # Check if recipient is on unsubscribe suppression list
    unsub_res = await db.execute(select(UnsubscribeRecord).where(
        UnsubscribeRecord.organization_id == org.id,
        UnsubscribeRecord.email == req.to_email
    ))
    if unsub_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Recipient email is on the unsubscribe suppression list")

    comp = await db.get(Company, lead.company_id)
    comp_name = comp.business_name if comp else "Prospect"
    clean_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', comp_name)[:30]

    # Load audit data if available
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

    # Build R&D Report Document & MIME Attachment
    attachments = []
    attached_filename = f"Technical-Audit-Report-{clean_slug}.html"
    report_data = technical_report_generator.generate_report_data(
        lead=lead,
        company=comp,
        audit=aud,
        contacts=contacts,
        metrics=metrics,
        issues=issues,
        technologies=technologies
    )
    html_report_doc = technical_report_generator.render_html_report(report_data)

    if req.attach_report:
        attachments.append({
            "filename": attached_filename,
            "content": html_report_doc,
            "content_type": "text/html"
        })

    # Prepare Rich HTML email body
    scores_dict = report_data.get("scores") if aud else None
    primary_issue = issues[0].evidence if issues else None

    body_html = req.body_html
    if not body_html:
        body_html = email_formatter.format_html_email(
            body_text=req.body_text,
            subject=req.subject,
            company_name=comp_name,
            scores=scores_dict,
            observed_issue=primary_issue,
            recommended_service=lead.recommended_service or lead.primary_opportunity,
            attached_report_name=attached_filename if req.attach_report else None,
            report_url=f"/api/audits/lead/{lead.id}/report/html"
        )
        
    # Dispatch email with MIME attachments & HTML
    success, msg_id, err = await email_sender.send_email(
        to_email=req.to_email,
        subject=req.subject,
        body_text=req.body_text,
        body_html=body_html,
        attachments=attachments if attachments else None
    )
    
    # Create or update Thread
    stmt_t = select(EmailThread).where(EmailThread.lead_id == lead.id)
    res_t = await db.execute(stmt_t)
    thread = res_t.scalar_one_or_none()
    if not thread:
        thread = EmailThread(
            organization_id=org.id,
            lead_id=lead.id,
            subject=req.subject,
            recipient_email=req.to_email,
            status="ACTIVE"
        )
        db.add(thread)
        await db.flush()
        
    msg = EmailMessage(
        thread_id=thread.id,
        direction="OUTBOUND",
        from_email=email_sender.from_email,
        to_email=req.to_email,
        subject=req.subject,
        body_text=req.body_text,
        body_html=body_html,
        status="SENT" if success else "FAILED",
        error_message=err,
        sent_at=datetime.datetime.now(datetime.timezone.utc) if success else None
    )
    db.add(msg)
    await db.flush()
    
    if success:
        db.add(EmailEvent(message_id=msg.id, event_type="sent"))
        lead.stage = "Contacted"
        db.add(Activity(
            organization_id=org.id,
            lead_id=lead.id,
            activity_type="EMAIL_SENT",
            title=f"Outreach Sent to {req.to_email}",
            description=f"Subject: {req.subject} | Attached: {attached_filename if req.attach_report else 'None'}"
        ))
        
    await db.commit()
    return {
        "success": success,
        "message_id": msg_id,
        "error": err,
        "thread_id": thread.id,
        "attached_document": attached_filename if req.attach_report else None,
        "formatted_html": body_html
    }

@router.post("/generate-ai-outreach")
async def generate_ai_outreach(
    req: AIOutreachGenerateRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    lead = await db.get(Lead, req.lead_id)
    if not lead or lead.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    comp = await db.get(Company, lead.company_id)
    
    # Find primary contact
    cont_res = await db.execute(select(Contact).where(Contact.company_id == comp.id).limit(1))
    contact = cont_res.scalar_one_or_none()
    contact_name = (contact.full_name if (contact and contact.full_name) else None) or getattr(req, "contact_name", None) or "Business Owner"
    
    # Find primary audit issue & scores
    issue_text = "Mobile navigation layout and performance could be optimized."
    scores_dict = None
    web_res = await db.execute(select(Website).where(Website.company_id == comp.id))
    web_obj = web_res.scalar_one_or_none()
    if web_obj:
        aud_res = await db.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(desc(WebsiteAudit.created_at)))
        aud_obj = aud_res.scalars().first()
        if aud_obj:
            scores_dict = {
                "overall_score": aud_obj.overall_score,
                "mobile_score": aud_obj.mobile_score,
                "performance_score": aud_obj.performance_score,
                "seo_score": aud_obj.seo_score,
                "security_score": aud_obj.security_score
            }
            iss_res = await db.execute(select(WebsiteIssue).where(WebsiteIssue.audit_id == aud_obj.id).limit(1))
            iss_obj = iss_res.scalar_one_or_none()
            if iss_obj:
                issue_text = f"{iss_obj.title}: {iss_obj.evidence}"

    opp_type = getattr(req, "opportunity_type", None) or lead.primary_opportunity or "Website Redesign"
    rec_service = lead.recommended_service or "Mobile Responsive Redesign"
    
    # Generate AI outreach email
    result = await prompt_engine.generate_personalized_email(
        company_name=comp.business_name,
        contact_name=contact_name,
        website_url=comp.website,
        opportunity_type=opp_type,
        primary_issue=issue_text,
        recommended_service=rec_service
    )
    
    subject = result.get("subject", f"Quick question regarding {comp.business_name} website")
    body_text = f"{result.get('opening', 'Hi ' + contact_name + ',')}\n\n{result.get('problem', issue_text)}\n\n{result.get('value_proposition', 'We specialize in ' + rec_service + ' to capture more prospective inquiries.')}\n\n{result.get('cta', 'Would you be open to a 10-minute call this Thursday?')}\n\n{result.get('signature', 'Best regards,\nAlex Mercer\nAcme Growth Agency')}"

    clean_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', comp.business_name)[:30]
    attached_filename = f"Technical-Audit-Report-{clean_slug}.html"

    formatted_html = email_formatter.format_html_email(
        body_text=body_text,
        subject=subject,
        company_name=comp.business_name,
        scores=scores_dict,
        observed_issue=issue_text,
        recommended_service=rec_service,
        attached_report_name=attached_filename,
        report_url=f"/api/audits/lead/{lead.id}/report/html"
    )
    
    return {
        "subject": subject,
        "body_text": body_text,
        "body_html": formatted_html,
        "contact_email": contact.email if contact else comp.business_email,
        "contact_name": contact_name,
        "observed_issue": issue_text,
        "recommended_service": rec_service,
        "attached_report_name": attached_filename
    }
