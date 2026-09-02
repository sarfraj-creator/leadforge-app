import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import json
import re
from sqlalchemy import select, func, or_
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob, LeadSourceConfig
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact, EmailVerificationRecord
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.provenance import FieldProvenanceRecord
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.services.discovery.taxonomy import resolve_industry_from_source

async def run_comprehensive_audit():
    await init_db()
    async with AsyncSessionLocal() as session:
        print("=" * 90)
        print("LEADFORGE COMPREHENSIVE PRODUCTION DATABASE INTEGRITY AUDIT")
        print("=" * 90)

        violations = []

        # ---------------------------------------------------------------------
        # 1. SCAN FOR SYNTHETIC/FAKE VALUES & PLACEHOLDERS
        # ---------------------------------------------------------------------
        comps = (await session.execute(select(Company))).scalars().all()
        contacts = (await session.execute(select(Contact))).scalars().all()
        audits = (await session.execute(select(WebsiteAudit))).scalars().all()
        leads = (await session.execute(select(Lead))).scalars().all()
        scores = (await session.execute(select(LeadScore))).scalars().all()

        for c in comps:
            name_lower = (c.business_name or "").lower()
            if any(fake in name_lower for fake in ["placeholder", "example", "dummy", "test company", "acme corp", "foo bar"]):
                violations.append({"id": f"Company #{c.id}", "field": "business_name", "value": c.business_name, "reason": "Placeholder name"})
            
            if c.website and any(fake in c.website.lower() for fake in ["example.com", "test.com", "placeholder.org"]):
                violations.append({"id": f"Company #{c.id}", "field": "website", "value": c.website, "reason": "Fake domain"})
            
            if c.phone and ("555-" in c.phone or "55501" in c.phone):
                violations.append({"id": f"Company #{c.id}", "field": "phone", "value": c.phone, "reason": "555 fictitious phone"})

        for ct in contacts:
            if ct.first_name and any(fake in ct.first_name.lower() for fake in ["john doe", "jane doe", "test", "placeholder", "fake"]):
                violations.append({"id": f"Contact #{ct.id}", "field": "first_name", "value": ct.first_name, "reason": "Synthetic name"})
            if ct.email and any(fake in ct.email.lower() for fake in ["example.com", "test.com", "placeholder.org"]):
                violations.append({"id": f"Contact #{ct.id}", "field": "email", "value": ct.email, "reason": "Fake email"})
            if ct.email_status == "MAILBOX_VERIFIED":
                violations.append({"id": f"Contact #{ct.id}", "field": "email_status", "value": ct.email_status, "reason": "MAILBOX_VERIFIED claimed without live SMTP handshake"})

        # ---------------------------------------------------------------------
        # 2. SCAN FOR INCOMPLETE AUDITS WITH SCORES
        # ---------------------------------------------------------------------
        for a in audits:
            if a.audit_status == "AUDIT_INCOMPLETE" and (a.overall_score > 0 or a.performance_score > 0):
                violations.append({"id": f"WebsiteAudit #{a.id}", "field": "overall_score", "value": a.overall_score, "reason": "Incomplete audit assigned non-zero score"})

        # ---------------------------------------------------------------------
        # 3. SCAN FOR BUYING INTENT HALLUCINATIONS
        # ---------------------------------------------------------------------
        for s in scores:
            if s.buying_intent != "UNKNOWN" or s.intent_score > 0:
                violations.append({"id": f"LeadScore #{s.id}", "field": "buying_intent", "value": f"{s.buying_intent} (Score: {s.intent_score})", "reason": "Intent fabricated without commercial signals"})

        # ---------------------------------------------------------------------
        # 4. SCAN FOR QUALIFICATION & SALES_READY LOGIC VIOLATIONS
        # ---------------------------------------------------------------------
        for l in leads:
            s = (await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))).scalar_one_or_none()
            c = await session.get(Company, l.company_id)
            w = (await session.execute(select(Website).where(Website.company_id == c.id))).scalar_one_or_none() if c else None
            a = (await session.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == w.id))).scalars().first() if w else None

            if l.is_qualified:
                if l.data_quality_score < 70:
                    violations.append({"id": f"Lead #{l.id}", "field": "is_qualified", "value": "True", "reason": f"Qualified with DQ {l.data_quality_score} < 70"})
                if s and s.opportunity_score < 60:
                    violations.append({"id": f"Lead #{l.id}", "field": "is_qualified", "value": "True", "reason": f"Qualified with Opp {s.opportunity_score} < 60"})
                if c.website and (not a or a.audit_status != "AUDIT_COMPLETE"):
                    violations.append({"id": f"Lead #{l.id}", "field": "is_qualified", "value": "True", "reason": "Qualified without AUDIT_COMPLETE"})
                if c.website and (not w or not w.website_official_verified):
                    violations.append({"id": f"Lead #{l.id}", "field": "is_qualified", "value": "True", "reason": "Qualified without official website verified"})

            if l.is_sales_ready:
                if not l.is_qualified:
                    violations.append({"id": f"Lead #{l.id}", "field": "is_sales_ready", "value": "True", "reason": "Sales-Ready but not Qualified"})
                if s and s.contactability_score < 50:
                    violations.append({"id": f"Lead #{l.id}", "field": "is_sales_ready", "value": "True", "reason": f"Sales-Ready with Contactability {s.contactability_score} < 50"})
                if l.review_status != "APPROVED":
                    violations.append({"id": f"Lead #{l.id}", "field": "is_sales_ready", "value": "True", "reason": f"Sales-Ready with review_status={l.review_status} != APPROVED"})

        # ---------------------------------------------------------------------
        # 5. SCAN FOR TAXONOMY MISMATCHES
        # ---------------------------------------------------------------------
        for c in comps:
            src = (await session.execute(select(LeadSourceRecord).where(LeadSourceRecord.company_id == c.id))).scalars().first()
            raw = json.loads(src.raw_data) if src and src.raw_data else {}
            resolved = resolve_industry_from_source(raw, c.category, c.industry)
            # Check if resolved industry diverges from current industry
            if resolved != c.industry and resolved != "General Business":
                violations.append({"id": f"Company #{c.id}", "field": "industry", "value": f"Current: {c.industry} vs Resolved: {resolved}", "reason": "Taxonomy mismatch with source tags"})

        print(f"\nAUDIT RESULTS: Total Violations Detected = {len(violations)}")
        if violations:
            for v in violations:
                print(f"  VIOLATION: {v['id']} | Field: {v['field']} | Value: {v['value']} | Reason: {v['reason']}")
        else:
            print("  PASSED: ZERO violations detected across all audited integrity rules.")
        print("=" * 90)

if __name__ == "__main__":
    asyncio.run(run_comprehensive_audit())
