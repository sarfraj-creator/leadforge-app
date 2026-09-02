import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from backend.app.models.crm import Activity, Task, Note, Deal, StageHistory
from backend.app.models.email import EmailEvent, EmailMessage, EmailThread
from backend.app.models.campaign import CampaignLead, Campaign
from backend.app.models.lead import LeadOpportunity, LeadScore, Lead
from backend.app.models.contact import EmailVerificationRecord, Contact
from backend.app.models.website import (
    WebsiteIssue,
    WebsiteAuditMetric,
    WebsiteTechnology,
    WebsiteAudit,
    WebsitePage,
    Website,
)
from backend.app.models.company import LeadSourceRecord, Company
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.ai import AIRequestLog

logger = logging.getLogger("leadforge.admin.reset")

async def reset_demo_and_lead_data(session: AsyncSession) -> dict:
    """
    Safely purges all demo/lead/discovery data while strictly preserving:
    - Users
    - Organizations
    - OrgMembers
    - Settings / Source configurations
    - Audit logs
    """
    deleted_counts = {}

    # Order of deletion respecting foreign keys
    models_to_clear = [
        ("activities", Activity),
        ("tasks", Task),
        ("notes", Note),
        ("deals", Deal),
        ("stage_histories", StageHistory),
        ("email_events", EmailEvent),
        ("email_messages", EmailMessage),
        ("email_threads", EmailThread),
        ("campaign_leads", CampaignLead),
        ("campaigns", Campaign),
        ("lead_opportunities", LeadOpportunity),
        ("lead_scores", LeadScore),
        ("leads", Lead),
        ("email_verification_records", EmailVerificationRecord),
        ("contacts", Contact),
        ("website_issues", WebsiteIssue),
        ("website_audit_metrics", WebsiteAuditMetric),
        ("website_technologies", WebsiteTechnology),
        ("website_audits", WebsiteAudit),
        ("website_pages", WebsitePage),
        ("websites", Website),
        ("lead_source_records", LeadSourceRecord),
        ("companies", Company),
        ("discovery_jobs", DiscoveryJob),
        ("ai_request_logs", AIRequestLog),
    ]

    for name, model in models_to_clear:
        res = await session.execute(delete(model))
        deleted_counts[name] = res.rowcount if hasattr(res, 'rowcount') else 0

    await session.commit()
    logger.info("Demo and lead data reset complete: %s", deleted_counts)
    return {
        "status": "SUCCESS",
        "message": "All demo leads, companies, audits, and discovery jobs have been safely reset.",
        "records_deleted": deleted_counts,
    }
