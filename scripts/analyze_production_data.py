import sys, os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import json
from sqlalchemy import select, func, or_, and_, desc
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsiteAudit, WebsitePage
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.models.provenance import FieldProvenanceRecord

async def analyze():
    await init_db()
    async with AsyncSessionLocal() as session:
        # Fetch jobs 1 to 7
        jobs = (await session.execute(select(DiscoveryJob).where(DiscoveryJob.id.in_([1, 2, 3, 4, 5, 6, 7])).order_by(DiscoveryJob.id))).scalars().all()
        
        print("--- 7 INDUSTRY DETAILED METRICS ---")
        headers = ["INDUSTRY", "DISCOVERED", "UNIQUE", "WEBSITE_FOUND", "REACHABLE", "OFFICIAL_VERIFIED", "AUDIT_COMPLETE", "AUDIT_INCOMPLETE", "OPPORTUNITIES", "INTENT_KNOWN", "CONTACTABLE", "QUALIFIED", "SALES_READY", "APPROVED", "REJECTED"]
        print("\t".join(headers))
        
        totals = {h: 0 for h in headers[1:]}
        
        industry_names = {
            1: "Restaurant",
            2: "Dentist / Dental Clinic",
            3: "Law Firm",
            4: "Real Estate",
            5: "Hotel / Hospitality",
            6: "Gym / Fitness",
            7: "E-Commerce / Retail"
        }
        
        for j in jobs:
            # Let's inspect leads and companies belonging to this job / industry
            # For each job:
            disc = j.discovered_count
            uniq = j.new_businesses_count
            wf = j.websites_found_count
            reach = getattr(j, "websites_reachable_count", 0)
            off_ver = getattr(j, "websites_verified_count", 0)
            aud_comp = getattr(j, "audits_completed_count", 0)
            aud_incomp = getattr(j, "audits_incomplete_count", 0)
            
            # Count opportunities detected for this job's companies
            # Find companies for this job
            c_res = await session.execute(select(Company).where(Company.industry == j.industry, Company.city == j.location))
            comps = c_res.scalars().all()
            comp_ids = [c.id for c in comps]
            
            leads_res = await session.execute(select(Lead).where(Lead.company_id.in_(comp_ids)))
            leads = leads_res.scalars().all()
            lead_ids = [l.id for l in leads]
            
            opp_count = (await session.execute(select(func.count(func.distinct(ServiceNeedEvidence.lead_id))).where(ServiceNeedEvidence.lead_id.in_(lead_ids)))).scalar() or 0 if lead_ids else 0
            intent_known = (await session.execute(select(func.count(LeadScore.id)).where(LeadScore.lead_id.in_(lead_ids), LeadScore.buying_intent != "UNKNOWN"))).scalar() or 0 if lead_ids else 0
            
            # Contactable: has email or phone
            contactable = 0
            for c in comps:
                cont_res = await session.execute(select(Contact).where(Contact.company_id == c.id))
                conts = cont_res.scalars().all()
                has_email = bool(c.business_email or any(ct.email for ct in conts))
                has_phone = bool(c.phone or any(ct.phone for ct in conts))
                if has_email or has_phone:
                    contactable += 1
                    
            qual = sum(1 for l in leads if l.is_qualified)
            sales_ready = sum(1 for l in leads if l.is_sales_ready)
            approved = sum(1 for l in leads if l.review_status == "APPROVED")
            rejected = len(leads) - qual
            
            ind_name = industry_names.get(j.id, j.name)
            row = [ind_name, disc, uniq, wf, reach, off_ver, aud_comp, aud_incomp, opp_count, intent_known, contactable, qual, sales_ready, approved, rejected]
            print("\t".join(str(x) for x in row))
            
            for idx, h in enumerate(headers[1:]):
                totals[h] += row[idx+1]
                
        total_row = ["TOTAL"] + [totals[h] for h in headers[1:]]
        print("\t".join(str(x) for x in total_row))
        
        # Detailed leads inspection
        print("\n--- QUALIFIED AND CONTACTABLE LEADS DETAILS ---")
        q_leads = (await session.execute(select(Lead).where(Lead.is_qualified == True))).scalars().all()
        print(f"Total Qualified Leads: {len(q_leads)}")
        for l in q_leads:
            c = await session.get(Company, l.company_id)
            w = (await session.execute(select(Website).where(Website.company_id == c.id))).scalar_one_or_none()
            conts = (await session.execute(select(Contact).where(Contact.company_id == c.id))).scalars().all()
            sc = (await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))).scalar_one_or_none()
            sne = (await session.execute(select(ServiceNeedEvidence).where(ServiceNeedEvidence.lead_id == l.id))).scalars().all()
            print(f"Lead #{l.id} - Company: {c.business_name}")
            print(f"  Industry: {c.industry} | Country: {c.country} | City: {c.city}")
            print(f"  Website: {c.website} | Status: {getattr(w, 'website_verification_status', None)} | Score: {getattr(w, 'verification_score', None)}")
            print(f"  Phone: {c.phone} | Status: {c.phone_validation_status}")
            print(f"  Email: {c.business_email}")
            for ct in conts:
                print(f"    Contact: {ct.full_name} | Email: {ct.email} ({ct.email_status}) | Job Title: {ct.job_title}")
            print(f"  Stage: {l.pipeline_stage} | Review: {l.review_status} | Quality: {l.data_quality_score}")
            if sc:
                print(f"  Scores -> Total: {sc.total_score} | Opp: {sc.opportunity_score} | Intent: {sc.intent_score} ({sc.buying_intent}) | Contactability: {sc.contactability_score}")
            for sn in sne:
                print(f"  Need: {sn.offering_type} | Evidence: {sn.evidence_text}")

if __name__ == "__main__":
    asyncio.run(analyze())
