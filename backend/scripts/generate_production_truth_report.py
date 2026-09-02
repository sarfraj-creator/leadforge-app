import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import json
import logging
from sqlalchemy import select, func, or_
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.discovery import DiscoveryJob
from backend.app.models.company import Company
from backend.app.models.website import Website, WebsiteAudit
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.provenance import FieldProvenanceRecord
from backend.app.models.service_need import ServiceNeedEvidence

logging.basicConfig(level=logging.INFO, format="%(message)s")

async def generate_production_truth_report():
    await init_db()
    async with AsyncSessionLocal() as session:
        def pct(num, den):
            return round((num / den * 100), 1) if den > 0 else 0.0

        print("\n" + "=" * 90)
        print("LEADFORGE CANONICAL PRODUCTION DATA TRUTH & REVALIDATION REPORT")
        print("=" * 90)

        # ---------------------------------------------------------------------
        # 1. TASK-1175 ACCEPTANCE SCOPE (JOBS 1 TO 7)
        # ---------------------------------------------------------------------
        t1175_jobs = (await session.execute(
            select(DiscoveryJob).where(DiscoveryJob.id.between(1, 7)).order_by(DiscoveryJob.id)
        )).scalars().all()

        t1175_comp_ids = list(range(1, 106))
        
        tot_disc_1175 = sum(j.discovered_count for j in t1175_jobs)
        unique_comps_1175 = (await session.execute(
            select(func.count(Company.id)).where(Company.id.in_(t1175_comp_ids))
        )).scalar() or 0
        
        web_found_1175 = sum(j.websites_found_count for j in t1175_jobs)
        web_reach_1175 = sum(j.websites_reachable_count for j in t1175_jobs)
        web_ver_1175 = sum(j.websites_verified_count for j in t1175_jobs)
        aud_comp_1175 = sum(j.audits_completed_count for j in t1175_jobs)
        aud_incomp_1175 = (await session.execute(
            select(func.count(WebsiteAudit.id))
            .join(Website, WebsiteAudit.website_id == Website.id)
            .where(Website.company_id.in_(t1175_comp_ids), WebsiteAudit.audit_status == "AUDIT_INCOMPLETE")
        )).scalar() or 0
        
        opp_detected_1175 = (await session.execute(
            select(func.count(func.distinct(ServiceNeedEvidence.lead_id)))
            .join(Lead, ServiceNeedEvidence.lead_id == Lead.id)
            .where(Lead.company_id.in_(t1175_comp_ids))
        )).scalar() or 0
        
        intent_known_1175 = (await session.execute(
            select(func.count(LeadScore.id))
            .join(Lead, LeadScore.lead_id == Lead.id)
            .where(Lead.company_id.in_(t1175_comp_ids), LeadScore.buying_intent != "UNKNOWN")
        )).scalar() or 0
        
        contactable_1175 = (await session.execute(
            select(func.count(func.distinct(Lead.id)))
            .join(Company, Lead.company_id == Company.id)
            .outerjoin(Contact, Contact.company_id == Company.id)
            .where(
                Lead.company_id.in_(t1175_comp_ids),
                or_(Company.business_email.isnot(None), Contact.email.isnot(None), Company.phone.isnot(None))
            )
        )).scalar() or 0
        
        qual_1175 = (await session.execute(
            select(func.count(Lead.id))
            .where(Lead.company_id.in_(t1175_comp_ids), Lead.is_qualified == True)
        )).scalar() or 0
        
        sales_ready_1175 = (await session.execute(
            select(func.count(Lead.id))
            .where(Lead.company_id.in_(t1175_comp_ids), Lead.is_sales_ready == True)
        )).scalar() or 0
        
        approved_1175 = (await session.execute(
            select(func.count(Lead.id))
            .where(Lead.company_id.in_(t1175_comp_ids), Lead.review_status == "APPROVED")
        )).scalar() or 0
        
        rejected_1175 = tot_disc_1175 - qual_1175

        print("\n--- 1. TASK-1175 ACCEPTANCE METRICS (JOBS 1–7) ---")
        print(f"Total Discovered Records:           {tot_disc_1175}")
        print(f"Unique Business Entities:           {unique_comps_1175}")
        print(f"Websites Discovered:                {web_found_1175}")
        print(f"Websites Reachable:                 {web_reach_1175}")
        print(f"Official Websites Verified:         {web_ver_1175}")
        print(f"Audits Completed:                   {aud_comp_1175}")
        print(f"Audits Incomplete:                  {aud_incomp_1175}")
        print(f"Service Opportunities Detected:     {opp_detected_1175}")
        print(f"Buying Intent Known:                {intent_known_1175}")
        print(f"Buying Intent Unknown:              {unique_comps_1175 - intent_known_1175}")
        print(f"Contactable Businesses:             {contactable_1175}")
        print(f"Qualified Leads (Canonical Rules):  {qual_1175}")
        print(f"Sales-Ready (Gated & Approved):     {sales_ready_1175}")
        print(f"Human Reviews Approved:             {approved_1175}")
        print(f"Filtered / Rejected (Job Total):    {rejected_1175}")

        # ---------------------------------------------------------------------
        # 2. LIFECYCLE STAGE DISTRIBUTION (TASK-1175)
        # ---------------------------------------------------------------------
        stage_counts = (await session.execute(
            select(Lead.pipeline_stage, func.count(Lead.id))
            .where(Lead.company_id.in_(t1175_comp_ids))
            .group_by(Lead.pipeline_stage)
        )).all()

        print("\n--- 2. CANONICAL LIFECYCLE STAGE BREAKDOWN (TASK-1175) ---")
        for stg, cnt in stage_counts:
            print(f"  • {stg:<25}: {cnt}")

        # ---------------------------------------------------------------------
        # 3. TASK-1175 JOB-BY-JOB PERFORMANCE MATRIX
        # ---------------------------------------------------------------------
        print("\n--- 3. TASK-1175 JOB-BY-JOB RECONCILIATION TABLE ---")
        print(f"{'JOB ID & CAMPAIGN':<30} | {'DISC':<5} | {'URLS':<5} | {'REACH':<5} | {'VERIF':<5} | {'AUDIT':<5} | {'CONT':<5} | {'QUAL':<5} | {'SALES_RDY':<9}")
        print("-" * 95)
        for j in t1175_jobs:
            print(f"Job #{j.id}: {j.name.replace(' Discovery', ''):<22} | {j.discovered_count:<5} | {j.websites_found_count:<5} | {j.websites_reachable_count:<5} | {j.websites_verified_count:<5} | {j.audits_completed_count:<5} | {j.contacts_found_count:<5} | {j.qualified_leads_count:<5} | {j.sales_ready_count:<9}")

        # ---------------------------------------------------------------------
        # 4. REJECTION REASON ATTRIBUTION (TASK-1175)
        # ---------------------------------------------------------------------
        agg_rej_1175 = {}
        for j in t1175_jobs:
            if j.rejection_reasons_json:
                try:
                    r_dict = json.loads(j.rejection_reasons_json)
                    for k, v in r_dict.items():
                        agg_rej_1175[k] = agg_rej_1175.get(k, 0) + v
                except Exception:
                    pass

        print("\n--- 4. TASK-1175 REJECTION REASON ATTRIBUTION (TOTAL = 105) ---")
        for rk, rv in agg_rej_1175.items():
            if rv > 0:
                print(f"  • {rk.replace('_', ' '):<28}: {rv}")
        print(f"  SUM OF ATTRIBUTED REJECTIONS : {sum(agg_rej_1175.values())}")

        # ---------------------------------------------------------------------
        # 5. CANDIDATE LEADS INVESTIGATION MATRIX
        # ---------------------------------------------------------------------
        print("\n--- 5. INVESTIGATED CANDIDATE LEADS EVIDENCE BREAKDOWN ---")
        candidate_ids = [41, 42, 43, 44, 45, 49, 53, 79, 80, 83, 84, 85]
        for cid in candidate_ids:
            c = await session.get(Company, cid)
            l = (await session.execute(select(Lead).where(Lead.company_id == cid))).scalar_one_or_none()
            w = (await session.execute(select(Website).where(Website.company_id == cid))).scalar_one_or_none()
            aud = (await session.execute(select(WebsiteAudit).where(WebsiteAudit.website_id == w.id))).scalars().first() if w else None
            sc = (await session.execute(select(LeadScore).where(LeadScore.lead_id == l.id))).scalar_one_or_none() if l else None
            sne = (await session.execute(select(ServiceNeedEvidence).where(ServiceNeedEvidence.lead_id == l.id))).scalars().all() if l else []
            
            needs_summary = ", ".join([f"{sn.service_type}({sn.need_score})" for sn in sne])
            print(f"Company #{c.id} ({c.business_name}):")
            print(f"  Industry: {c.industry} | Category: {c.category}")
            print(f"  Website:  {c.website} (Verified: {w.website_official_verified if w else False})")
            print(f"  Audit:    Status={aud.audit_status if aud else 'N/A'}, Overall={aud.overall_score if aud else 'N/A'}, Mob={aud.mobile_score if aud else 'N/A'}, SEO={aud.seo_score if aud else 'N/A'}, Conv={aud.conversion_score if aud else 'N/A'}, Perf={aud.performance_score if aud else 'N/A'}")
            print(f"  Scores:   Opp={sc.opportunity_score if sc else 'N/A'}, DQ={l.data_quality_score if l else 'N/A'}, Contact={sc.contactability_score if sc else 'N/A'}, Stage={l.pipeline_stage if l else 'N/A'}")
            print(f"  Needs:    {needs_summary if needs_summary else 'None'}")
            print("-" * 90)

        # ---------------------------------------------------------------------
        # 6. FULL DATABASE ENTIRETY (JOBS 1 TO 9)
        # ---------------------------------------------------------------------
        all_jobs = (await session.execute(select(DiscoveryJob).order_by(DiscoveryJob.id))).scalars().all()
        tot_disc_all = sum(j.discovered_count for j in all_jobs)
        tot_comps_all = (await session.execute(select(func.count(Company.id)))).scalar() or 0
        tot_qual_all = (await session.execute(select(func.count(Lead.id)).where(Lead.is_qualified == True))).scalar() or 0
        tot_sales_all = (await session.execute(select(func.count(Lead.id)).where(Lead.is_sales_ready == True))).scalar() or 0

        print("\n--- 6. FULL DATABASE SCOPE (ALL JOBS) ---")
        print(f"Total Jobs in DB:                   {len(all_jobs)} (Jobs 1–7 Task-1175 + Jobs 8–{len(all_jobs)} Test Runs)")
        print(f"Total Discovered Records:           {tot_disc_all} ({tot_disc_1175} in Task-1175 + {tot_disc_all - tot_disc_1175} in subsequent runs)")
        print(f"Total Unique Business Entities:     {tot_comps_all} ({unique_comps_1175} in Task-1175 + {tot_comps_all - unique_comps_1175} in subsequent runs)")
        print(f"Total Qualified across DB:          {tot_qual_all}")
        print(f"Total Sales-Ready across DB:        {tot_sales_all}")
        print("=" * 90 + "\n")

if __name__ == "__main__":
    asyncio.run(generate_production_truth_report())
