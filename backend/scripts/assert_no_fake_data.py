import asyncio
import sys
import os
import json
sys.path.insert(0, os.path.abspath("."))
import logging
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.contact import Contact
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.models.provenance import FieldProvenanceRecord
from backend.app.services.discovery.taxonomy import resolve_industry_from_source

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("assert_no_fake_data")

SUSPICIOUS_EMAIL_PATTERNS = ["example.com", "domain.com", "fake.com", "test.com", "user@email.com", "john.doe", "jane.doe"]
SUSPICIOUS_PHONE_PATTERNS = ["555-", "0000000000", "1234567890", "+1 555"]
SUSPICIOUS_NAME_PATTERNS = ["john doe", "jane doe", "test company", "fake business", "demo company", "placeholder", "generic business"]
GENERIC_PERSON_PATTERNS = ["admin", "placeholder", "team member", "contact person", "owner", "staff"]

async def assert_no_fake_data():
    await init_db()
    violations = []

    async with AsyncSessionLocal() as session:
        # 1. Audit Companies
        c_res = await session.execute(select(Company))
        companies = c_res.scalars().all()
        for c in companies:
            name_lower = c.business_name.lower()
            if any(p in name_lower for p in SUSPICIOUS_NAME_PATTERNS):
                violations.append(f"Suspicious business name found: '{c.business_name}' (Company ID {c.id})")
            if c.business_email and any(p in c.business_email.lower() for p in SUSPICIOUS_EMAIL_PATTERNS):
                violations.append(f"Suspicious placeholder email found: '{c.business_email}' (Company ID {c.id})")
            if c.phone and any(p in c.phone for p in SUSPICIOUS_PHONE_PATTERNS):
                violations.append(f"Suspicious placeholder phone found: '{c.phone}' (Company ID {c.id})")
            if c.domain and any(p in c.domain.lower() for p in ["example.com", "domain.com", "fake.com"]):
                violations.append(f"Fake domain found: '{c.domain}' (Company ID {c.id})")

        # 2. Audit Contacts
        cont_res = await session.execute(select(Contact))
        contacts = cont_res.scalars().all()
        for cont in contacts:
            if cont.full_name:
                name_lower = cont.full_name.lower()
                if any(p in name_lower for p in SUSPICIOUS_NAME_PATTERNS) or any(p == name_lower for p in GENERIC_PERSON_PATTERNS):
                    violations.append(f"Suspicious contact person name found: '{cont.full_name}' (Contact ID {cont.id})")
            if cont.email and any(p in cont.email.lower() for p in SUSPICIOUS_EMAIL_PATTERNS):
                violations.append(f"Suspicious contact email found: '{cont.email}' (Contact ID {cont.id})")
            if cont.phone and any(p in cont.phone for p in SUSPICIOUS_PHONE_PATTERNS):
                violations.append(f"Suspicious contact phone found: '{cont.phone}' (Contact ID {cont.id})")

        # 3. Audit Websites
        web_res = await session.execute(select(Website))
        websites = web_res.scalars().all()
        for w in websites:
            if w.website_official_verified and w.website_verification_status not in ["OFFICIAL_VERIFIED", "OFFICIAL_MATCH"]:
                violations.append(f"Website ID {w.id} marked official verified but has status '{w.website_verification_status}'")

        # 4. Audit Website Audits
        aud_res = await session.execute(select(WebsiteAudit))
        audits = aud_res.scalars().all()
        for aud in audits:
            if aud.audit_status == "AUDIT_INCOMPLETE" and aud.overall_score and aud.overall_score > 0:
                violations.append(f"Incomplete audit has synthetic positive overall score: {aud.overall_score} (Audit ID {aud.id})")

        # 5. Audit Lead Scores & Intent
        score_res = await session.execute(select(LeadScore))
        scores = score_res.scalars().all()
        for s in scores:
            if s.buying_intent != "UNKNOWN" and s.intent_score == 0:
                violations.append(f"Intent state is not UNKNOWN but has 0 score: {s.buying_intent} (Score ID {s.id})")
            if s.buying_intent == "UNKNOWN" and s.intent_score > 0:
                violations.append(f"Intent state is UNKNOWN but has positive score: {s.intent_score} (Score ID {s.id})")

        # 6. Audit Service Need Evidence
        sne_res = await session.execute(select(ServiceNeedEvidence))
        snes = sne_res.scalars().all()
        for sn in snes:
            ev_list = json.loads(sn.evidence_json) if sn.evidence_json else []
            if len(ev_list) == 0:
                violations.append(f"ServiceNeedEvidence ID {sn.id} has empty evidence list")

        # 7. Audit Leads: Qualification, Sales-Ready, and Review Rules
        lead_res = await session.execute(select(Lead))
        leads = lead_res.scalars().all()
        for l in leads:
            s_res = await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))
            score = s_res.scalar_one_or_none()
            
            if l.is_qualified:
                if l.data_quality_score < 70:
                    violations.append(f"Lead ID {l.id} marked qualified with DQ {l.data_quality_score} < 70")
                if score and score.opportunity_score < 60:
                    violations.append(f"Lead ID {l.id} marked qualified with Opportunity {score.opportunity_score} < 60")
            
            if l.is_sales_ready:
                if not l.is_qualified:
                    violations.append(f"Lead ID {l.id} marked sales-ready but is not qualified")
                if l.review_status != "APPROVED":
                    violations.append(f"Lead ID {l.id} marked sales-ready with review_status '{l.review_status}' != APPROVED")
                if score and score.contactability_score < 50:
                    violations.append(f"Lead ID {l.id} marked sales-ready with contactability {score.contactability_score} < 50")

    print("\n" + "="*70)
    print("LEADFORGE ZERO FAKE DATA & INTEGRITY ASSERTION SUITE")
    print("="*70)
    if violations:
        print(f"FAILED: {len(violations)} data integrity or fake data violations detected:")
        for v in violations:
            print(f"  - {v}")
        print("="*70 + "\n")
        sys.exit(1)
    else:
        print("PASSED: 0 placeholder, synthetic, or fake data items detected in DB.")
        print(f"Audited {len(companies)} companies, {len(contacts)} contacts, {len(websites)} websites, {len(audits)} audits, {len(leads)} leads.")
        print("="*70 + "\n")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(assert_no_fake_data())
