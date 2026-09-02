import pytest
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import Organization, User
from backend.app.models.company import Company
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.website import Website, WebsiteAudit, WebsiteIssue, WebsiteAuditMetric
from backend.app.models.email import EmailThread
from backend.app.services.audit.report_generator import technical_report_generator
from backend.app.workers.sequence_runner import sequence_runner, DEFAULT_SEQUENCE_STEPS

@pytest.mark.anyio
async def test_technical_report_generator_completeness():
    await init_db()
    async with AsyncSessionLocal() as session:
        # Create test company & lead
        comp = Company(
            organization_id=1,
            business_name="Acme Dental Studio",
            industry="Healthcare / Dental",
            website="https://acmedentalstudio.demo",
            domain="acmedentalstudio.demo",
            city="Seattle",
            state="WA",
            country="USA",
            phone="+1-206-555-0199",
            business_email="info@acmedentalstudio.demo",
            dedup_hash="test:acmedentalstudio.demo"
        )
        session.add(comp)
        await session.flush()

        # Add Audit
        web = Website(
            company_id=comp.id,
            url="https://acmedentalstudio.demo",
            domain="acmedentalstudio.demo",
            status="WEBSITE_FOUND",
            http_status=200,
            ssl_valid=True
        )
        session.add(web)
        await session.flush()

        audit = WebsiteAudit(
            website_id=web.id,
            overall_score=52,
            mobile_score=48,
            performance_score=45,
            seo_score=68,
            accessibility_score=70,
            security_score=85,
            conversion_score=40,
            summary="Mobile responsiveness deficiencies and missing booking CTA flow."
        )
        session.add(audit)
        await session.flush()

        issue_obj = WebsiteIssue(
            audit_id=audit.id,
            category="Mobile",
            title="Missing Responsive Viewport Meta",
            severity="CRITICAL",
            evidence="Page renders at 980px desktop width on smartphone viewports.",
            recommendation="Deploy mobile-first viewport architecture."
        )
        session.add(issue_obj)

        metric_obj = WebsiteAuditMetric(
            audit_id=audit.id,
            category="Performance",
            metric_name="Page Load Time",
            value="4200ms",
            score=45
        )
        session.add(metric_obj)

        lead = Lead(
            organization_id=1,
            company_id=comp.id,
            is_qualified=True,
            stage="Qualified",
            primary_opportunity="Responsive Redesign",
            recommended_service="Mobile-First Responsive Redesign & Speed Optimization",
            freshness_state="FRESH"
        )
        session.add(lead)
        await session.flush()

        # Generate report
        report = technical_report_generator.generate_report_data(
            lead=lead,
            company=comp,
            audit=audit,
            issues=[issue_obj],
            metrics=[metric_obj]
        )
        assert report is not None
        assert report["company"]["business_name"] == "Acme Dental Studio"
        assert report["category"] == "HAS_WEBSITE_REDESIGN"
        assert report["scores"]["mobile_score"] == 48
        assert len(report["issues"]) >= 1
        assert len(report["action_plan"]) >= 1

        # Test HTML rendering
        html = technical_report_generator.render_html_report(report)
        assert "Acme Dental Studio" in html
        assert "Missing Responsive Viewport Meta" in html
        assert "Phase 1: Responsive Layout Modernization" in html
        assert "<!DOCTYPE html>" in html

@pytest.mark.anyio
async def test_lead_category_segmentation():
    await init_db()
    async with AsyncSessionLocal() as session:
        # 1. Has Website Lead
        c1 = Company(
            organization_id=1,
            business_name="Web Redesign Candidate",
            industry="Legal",
            website="https://webrepair.demo",
            domain="webrepair.demo",
            dedup_hash="test:webrepair.demo"
        )
        session.add(c1)
        await session.flush()
        l1 = Lead(organization_id=1, company_id=c1.id, is_qualified=True, stage="Qualified")
        session.add(l1)

        # 2. No Website Lead
        c2 = Company(
            organization_id=1,
            business_name="New Build Candidate",
            industry="Plumbing",
            website=None,
            domain=None,
            dedup_hash="test:newbuild.demo"
        )
        session.add(c2)
        await session.flush()
        l2 = Lead(organization_id=1, company_id=c2.id, is_qualified=True, stage="Qualified")
        session.add(l2)

        await session.flush()

        rep1 = technical_report_generator.generate_report_data(lead=l1, company=c1)
        rep2 = technical_report_generator.generate_report_data(lead=l2, company=c2)

        assert rep1["category"] == "HAS_WEBSITE_REDESIGN"
        assert rep2["category"] == "NO_WEBSITE_NEW_BUILD"
        assert "Zero Web Footprint Detected" in rep2["issues"][0]["title"]

@pytest.mark.anyio
async def test_sequence_runner_day_intervals():
    await init_db()
    async with AsyncSessionLocal() as session:
        org_id = 1
        camp = await sequence_runner.get_or_create_default_campaign(session, org_id)
        assert camp is not None
        assert len(DEFAULT_SEQUENCE_STEPS) == 4
        assert [s["delay_days"] for s in DEFAULT_SEQUENCE_STEPS] == [0, 3, 7, 14]

        # Auto enroll
        enroll_res = await sequence_runner.auto_enroll_leads(session, org_id)
        assert enroll_res["campaign_id"] == camp.id
        assert enroll_res["enrolled_count"] >= 0

        # Process due steps
        process_res = await sequence_runner.process_due_steps(session, org_id)
        assert "processed" in process_res
        assert "sent" in process_res

@pytest.mark.anyio
async def test_sequence_auto_stop_on_reply():
    await init_db()
    async with AsyncSessionLocal() as session:
        org_id = 1
        # Create company, lead, and thread with REPLIED
        comp = Company(
            organization_id=org_id,
            business_name="Reply Test Co",
            industry="Tech",
            business_email="test@replyco.demo",
            dedup_hash="test:replyco.demo"
        )
        session.add(comp)
        await session.flush()

        lead = Lead(organization_id=org_id, company_id=comp.id, is_qualified=True, stage="Qualified")
        session.add(lead)
        await session.flush()

        # Add thread marked REPLIED
        thread = EmailThread(
            organization_id=org_id,
            lead_id=lead.id,
            subject="Interested in redesign",
            recipient_email="test@replyco.demo",
            status="REPLIED",
            reply_classification="Interested"
        )
        session.add(thread)
        await session.flush()

        # Enroll lead
        camp = await sequence_runner.get_or_create_default_campaign(session, org_id)
        enroll_res = await sequence_runner.auto_enroll_leads(session, org_id, lead_ids=[lead.id])
        
        # Process steps: should be skipped because thread status is REPLIED
        res = await sequence_runner.process_due_steps(session, org_id)
        assert res["skipped"] >= 1
