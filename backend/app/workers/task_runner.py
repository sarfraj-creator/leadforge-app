import asyncio
import re
import json
import logging
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.user import Organization
from backend.app.models.discovery import DiscoveryJob, LeadSourceConfig
from backend.app.models.company import Company, LeadSourceRecord
from backend.app.models.website import Website, WebsitePage, WebsiteAudit, WebsiteAuditMetric, WebsiteIssue, WebsiteTechnology
from backend.app.models.contact import Contact, EmailVerificationRecord
from backend.app.models.lead import Lead, LeadScore, LeadOpportunity
from backend.app.models.crm import StageHistory
from backend.app.models.provenance import FieldProvenanceRecord
from backend.app.models.service_need import ServiceNeedEvidence
from backend.app.services.discovery.registry import source_registry
from backend.app.services.crawler.safe_crawler import safe_crawler
from backend.app.services.verification.website_verifier import WebsiteVerifier
from backend.app.services.verification.identity_verifier import BusinessIdentityVerifier
from backend.app.services.domain.domain_intel import DomainIntelligence
from backend.app.services.contact.verifier import email_verifier
from backend.app.services.contact.phone_verifier import phone_verifier
from backend.app.services.contact.decision_maker import decision_maker_finder
from backend.app.services.audit.engine import audit_engine
from backend.app.services.scoring.opportunity_engine import opportunity_engine
from backend.app.services.scoring.service_need_engine import service_need_engine
from backend.app.services.scoring.lead_scorer import lead_scorer
from backend.app.services.scoring.data_quality_scorer import data_quality_scorer
from backend.app.services.freshness.field_freshness import field_freshness_engine
from backend.app.services.conflict.contradiction_detector import contradiction_detector
from backend.app.services.intent.intent_engine import BuyingIntentEngine
from backend.app.services.verification.operating_status_verifier import OperatingStatusVerifier
from backend.app.services.discovery.taxonomy import resolve_industry_from_source

logger = logging.getLogger("leadforge.worker.task_runner")

class DiscoveryPipelineRunner:
    """
    Production-Hardened Discovery Pipeline with Field-Level Data Truth:
    DISCOVERED -> IDENTITY_VERIFIED -> WEBSITE_VERIFIED -> AUDITED -> OPPORTUNITY_DETECTED -> CONTACTABLE -> QUALIFIED -> SALES_READY
    """

    async def run_discovery_pipeline(self, job_id: int):
        logger.info("Starting hardened data-truth pipeline for Job ID #%d", job_id)
        now_utc = datetime.datetime.now(datetime.timezone.utc)

        async with AsyncSessionLocal() as session:
            job = await session.get(DiscoveryJob, job_id)
            if not job:
                logger.error("Job #%d not found", job_id)
                return

            job.status = "RUNNING"
            job.started_at = now_utc
            job.progress_percent = 5
            await session.commit()
            org_id = job.organization_id

        total_discovered = 0
        total_new = 0
        total_duplicates = 0
        total_websites = 0
        total_reachable = 0
        total_verified_sites = 0
        total_crawled = 0
        total_audits_complete = 0
        total_audits_incomplete = 0
        total_contacts = 0
        total_verified_emails = 0
        total_qualified = 0
        total_sales_ready = 0

        rejection_reasons = {
            "NO_WEBSITE": 0,
            "BROKEN_WEBSITE": 0,
            "PARKED_DOMAIN": 0,
            "IDENTITY_MISMATCH": 0,
            "LOW_DATA_CONFIDENCE": 0,
            "AUDIT_FAILED": 0,
            "NO_SERVICE_EVIDENCE": 0,
            "NO_CONTACT": 0,
            "CONFLICT": 0,
            "STALE_DATA": 0
        }
        geographic_coverage: Dict[str, int] = {}

        try:
            # 1. Multi-Source Lead Discovery (Google Maps, AI Search, OpenStreetMap, Search Engine)
            target_limit = min(job.max_leads or 50, 150)
            sources_to_query = [s.strip() for s in (job.sources_used or "OpenStreetMap").split(",") if s.strip()]
            
            discovered_records = await source_registry.run_discovery(
                sources=sources_to_query,
                query=job.keywords or job.industry,
                location=job.location,
                industry=job.industry,
                limit_per_source=max(15, target_limit // max(1, len(sources_to_query)))
            )
            total_discovered = len(discovered_records)
            logger.info("Multi-source discovery returned %d combined records from sources: %s", total_discovered, sources_to_query)

            if total_discovered == 0:
                async with AsyncSessionLocal() as session:
                    job = await session.get(DiscoveryJob, job_id)
                    job.status = "COMPLETED"
                    job.progress_percent = 100
                    job.discovered_count = 0
                    job.completed_at = datetime.datetime.now(datetime.timezone.utc)
                    job.error_message = "No records discovered from source for specified criteria."
                    await session.commit()
                return

            async with AsyncSessionLocal() as session:
                job = await session.get(DiscoveryJob, job_id)
                job.discovered_count = total_discovered
                job.progress_percent = 15
                await session.commit()

            # Process each discovered record
            for idx, record in enumerate(discovered_records):
                async with AsyncSessionLocal() as session:
                    # Normalize Phone
                    phone_norm = phone_verifier.verify_and_normalize(record.phone)

                    # 1. Company Ingestion & Deduplication
                    stmt = select(Company).where(
                        Company.organization_id == org_id,
                        Company.dedup_hash == record.dedup_hash
                    )
                    res = await session.execute(stmt)
                    company = res.scalar_one_or_none()

                    if not company:
                        resolved_ind = resolve_industry_from_source(
                            raw_tags=record.raw_data,
                            source_category=record.category,
                            query_industry=record.industry or job.industry
                        )
                        company = Company(
                            organization_id=org_id,
                            business_name=record.business_name,
                            industry=resolved_ind,
                            discovered_industry=resolved_ind,
                            verified_industry=resolved_ind,
                            category=record.category or "business",
                            address=record.address,
                            city=record.city,
                            country=record.country,
                            postal_code=record.postal_code,
                            phone=record.phone,
                            normalized_phone_e164=phone_norm["normalized_e164"],
                            phone_validation_status=phone_norm["validation_status"],
                            business_email=record.email,
                            website=record.website,
                            domain=record.domain,
                            source=record.source,
                            source_url=record.source_url,
                            confidence=record.confidence,
                            dedup_hash=record.dedup_hash,
                            latitude=record.latitude,
                            longitude=record.longitude,
                            company_observed_at=now_utc,
                            phone_observed_at=now_utc if record.phone else None,
                            email_observed_at=now_utc if record.email else None,
                            website_observed_at=now_utc if record.website else None,
                            discovered_at=now_utc,
                            last_seen_at=now_utc,
                            last_checked_at=now_utc
                        )
                        session.add(company)
                        await session.flush()
                        total_new += 1

                        # Geographic Coverage
                        country_label = record.country or record.city or "Worldwide"
                        geographic_coverage[country_label] = geographic_coverage.get(country_label, 0) + 1
                    else:
                        company.last_seen_at = now_utc
                        total_duplicates += 1

                    # Provenance Record
                    src_stmt = select(LeadSourceRecord).where(
                        LeadSourceRecord.company_id == company.id,
                        LeadSourceRecord.source_record_id == record.source_record_id
                    )
                    src_res = await session.execute(src_stmt)
                    if not src_res.scalar_one_or_none():
                        source_rec = LeadSourceRecord(
                            company_id=company.id,
                            source_name=record.source,
                            source_record_id=record.source_record_id,
                            source_url=record.source_url,
                            raw_data=json.dumps(record.raw_data),
                            confidence=record.confidence,
                            discovered_at=now_utc
                        )
                        session.add(source_rec)

                    # Track Field Provenance: Business Name, Address, Phone, Website
                    fields_to_track = [
                        ("company", company.id, "business_name", record.business_name, "OPENSTREETMAP_TAG", "VERIFIED"),
                        ("company", company.id, "industry", record.industry or job.industry, "OPENSTREETMAP_TAG", "VERIFIED"),
                        ("company", company.id, "city", record.city, "OPENSTREETMAP_TAG", "VERIFIED" if record.city else "UNKNOWN"),
                        ("company", company.id, "country", record.country, "OPENSTREETMAP_TAG", "VERIFIED" if record.country else "UNKNOWN"),
                        ("company", company.id, "phone", record.phone, "E164_ITU", phone_norm["validation_status"] if record.phone else "UNKNOWN"),
                        ("company", company.id, "website", record.website, "SOURCE_PROVIDED", "URL_DISCOVERED" if record.website else "UNKNOWN")
                    ]
                    for ent_type, ent_id, f_name, f_val, v_method, v_status in fields_to_track:
                        session.add(FieldProvenanceRecord(
                            organization_id=org_id,
                            entity_type=ent_type,
                            entity_id=ent_id,
                            field_name=f_name,
                            value=f_val,
                            source_type=record.source,
                            source_url=record.source_url,
                            source_record_id=record.source_record_id,
                            observed_at=now_utc,
                            verification_method=v_method,
                            verification_status=v_status,
                            confidence_score=record.confidence
                        ))

                    # 2. Official Website Crawling, Verification & Domain Intelligence
                    audit_res = None
                    website_obj = None
                    crawl = None
                    intent_info = {"buying_intent": "UNKNOWN", "intent_score": 0, "signals": []}
                    primary_email_status = None
                    has_contacts = False
                    identity_res = {"status": "UNVERIFIED", "score": 0, "signals": [], "is_verified": False}
                    web_verify_res = {"website_verification_status": "UNVERIFIED", "verification_score": 0, "verification_reasons": [], "is_verified": False}

                    if company.website:
                        total_websites += 1
                        w_stmt = select(Website).where(Website.company_id == company.id)
                        w_res = await session.execute(w_stmt)
                        website_obj = w_res.scalar_one_or_none()

                        crawl = await safe_crawler.crawl_site(
                            target_url=company.website,
                            business_name=company.business_name,
                            city=company.city
                        )
                        total_crawled += 1

                        # Multi-Signal Website Verification
                        web_verify_res = WebsiteVerifier.verify_website(
                            business_name=company.business_name,
                            website_url=company.website,
                            html_content=crawl.raw_html,
                            status_code=crawl.http_status,
                            phone=company.phone,
                            city=company.city
                        )
                        
                        if crawl.website_reachable:
                            total_reachable += 1
                        if web_verify_res["is_verified"]:
                            total_verified_sites += 1

                        # 9-Signal Business Identity Verification
                        if crawl.website_reachable and crawl.raw_html:
                            identity_res = BusinessIdentityVerifier.verify_identity(
                                business_name=company.business_name,
                                website_url=company.website,
                                domain=company.domain,
                                title=crawl.title,
                                h1_tags=crawl.h1_tags,
                                html_content=crawl.raw_html,
                                visible_text=getattr(crawl, "visible_text", "") or "",
                                address=company.address,
                                city=company.city,
                                country=company.country,
                                phone=company.phone
                            )
                        company.identity_verification_status = identity_res["status"]
                        company.identity_signals_json = json.dumps(identity_res["signals"])

                        # Domain Intelligence (DNS, MX, TLS)
                        domain_intel = await DomainIntelligence.get_domain_intel(company.domain or company.website)

                        # Buying Intent Detection (strictly evidence-based)
                        if crawl.website_reachable and crawl.raw_html:
                            intent_info = BuyingIntentEngine.detect_intent(
                                html_content=crawl.raw_html,
                                source_url=company.website
                            )

                        if not website_obj:
                            website_obj = Website(
                                company_id=company.id,
                                url=company.website,
                                domain=company.domain or "unknown.com",
                                canonical_url=crawl.canonical_url,
                                website_url_discovered=True,
                                website_reachable=crawl.website_reachable,
                                website_official_verified=web_verify_res["is_verified"],
                                website_verification_status=web_verify_res["website_verification_status"],
                                verification_score=web_verify_res["verification_score"],
                                verification_reasons_json=json.dumps(web_verify_res["verification_reasons"]),
                                status="WEBSITE_FOUND" if crawl.website_reachable else "WEBSITE_UNREACHABLE",
                                http_status=crawl.http_status,
                                ssl_valid=crawl.ssl_valid if crawl.ssl_valid is not None else domain_intel["tls_valid"],
                                html_hash=crawl.html_hash,
                                content_hash=crawl.content_hash,
                                last_crawled_at=now_utc,
                                last_audited_at=now_utc
                            )
                            session.add(website_obj)
                            await session.flush()
                        else:
                            website_obj.website_reachable = crawl.website_reachable
                            website_obj.website_official_verified = web_verify_res["is_verified"]
                            website_obj.website_verification_status = web_verify_res["website_verification_status"]
                            website_obj.verification_score = web_verify_res["verification_score"]
                            website_obj.verification_reasons_json = json.dumps(web_verify_res["verification_reasons"])
                            website_obj.html_hash = crawl.html_hash
                            website_obj.content_hash = crawl.content_hash
                            website_obj.http_status = crawl.http_status
                            website_obj.ssl_valid = crawl.ssl_valid if crawl.ssl_valid is not None else domain_intel["tls_valid"]
                            website_obj.last_crawled_at = now_utc
                            website_obj.last_audited_at = now_utc

                        # 3. Deterministic Website Audit (7 Dimensions)
                        audit_res = audit_engine.audit(crawl)
                        if audit_res.status == "AUDIT_COMPLETE":
                            total_audits_complete += 1
                        else:
                            total_audits_incomplete += 1

                        w_audit = WebsiteAudit(
                            website_id=website_obj.id,
                            audit_status=audit_res.status,
                            overall_score=audit_res.overall_score,
                            performance_score=audit_res.performance_score,
                            mobile_score=audit_res.mobile_score,
                            seo_score=audit_res.seo_score,
                            accessibility_score=audit_res.accessibility_score,
                            security_score=audit_res.security_score,
                            ux_score=audit_res.ux_score,
                            conversion_score=audit_res.conversion_score,
                            summary=audit_res.summary
                        )
                        session.add(w_audit)
                        await session.flush()

                        # Save Metrics, Issues, Technologies
                        for m in audit_res.metrics:
                            session.add(WebsiteAuditMetric(
                                audit_id=w_audit.id,
                                category=m["category"],
                                metric_name=m["metric_name"],
                                value=m["value"],
                                score=m.get("score")
                            ))
                        for iss in audit_res.issues:
                            session.add(WebsiteIssue(
                                audit_id=w_audit.id,
                                category=iss["category"],
                                title=iss["title"],
                                severity=iss["severity"],
                                evidence=iss["evidence"],
                                recommendation=iss["recommendation"]
                            ))
                        for t in audit_res.technologies:
                            session.add(WebsiteTechnology(
                                audit_id=w_audit.id,
                                name=t["name"],
                                category=t["category"],
                                version=t.get("version"),
                                confidence=t["confidence"]
                            ))

                        # Public Contact Extraction & LinkedIn Profile Enrichment
                        observed_crawl_phone = None
                        discovered_contacts = []
                        if crawl and crawl.website_reachable:
                            discovered_contacts = decision_maker_finder.extract_contacts_from_crawl(
                                crawl=crawl,
                                company_name=company.business_name,
                                source_url=company.website
                            )

                        # Merge AI-discovered decision maker if present in raw_data
                        raw_dm_name = record.raw_data.get("decision_maker_name") or record.raw_data.get("author_name")
                        raw_dm_role = record.raw_data.get("decision_maker_role") or record.raw_data.get("author_title") or "Executive / Founder"
                        raw_dm_li = record.raw_data.get("decision_maker_linkedin") or record.raw_data.get("author_linkedin_url")

                        if raw_dm_name:
                            already_present = any(c.get("full_name") == raw_dm_name for c in discovered_contacts)
                            if not already_present:
                                discovered_contacts.insert(0, {
                                    "full_name": raw_dm_name,
                                    "job_title": raw_dm_role,
                                    "linkedin_url": raw_dm_li,
                                    "email": record.email or company.business_email,
                                    "phone": record.phone or company.phone,
                                    "is_decision_maker": True,
                                    "contact_source": f"Grounded AI Discovery ({record.source})",
                                    "source_url": record.source_url or company.website,
                                    "confidence": 0.95
                                })
                            else:
                                for c in discovered_contacts:
                                    if c.get("full_name") == raw_dm_name and raw_dm_li:
                                        c["linkedin_url"] = raw_dm_li

                        for dc in discovered_contacts:
                            contact_email = dc.get("email") or company.business_email
                            c_phone = dc.get("phone") or company.phone
                            c_phone_norm = phone_verifier.verify_and_normalize(c_phone)
                            if dc.get("phone"):
                                observed_crawl_phone = dc.get("phone")

                            # Look for LinkedIn URL in crawled HTML if not yet present
                            c_linkedin = dc.get("linkedin_url") or raw_dm_li
                            if not c_linkedin and crawl and crawl.raw_html:
                                li_matches = re.findall(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', crawl.raw_html)
                                if li_matches:
                                    c_linkedin = li_matches[0]

                            c_record = Contact(
                                company_id=company.id,
                                full_name=dc["full_name"],
                                job_title=dc.get("job_title"),
                                is_decision_maker=dc.get("is_decision_maker", False),
                                linkedin_url=c_linkedin,
                                email=contact_email,
                                phone=c_phone,
                                normalized_phone_e164=c_phone_norm["normalized_e164"],
                                phone_validation_status=c_phone_norm["validation_status"],
                                source=dc.get("contact_source", "Official Website"),
                                source_url=dc.get("source_url") or company.website,
                                confidence=dc.get("confidence", 0.9),
                                observed_at=now_utc
                            )
                            session.add(c_record)
                            await session.flush()
                            total_contacts += 1
                            has_contacts = True

                            # Email Verification
                            if contact_email:
                                v_res = await email_verifier.verify(contact_email)
                                c_record.email_status = v_res["status"]
                                c_record.syntax_valid = v_res["syntax_valid"]
                                c_record.domain_valid = v_res["domain_valid"]
                                c_record.mx_valid = v_res["mx_valid"]
                                c_record.mailbox_verified = v_res["mailbox_verified"]
                                c_record.email_verified_at = now_utc
                                primary_email_status = v_res["status"]
                                session.add(EmailVerificationRecord(
                                    contact_id=c_record.id,
                                    email=contact_email,
                                    status=v_res["status"],
                                    reason=v_res.get("reason"),
                                    confidence=v_res.get("confidence", 1.0)
                                ))
                                if v_res["mx_valid"]:
                                    total_verified_emails += 1

                                # Field provenance for email
                                session.add(FieldProvenanceRecord(
                                    organization_id=org_id,
                                    entity_type="contact",
                                    entity_id=c_record.id,
                                    field_name="email",
                                    value=contact_email,
                                    source_type=record.source,
                                    source_url=company.website or record.source_url,
                                    observed_at=now_utc,
                                    verification_method="DNS_MX",
                                    verification_status=v_res["status"],
                                    confidence_score=v_res["confidence"]
                                ))

                        # Cross-Source Contradiction Detection
                        conflict_res = contradiction_detector.detect_conflicts(
                            company_name_source=record.business_name,
                            company_name_observed=crawl.title,
                            phone_source=record.phone,
                            phone_observed=observed_crawl_phone,
                            website_source=record.website,
                            website_observed=crawl.canonical_url,
                            city_source=record.city,
                            city_observed=company.city
                        )
                        company.has_conflicts = conflict_res["has_conflicts"]
                        company.conflict_count = conflict_res["conflict_count"]

                    # 4. Service Need Evidence Engine (9 Core Services)
                    service_items = service_need_engine.evaluate_services(
                        has_website=bool(company.website),
                        audit=audit_res,
                        source_url=company.website
                    )

                    # 5. Opportunity & Decoupled 5-Part Lead Scoring
                    opps, primary_service = opportunity_engine.evaluate(
                        has_website=bool(company.website),
                        audit=audit_res,
                        has_contact_email=bool(company.business_email or has_contacts),
                        has_phone=bool(company.phone),
                        is_fresh=True
                    )

                    score_info = lead_scorer.calculate_score(
                        has_website=bool(company.website),
                        audit=audit_res,
                        opportunities=opps,
                        has_email=bool(company.business_email or has_contacts),
                        email_status=primary_email_status,
                        has_phone=bool(company.phone),
                        has_form=bool(crawl and len(crawl.forms) > 0),
                        is_fresh=True,
                        website_reachable=bool(crawl and crawl.website_reachable),
                        website_official_verified=bool(crawl and crawl.website_official_verified),
                        intent_info=intent_info,
                        has_source_provenance=True
                    )

                    # 6. Data Quality Score (0-100)
                    data_quality_res = data_quality_scorer.calculate_data_quality(
                        source_name=record.source,
                        identity_status=company.identity_verification_status,
                        website_status=web_verify_res["website_verification_status"],
                        email_status=primary_email_status,
                        phone_status=company.phone_validation_status,
                        freshness_state="FRESH",
                        has_conflicts=company.has_conflicts
                    )

                    # 7. Strict 8-Stage Canonical Lifecycle Calculation
                    # DISCOVERED -> IDENTITY_VERIFIED -> WEBSITE_VERIFIED -> AUDITED -> OPPORTUNITY_DETECTED -> CONTACTABLE -> QUALIFIED -> SALES_READY
                    has_verified_identity = bool(company.identity_verification_status in ["HIGH", "MEDIUM", "LOW"])
                    has_verified_website = bool(web_verify_res["is_verified"] or not company.website)
                    has_complete_audit = bool((audit_res and audit_res.status == "AUDIT_COMPLETE") or not company.website)
                    has_qualifying_opportunity = bool(score_info["opportunity_score"] >= 60)
                    has_qualifying_quality = bool(data_quality_res["total_score"] >= 70)

                    canonical_qualified = (
                        has_verified_identity
                        and has_verified_website
                        and has_complete_audit
                        and has_qualifying_opportunity
                        and has_qualifying_quality
                    )

                    if canonical_qualified:
                        lifecycle_stage = "QUALIFIED"
                    elif (company.business_email or has_contacts) and primary_email_status in ["DOMAIN_MAIL_ENABLED", "MAILBOX_VERIFIED"]:
                        lifecycle_stage = "CONTACTABLE"
                    elif len(service_items) > 0 and audit_res and audit_res.status == "AUDIT_COMPLETE":
                        lifecycle_stage = "OPPORTUNITY_DETECTED"
                    elif audit_res and audit_res.status == "AUDIT_COMPLETE":
                        lifecycle_stage = "AUDITED"
                    elif web_verify_res["is_verified"]:
                        lifecycle_stage = "WEBSITE_VERIFIED"
                    elif company.identity_verification_status in ["HIGH", "MEDIUM"]:
                        lifecycle_stage = "IDENTITY_VERIFIED"
                    else:
                        lifecycle_stage = "DISCOVERED"

                    is_qual = canonical_qualified
                    # SALES_READY strictly requires canonical_qualified + contactability >= 50 + human review approval (APPROVED)
                    is_sales_ready = False

                    # Operating Status Determination
                    op_res = OperatingStatusVerifier.determine_operating_status(
                        business_name=company.business_name,
                        website_reachable=crawl.website_reachable if crawl else False,
                        http_status=crawl.http_status if crawl else None,
                        html_content=crawl.raw_html if crawl else None,
                        phone_valid=bool(company.phone_validation_status == "VALID_E164"),
                        observed_at=now_utc,
                        source_name=record.source,
                        opening_hours=record.raw_data.get("opening_hours") if record.raw_data else None,
                        raw_source_tags=record.raw_data
                    )
                    company.operating_status = op_res["status"]
                    company.operating_status_evidence_json = json.dumps(op_res["evidence"])

                    # Rejection Telemetry Attribution
                    if not is_qual:
                        if not company.website:
                            rejection_reasons["NO_WEBSITE"] += 1
                        elif not crawl or not crawl.website_reachable:
                            rejection_reasons["BROKEN_WEBSITE"] += 1
                        elif web_verify_res.get("website_verification_status") == "PARKED":
                            rejection_reasons["PARKED_DOMAIN"] += 1
                        elif company.identity_verification_status not in ["HIGH", "MEDIUM"]:
                            rejection_reasons["IDENTITY_MISMATCH"] += 1
                        elif not audit_res or audit_res.status != "AUDIT_COMPLETE":
                            rejection_reasons["AUDIT_FAILED"] += 1
                        elif not company.business_email and not has_contacts:
                            rejection_reasons["NO_CONTACT"] += 1
                        elif company.has_conflicts:
                            rejection_reasons["CONFLICT"] += 1
                        elif data_quality_res["total_score"] < 65:
                            rejection_reasons["LOW_DATA_CONFIDENCE"] += 1
                        else:
                            rejection_reasons["NO_SERVICE_EVIDENCE"] += 1

                    if is_qual:
                        total_qualified += 1
                    if is_sales_ready:
                        total_sales_ready += 1

                    crm_stage = "Sales Ready" if is_sales_ready else ("Qualified" if is_qual else "Discovered")

                    # 8. Lead Entity Creation & Relation Storage
                    l_stmt = select(Lead).where(Lead.company_id == company.id)
                    l_res = await session.execute(l_stmt)
                    lead_obj = l_res.scalar_one_or_none()

                    if not lead_obj:
                        lead_obj = Lead(
                            organization_id=org_id,
                            company_id=company.id,
                            pipeline_stage=lifecycle_stage,
                            is_qualified=is_qual,
                            is_sales_ready=is_sales_ready,
                            needs_review=True,
                            review_status="PENDING",
                            stage=crm_stage,
                            data_quality_score=data_quality_res["total_score"],
                            data_quality_breakdown_json=json.dumps(data_quality_res["breakdown"]),
                            primary_opportunity=opps[0].opportunity_type if opps else ("Website Build" if not company.website else "Audit Incomplete"),
                            recommended_service=primary_service,
                            freshness_state="FRESH"
                        )
                        session.add(lead_obj)
                        await session.flush()

                        session.add(LeadScore(
                            lead_id=lead_obj.id,
                            total_score=score_info["total_score"],
                            category=score_info["category"],
                            data_confidence_score=score_info["data_confidence_score"],
                            business_fit_score=score_info["business_fit_score"],
                            opportunity_score=score_info["opportunity_score"],
                            intent_score=score_info["intent_score"],
                            buying_intent=score_info["buying_intent"],
                            contactability_score=score_info["contactability_score"],
                            rules_applied=json.dumps(score_info["rules_applied"]),
                            explanation=score_info["explanation"]
                        ))

                        for op in opps:
                            session.add(LeadOpportunity(
                                lead_id=lead_obj.id,
                                opportunity_type=op.opportunity_type,
                                confidence=op.confidence,
                                observed_evidence=op.observed_evidence,
                                inferred_benefit=op.inferred_benefit
                            ))

                        for sni in service_items:
                            session.add(ServiceNeedEvidence(
                                lead_id=lead_obj.id,
                                service_type=sni.service_type,
                                need_score=sni.need_score,
                                evidence_json=json.dumps(sni.evidence),
                                source_url=sni.source_url,
                                confidence=sni.confidence,
                                observed_at=now_utc
                            ))
                    else:
                        lead_obj.pipeline_stage = lifecycle_stage
                        lead_obj.is_qualified = is_qual
                        lead_obj.is_sales_ready = is_sales_ready
                        lead_obj.data_quality_score = data_quality_res["total_score"]
                        lead_obj.data_quality_breakdown_json = json.dumps(data_quality_res["breakdown"])

                    # Update live progress telemetry
                    progress = 15 + int(((idx + 1) / total_discovered) * 80)
                    job = await session.get(DiscoveryJob, job_id)
                    if job:
                        job.progress_percent = min(98, progress)
                        job.new_businesses_count = total_new
                        job.duplicates_count = total_duplicates
                        job.websites_found_count = total_websites
                        job.websites_reachable_count = total_reachable
                        job.websites_verified_count = total_verified_sites
                        job.websites_crawled_count = total_crawled
                        job.audits_completed_count = total_audits_complete
                        job.audits_incomplete_count = total_audits_incomplete
                        job.contacts_found_count = total_contacts
                        job.verified_emails_count = total_verified_emails
                        job.qualified_leads_count = total_qualified
                        job.sales_ready_count = total_sales_ready

                    await session.commit()

            # Mark Completed
            async with AsyncSessionLocal() as session:
                job = await session.get(DiscoveryJob, job_id)
                job.status = "COMPLETED"
                job.progress_percent = 100
                job.new_businesses_count = total_new
                job.duplicates_count = total_duplicates
                job.websites_found_count = total_websites
                job.websites_reachable_count = total_reachable
                job.websites_verified_count = total_verified_sites
                job.websites_crawled_count = total_crawled
                job.audits_completed_count = total_audits_complete
                job.audits_incomplete_count = total_audits_incomplete
                job.contacts_found_count = total_contacts
                job.verified_emails_count = total_verified_emails
                job.qualified_leads_count = total_qualified
                job.sales_ready_count = total_sales_ready
                job.rejection_reasons_json = json.dumps(rejection_reasons)
                job.geographic_coverage_json = json.dumps(geographic_coverage)
                job.completed_at = datetime.datetime.now(datetime.timezone.utc)
                await session.commit()

            logger.info("Hardened pipeline finished for Job #%d. Total Discovered=%d, Verified Sites=%d, Qualified=%d, Sales Ready=%d",
                        job_id, total_discovered, total_verified_sites, total_qualified, total_sales_ready)

        except Exception as e:
            logger.exception("Pipeline failed for Job #%d: %s", job_id, e)
            async with AsyncSessionLocal() as session:
                job = await session.get(DiscoveryJob, job_id)
                if job:
                    job.status = "FAILED"
                    job.error_message = str(e)
                    job.completed_at = datetime.datetime.now(datetime.timezone.utc)
                    await session.commit()

    async def run_pipeline_wrapper(self, job_id: int):
        await self.run_discovery_pipeline(job_id)

task_runner = DiscoveryPipelineRunner()
