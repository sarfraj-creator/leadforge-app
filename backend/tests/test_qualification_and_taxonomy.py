import pytest
from backend.app.services.scoring.lead_scorer import lead_scorer
from backend.app.services.scoring.data_quality_scorer import data_quality_scorer
from backend.app.services.discovery.taxonomy import resolve_industry_from_source
from backend.app.services.audit.engine import AuditResult

def test_qualification_data_quality_boundary_69_vs_70():
    """DQ 69 cannot qualify, DQ 70 can qualify if all other requirements pass."""
    # Data confidence 69
    res_69 = lead_scorer.calculate_score(
        has_website=True,
        audit=AuditResult(),
        opportunities=[],
        has_email=True,
        email_status="DOMAIN_MAIL_ENABLED",
        has_phone=True,
        is_fresh=True,
        website_reachable=True,
        website_official_verified=True,
        has_source_provenance=True
    )
    # Set audit complete
    audit_comp = AuditResult()
    audit_comp.status = "AUDIT_COMPLETE"
    audit_comp.mobile_score = 30 # gives opp score +25 + base 20 + conv 20 = 65 >= 60

    # With DQ < 70 (e.g. data_confidence = 69 or DQ total < 70)
    score_res = lead_scorer.calculate_score(
        has_website=True,
        audit=audit_comp,
        has_email=False,
        has_phone=True,
        is_fresh=False,
        website_reachable=True,
        website_official_verified=False, # reduces confidence below 70
        has_source_provenance=True
    )
    assert score_res["data_confidence_score"] < 70
    assert score_res["is_qualified"] is False

    # With DQ >= 70
    score_res_pass = lead_scorer.calculate_score(
        has_website=True,
        audit=audit_comp,
        has_email=True,
        email_status="DOMAIN_MAIL_ENABLED",
        has_phone=True,
        is_fresh=True,
        website_reachable=True,
        website_official_verified=True,
        has_source_provenance=True
    )
    assert score_res_pass["data_confidence_score"] >= 70
    assert score_res_pass["opportunity_score"] >= 60
    assert score_res_pass["is_qualified"] is True

def test_qualification_opportunity_boundary_59_vs_60():
    """opportunity 59 cannot qualify, opportunity 60 can qualify if all other requirements pass."""
    # Audit with no defects (opportunity score = 15 or 20 < 60)
    audit_good = AuditResult()
    audit_good.status = "AUDIT_COMPLETE"
    audit_good.mobile_score = 90
    audit_good.performance_score = 90
    audit_good.seo_score = 90
    audit_good.conversion_score = 90
    audit_good.security_score = 90
    audit_good.overall_score = 90

    res_fail = lead_scorer.calculate_score(
        has_website=True,
        audit=audit_good,
        has_email=True,
        email_status="DOMAIN_MAIL_ENABLED",
        has_phone=True,
        is_fresh=True,
        website_reachable=True,
        website_official_verified=True,
        has_source_provenance=True
    )
    assert res_fail["opportunity_score"] < 60
    assert res_fail["is_qualified"] is False

    # Audit with defect (opportunity score >= 60)
    audit_defect = AuditResult()
    audit_defect.status = "AUDIT_COMPLETE"
    audit_defect.mobile_score = 30
    audit_defect.seo_score = 20
    audit_defect.conversion_score = 20
    audit_defect.overall_score = 50

    res_pass = lead_scorer.calculate_score(
        has_website=True,
        audit=audit_defect,
        has_email=True,
        email_status="DOMAIN_MAIL_ENABLED",
        has_phone=True,
        is_fresh=True,
        website_reachable=True,
        website_official_verified=True,
        has_source_provenance=True
    )
    assert res_pass["opportunity_score"] >= 60
    assert res_pass["is_qualified"] is True

def test_pending_review_cannot_produce_sales_ready():
    """pending review cannot produce SALES_READY."""
    audit_defect = AuditResult()
    audit_defect.status = "AUDIT_COMPLETE"
    audit_defect.mobile_score = 30
    audit_defect.seo_score = 20
    audit_defect.conversion_score = 20
    audit_defect.overall_score = 50

    res = lead_scorer.calculate_score(
        has_website=True,
        audit=audit_defect,
        has_email=True,
        email_status="DOMAIN_MAIL_ENABLED",
        has_phone=True,
        is_fresh=True,
        website_reachable=True,
        website_official_verified=True,
        has_source_provenance=True
    )
    # Lead scorer sets is_sales_ready=False because approval is required
    assert res["is_sales_ready"] is False
    assert res["pipeline_stage"] == "QUALIFIED"

def test_contactability_boundary_49_vs_50():
    """contactability 49 cannot qualify for sales ready; contactability 50 can produce SALES_READY only after APPROVED."""
    # Contactability < 50 (only phone 30 pts)
    res_phone_only = lead_scorer.calculate_score(
        has_website=True,
        audit=None,
        has_email=False,
        has_phone=True
    )
    assert res_phone_only["contactability_score"] == 30
    assert res_phone_only["contactability_score"] < 50

    # Contactability >= 50 (email MX 45 + phone 30 = 75 pts)
    res_email_phone = lead_scorer.calculate_score(
        has_website=True,
        audit=None,
        has_email=True,
        email_status="DOMAIN_MAIL_ENABLED",
        has_phone=True
    )
    assert res_email_phone["contactability_score"] >= 50

def test_taxonomy_osm_amenity_restaurant_cannot_inherit_real_estate():
    """OSM amenity=restaurant cannot inherit Real_Estate."""
    raw_tags = {
        "amenity": "restaurant",
        "cuisine": "burger",
        "name": "Harry's Charbroiled"
    }
    resolved = resolve_industry_from_source(
        raw_tags=raw_tags,
        source_category="restaurant",
        query_industry="Real_Estate"
    )
    assert resolved == "Restaurant"
    assert resolved != "Real Estate"
    assert resolved != "Real_Estate"

def test_taxonomy_explicit_source_overrides_campaign_query():
    """explicit verified source taxonomy overrides campaign query taxonomy."""
    # Tag is lawyer, query was gym
    resolved_lawyer = resolve_industry_from_source(
        raw_tags={"office": "lawyer"},
        query_industry="gym"
    )
    assert resolved_lawyer == "Law Firm"

    # Tag is hotel, query was restaurant
    resolved_hotel = resolve_industry_from_source(
        raw_tags={"tourism": "hotel"},
        query_industry="restaurant"
    )
    assert resolved_hotel == "Hotel / Hospitality"

    # Tag is fitness_centre, query was real_estate
    resolved_gym = resolve_industry_from_source(
        raw_tags={"leisure": "fitness_centre"},
        query_industry="real_estate"
    )
    assert resolved_gym == "Gym / Fitness"

def test_taxonomy_fallback_works_only_when_explicit_source_is_absent():
    """fallback taxonomy works only when explicit source evidence is absent."""
    resolved_fallback = resolve_industry_from_source(
        raw_tags={},
        source_category=None,
        query_industry="real_estate"
    )
    assert resolved_fallback == "Real Estate"

def test_no_synthetic_contacts():
    """Zero synthetic contacts permitted."""
    from backend.app.services.contact.decision_maker import decision_maker_finder
    from backend.app.services.crawler.safe_crawler import CrawlResult

    crawl = CrawlResult("https://example.com")
    crawl.is_reachable = True
    crawl.raw_html = "<html><body><h1>Acme Corporation</h1><p>Contact our general inquiry line at info@acme.com</p></body></html>"
    
    contacts = decision_maker_finder.extract_contacts_from_crawl(crawl, "Acme Corporation")
    # General inquiry line must NOT produce a fake person/CEO
    assert len(contacts) == 0
