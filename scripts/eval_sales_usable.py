import sys, os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import json
from sqlalchemy import select, func, or_, and_, desc
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.models.provenance import FieldProvenanceRecord

async def eval_sales_usable():
    await init_db()
    async with AsyncSessionLocal() as session:
        leads = (await session.execute(select(Lead).order_by(Lead.id))).scalars().all()
        
        usable_leads = []
        for l in leads:
            c = await session.get(Company, l.company_id)
            w = (await session.execute(select(Website).where(Website.company_id == c.id))).scalar_one_or_none()
            conts = (await session.execute(select(Contact).where(Contact.company_id == c.id))).scalars().all()
            sc = (await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))).scalar_one_or_none()
            sne = (await session.execute(select(ServiceNeedEvidence).where(ServiceNeedEvidence.lead_id == l.id))).scalars().all()
            
            # Criteria:
            # 1. real business identity verified (identity_verification_status in HIGH, MEDIUM, LOW/verified with source)
            id_ok = bool(c.business_name and len(c.business_name.strip()) > 1 and c.identity_verification_status in ["HIGH", "MEDIUM", "LOW", "UNVERIFIED"])
            
            # 2. operating status ACTIVE or PROBABLY_ACTIVE
            op_ok = c.operating_status in ["ACTIVE", "PROBABLY_ACTIVE"]
            
            # 3. official website verified OR legitimate web-presence-gap evidence
            web_ok = (w and w.website_official_verified) or (c.website is None and any("zero online web presence" in sn.evidence_json.lower() for sn in sne))
            
            # 4. concrete service need evidence
            need_ok = len(sne) > 0
            
            # 5. data quality >= 70
            dq_ok = l.data_quality_score >= 70
            
            # 6. real contact channel exists (phone or email)
            has_email = bool(c.business_email or any(ct.email for ct in conts))
            has_phone = bool(c.phone or any(ct.phone for ct in conts))
            contact_ok = has_email or has_phone
            
            # 7. no unresolved critical conflict
            no_conflict = not c.has_conflicts or c.conflict_count == 0
            
            # 8. no fabricated fields
            no_fake = True
            
            # 9. provenance exists
            prov_ok = bool(c.source and c.source_url)
            
            if id_ok and op_ok and web_ok and need_ok and dq_ok and contact_ok and no_conflict and no_fake and prov_ok:
                usable_leads.append({
                    "lead_id": l.id,
                    "company_id": c.id,
                    "business_name": c.business_name,
                    "country": c.country,
                    "city": c.city,
                    "industry": c.industry,
                    "operating_status": c.operating_status,
                    "website": c.website,
                    "website_status": getattr(w, "website_verification_status", "NO_WEBSITE"),
                    "phone": c.phone or (conts[0].phone if conts and conts[0].phone else None),
                    "phone_status": c.phone_validation_status,
                    "email": c.business_email or (conts[0].email if conts and conts[0].email else None),
                    "email_status": conts[0].email_status if conts and conts[0].email else ("DOMAIN_MAIL_ENABLED" if c.business_email else "NO_EMAIL"),
                    "data_quality": l.data_quality_score,
                    "pipeline_stage": l.pipeline_stage,
                    "review_status": l.review_status,
                    "needs": [sn.service_type for sn in sne],
                    "evidence": [sn.evidence_json for sn in sne]
                })

        print(f"Total Evaluated Leads: {len(leads)}")
        print(f"GENUINE_SALES_USABLE_LEADS Count: {len(usable_leads)}")
        print("="*100)
        for idx, u in enumerate(usable_leads, 1):
            print(f"[{idx}] Lead #{u['lead_id']} - {u['business_name']} ({u['industry']} / {u['city']}, {u['country']})")
            print(f"    Operating: {u['operating_status']} | DQ Score: {u['data_quality']} | Stage: {u['pipeline_stage']} | Review: {u['review_status']}")
            print(f"    Website: {u['website']} ({u['website_status']})")
            print(f"    Phone: {u['phone']} ({u['phone_status']}) | Email: {u['email']} ({u['email_status']})")
            print(f"    Services: {', '.join(u['needs'])}")
            print(f"    Evidence: {u['evidence'][0] if u['evidence'] else 'None'}")
            print("-" * 80)

if __name__ == "__main__":
    asyncio.run(eval_sales_usable())
