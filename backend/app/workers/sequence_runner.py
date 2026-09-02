import datetime
import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from backend.app.models.campaign import Campaign, SequenceStep, CampaignLead
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.company import Company
from backend.app.models.contact import Contact
from backend.app.models.website import Website, WebsiteAudit, WebsiteIssue, WebsiteAuditMetric, WebsiteTechnology
from backend.app.models.email import EmailThread, EmailMessage, EmailEvent
from backend.app.models.crm import Activity
from backend.app.services.email.sender import email_sender
from backend.app.services.email.formatter import email_formatter
from backend.app.services.ai.prompt_engine import prompt_engine
from backend.app.services.audit.report_generator import technical_report_generator

# Default 4-Step Sequence Configuration (Day 0, Day 3, Day 7, Day 14)
DEFAULT_SEQUENCE_STEPS = [
    {
        "step_number": 1,
        "delay_days": 0, # Day 0: Immediate Initial Outreach with Audit Brief
        "subject_template": "Quick question regarding {{company_name}} website & mobile experience",
        "body_template": """Hi {{first_name}},

I was reviewing the digital presence for companies in {{city}} and ran a technical website audit on {{website}}.

Our engineering analysis identified {{primary_issue}}, which affects mobile smartphone inquiries and loading performance.

We prepared a complete technical R&D Audit Report with a step-by-step modernization blueprint for {{company_name}} (attached / referenced below):
• Service Recommendation: {{recommended_service}}
• Estimated Turnaround: 2-3 weeks
• Target ROI: 2.5x increase in conversion

Would you be open to a brief 10-minute call this Thursday to walk through the findings?

Best regards,
Alex Mercer
Acme Digital & Web Engineering""",
        "use_ai_personalization": True
    },
    {
        "step_number": 2,
        "delay_days": 3, # Day 3: First Follow-Up (Wireframe / Mockup Preview)
        "subject_template": "Wireframe idea for {{company_name}} website navigation",
        "body_template": """Hi {{first_name}},

Following up on my previous note regarding {{company_name}}'s website.

Our design team put together a quick wireframe concept addressing the {{primary_issue}} on {{website}}, making it significantly easier for mobile visitors to contact you.

Would you like me to send over the interactive preview link?

Best regards,
Alex Mercer""",
        "use_ai_personalization": True
    },
    {
        "step_number": 3,
        "delay_days": 7, # Day 7: Second Follow-Up (Competitor Benchmark / Case Study)
        "subject_template": "Benchmark insight for {{company_name}} in {{industry}}",
        "body_template": """Hi {{first_name}},

We recently helped another business in {{industry}} modernize their web architecture and resolve similar mobile and speed bottlenecks, resulting in a +42% lift in direct client inquiries.

I would be happy to share the specific framework we used to see if it makes sense for {{company_name}}.

Are you free for a quick 5-minute chat next Tuesday?

Best regards,
Alex Mercer""",
        "use_ai_personalization": True
    },
    {
        "step_number": 4,
        "delay_days": 14, # Day 14: Final Follow-Up (Polite Breakup / Future Reference)
        "subject_template": "Final check-in regarding {{company_name}}",
        "body_template": """Hi {{first_name}},

I know you are busy running {{company_name}}. I won't follow up further so I don't clutter your inbox.

If modernizing your website or improving your conversion funnel becomes a priority later this quarter, you can access your technical audit report anytime.

Wishing you continued growth!

Best regards,
Alex Mercer
Acme Digital & Web Engineering""",
        "use_ai_personalization": True
    }
]

class AutonomousSequenceRunner:
    """
    Executes automated, multi-day 3/7/14-day sequence follow-ups with AI personalized
    copy and attached technical R&D website audit documents.
    """

    async def get_or_create_default_campaign(self, session: AsyncSession, org_id: int) -> Campaign:
        res = await session.execute(
            select(Campaign).where(
                and_(Campaign.organization_id == org_id, Campaign.name.like("%Autonomous AI Follow-Up Engine%"))
            )
        )
        camp = res.scalars().first()
        if not camp:
            camp = Campaign(
                organization_id=org_id,
                name="[AUTO] Autonomous AI Follow-Up Engine (Day 0, 3, 7, 14)",
                description="Automated 4-step multi-day agency sequence with attached technical R&D audit briefs.",
                status="RUNNING",
                daily_limit=100,
                hourly_limit=25,
                approval_mode="AUTOMATIC"
            )
            session.add(camp)
            await session.flush()

            for s in DEFAULT_SEQUENCE_STEPS:
                session.add(SequenceStep(
                    campaign_id=camp.id,
                    step_number=s["step_number"],
                    delay_days=s["delay_days"],
                    subject_template=s["subject_template"],
                    body_template=s["body_template"],
                    use_ai_personalization=s["use_ai_personalization"],
                    is_active=True
                ))
            await session.flush()

        return camp

    async def auto_enroll_leads(
        self,
        session: AsyncSession,
        org_id: int,
        lead_ids: Optional[List[int]] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrolls leads into the 4-step sequence with Day 0 step due immediately.
        """
        camp = await self.get_or_create_default_campaign(session, org_id)

        query = select(Lead).where(
            and_(
                Lead.organization_id == org_id,
                Lead.is_do_not_contact == False
            )
        )
        if lead_ids:
            query = query.where(Lead.id.in_(lead_ids))

        res = await session.execute(query)
        leads = res.scalars().all()

        enrolled_count = 0
        now = datetime.datetime.now(datetime.timezone.utc)

        for l in leads:
            comp = await session.get(Company, l.company_id)
            score_res = await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))
            score_obj = score_res.scalar_one_or_none()

            lead_has_web = bool(comp and (comp.website or comp.domain))
            lead_has_intent = bool(score_obj and score_obj.buying_intent != "UNKNOWN")

            if category == "HAS_WEBSITE_REDESIGN" and not lead_has_web:
                continue
            elif category == "NO_WEBSITE_NEW_BUILD" and lead_has_web:
                continue
            elif category == "BUYER_INTENT_POST" and not lead_has_intent:
                continue

            # Check if already enrolled in campaign
            existing = await session.execute(
                select(CampaignLead).where(
                    and_(CampaignLead.campaign_id == camp.id, CampaignLead.lead_id == l.id)
                )
            )
            if existing.scalars().first():
                continue

            # Enroll with step 1 due immediately
            cl = CampaignLead(
                campaign_id=camp.id,
                lead_id=l.id,
                status="QUEUED",
                current_step=0,
                next_step_due_at=now,
                is_approved_by_user=True,
                enrolled_at=now
            )
            session.add(cl)
            enrolled_count += 1

        await session.commit()
        return {
            "campaign_id": camp.id,
            "campaign_name": camp.name,
            "enrolled_count": enrolled_count,
            "total_candidates": len(leads)
        }

    async def process_due_steps(self, session: AsyncSession, org_id: int) -> Dict[str, Any]:
        """
        Processes all due sequence steps across all active campaigns for the organization.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        camp = await self.get_or_create_default_campaign(session, org_id)

        # Query CampaignLeads due for processing
        res = await session.execute(
            select(CampaignLead).where(
                and_(
                    CampaignLead.campaign_id == camp.id,
                    CampaignLead.status.in_(["QUEUED", "IN_SEQUENCE", "APPROVED"]),
                    CampaignLead.next_step_due_at <= now
                )
            )
        )
        due_leads = res.scalars().all()

        processed = 0
        sent = 0
        skipped = 0

        for cl in due_leads:
            lead = await session.get(Lead, cl.lead_id)
            if not lead or lead.is_do_not_contact:
                cl.status = "UNSUBSCRIBED"
                skipped += 1
                continue

            # Verify if prospect has already replied in inbox
            threads = await session.execute(
                select(EmailThread).where(
                    and_(EmailThread.lead_id == lead.id, EmailThread.status == "REPLIED")
                )
            )
            if threads.scalars().first():
                cl.status = "REPLIED"
                skipped += 1
                continue

            next_step_num = cl.current_step + 1
            step_obj_res = await session.execute(
                select(SequenceStep).where(
                    and_(SequenceStep.campaign_id == camp.id, SequenceStep.step_number == next_step_num)
                )
            )
            step = step_obj_res.scalars().first()
            if not step:
                cl.status = "COMPLETED"
                cl.completed_at = now
                continue

            # Query related company and contacts
            comp = await session.get(Company, lead.company_id)
            if not comp:
                cl.status = "FAILED"
                skipped += 1
                continue

            cont_res = await session.execute(select(Contact).where(Contact.company_id == lead.company_id))
            contacts = cont_res.scalars().all()
            contact = contacts[0] if contacts else None
            to_email = contact.email if (contact and contact.email) else comp.business_email
            if not to_email:
                cl.status = "FAILED"
                skipped += 1
                continue

            first_name = contact.full_name.split()[0] if (contact and contact.full_name) else "there"
            issue_text = "mobile responsiveness and loading speed"
            
            # Fetch website and audit if available
            web_res = await session.execute(select(Website).where(Website.company_id == lead.company_id))
            web_obj = web_res.scalar_one_or_none()
            aud_obj = None
            issues_list, metrics_list, tech_list = [], [], []
            if web_obj:
                aud_res = await session.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == web_obj.id).order_by(WebsiteAudit.created_at.desc()))
                aud_obj = aud_res.scalars().first()
                if aud_obj:
                    iss_res = await session.execute(select(WebsiteIssue).where(WebsiteIssue.audit_id == aud_obj.id))
                    issues_list = iss_res.scalars().all()
                    if issues_list:
                        issue_text = issues_list[0].evidence
                    m_res = await session.execute(select(WebsiteAuditMetric).where(WebsiteAuditMetric.audit_id == aud_obj.id))
                    metrics_list = m_res.scalars().all()
                    t_res = await session.execute(select(WebsiteTechnology).where(WebsiteTechnology.audit_id == aud_obj.id))
                    tech_list = t_res.scalars().all()

            rec_service = lead.recommended_service or lead.primary_opportunity or "Website Redesign & Optimization"

            variables = {
                "first_name": first_name,
                "company_name": comp.business_name,
                "website": comp.website or comp.domain or "your website",
                "city": comp.city or "your area",
                "industry": comp.industry or "business",
                "primary_issue": issue_text,
                "recommended_service": rec_service
            }

            _, subject, _ = email_sender.render_template(step.subject_template, variables)
            _, body_text, _ = email_sender.render_template(step.body_template, variables)

            # Generate Technical R&D Audit Report for document attachment
            report_data = technical_report_generator.generate_report_data(
                lead=lead,
                company=comp,
                audit=aud_obj,
                contacts=contacts,
                issues=issues_list,
                metrics=metrics_list,
                technologies=tech_list
            )
            report_html = technical_report_generator.render_html_report(report_data)
            clean_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', comp.business_name)[:30]
            attached_filename = f"Technical-Audit-Report-{clean_slug}.html"

            # Format responsive, branded HTML email with scorecards
            scores_dict = report_data.get("scores") if aud_obj else None
            body_html = email_formatter.format_html_email(
                body_text=body_text,
                subject=subject,
                company_name=comp.business_name,
                scores=scores_dict,
                observed_issue=issue_text,
                recommended_service=rec_service,
                attached_report_name=attached_filename,
                report_url=f"/api/audits/lead/{lead.id}/report/html"
            )

            # Dispatch Outbound Email with MIME Attachment
            attachments = [{
                "filename": attached_filename,
                "content": report_html,
                "content_type": "text/html"
            }]

            success, msg_id, err = await email_sender.send_email(
                to_email=to_email,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                attachments=attachments
            )

            # Record in Thread & Inbox
            th_res = await session.execute(
                select(EmailThread).where(
                    and_(EmailThread.organization_id == org_id, EmailThread.lead_id == lead.id)
                )
            )
            thread = th_res.scalars().first()
            if not thread:
                thread = EmailThread(
                    organization_id=org_id,
                    lead_id=lead.id,
                    subject=subject,
                    recipient_email=to_email,
                    status="ACTIVE"
                )
                session.add(thread)
                await session.flush()

            msg = EmailMessage(
                thread_id=thread.id,
                direction="OUTBOUND",
                from_email=email_sender.from_email,
                to_email=to_email,
                subject=subject,
                body_text=body_text,
                status="SENT" if success else "FAILED",
                error_message=err,
                sent_at=now if success else None
            )
            session.add(msg)
            await session.flush()

            session.add(EmailEvent(message_id=msg.id, event_type="sent"))
            session.add(Activity(
                organization_id=org_id,
                lead_id=lead.id,
                activity_type="EMAIL_SENT",
                title=f"Sequence Step {next_step_num} Sent: {subject}",
                description=f"Automated multi-day follow-up outreach with attached R&D Audit Brief."
            ))

            # Update Stage
            lead.stage = "Contacted"
            lead.pipeline_stage = "CONTACTED"

            # Advance Step & Compute Next Due Date
            cl.current_step = next_step_num
            cl.status = "IN_SEQUENCE"

            # Determine next step delay
            next_step_query = await session.execute(
                select(SequenceStep).where(
                    and_(SequenceStep.campaign_id == camp.id, SequenceStep.step_number == next_step_num + 1)
                )
            )
            next_step_obj = next_step_query.scalars().first()
            if next_step_obj:
                # Interval between steps (e.g. Day 3 = 3 days after step 1; Day 7 = 4 days after step 2; Day 14 = 7 days after step 3)
                delta_days = next_step_obj.delay_days - step.delay_days
                if delta_days <= 0:
                    delta_days = 3
                cl.next_step_due_at = now + datetime.timedelta(days=delta_days)
            else:
                cl.status = "COMPLETED"
                cl.completed_at = now
                cl.next_step_due_at = None

            sent += 1
            processed += 1

        await session.commit()
        return {
            "processed": processed,
            "sent": sent,
            "skipped": skipped
        }

sequence_runner = AutonomousSequenceRunner()
