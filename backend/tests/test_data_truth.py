import pytest
import datetime
from backend.app.services.verification.identity_verifier import BusinessIdentityVerifier
from backend.app.services.verification.website_verifier import WebsiteVerifier
from backend.app.services.verification.operating_status_verifier import OperatingStatusVerifier
from backend.app.services.contact.phone_verifier import phone_verifier
from backend.app.services.contact.verifier import email_verifier
from backend.app.services.contact.decision_maker import decision_maker_finder
from backend.app.services.intent.intent_engine import BuyingIntentEngine
from backend.app.services.audit.engine import audit_engine
from backend.app.services.crawler.safe_crawler import CrawlResult
from backend.app.services.scoring.data_quality_scorer import data_quality_scorer
from backend.app.services.conflict.contradiction_detector import contradiction_detector
from backend.app.services.scoring.service_need_engine import service_need_engine

def test_no_data_fabrication_missing_contact_phone_email():
    # When no email or phone is discovered, they must remain None/NULL
    norm_phone = phone_verifier.verify_and_normalize(None)
    assert norm_phone["raw_phone"] is None
    assert norm_phone["normalized_e164"] is None
    assert norm_phone["validation_status"] == "UNVERIFIED"

    norm_empty = phone_verifier.verify_and_normalize("   ")
    assert norm_empty["normalized_e164"] is None

def test_contact_person_truth_no_generic_fabrication():
    # When page only has generic info emails, full_name must be None, NOT a fabricated string
    crawl = CrawlResult("https://examplecorp.com")
    crawl.is_reachable = True
    crawl.raw_html = "<html><body><a href='mailto:info@examplecorp.com'>Email Us</a></body></html>"
    crawl.emails = {"info@examplecorp.com"}
    
    contacts = decision_maker_finder.extract_contacts_from_crawl(crawl, "Example Corp")
    assert len(contacts) == 1
    assert contacts[0]["email"] == "info@examplecorp.com"
    assert contacts[0]["full_name"] is None # NEVER fabricated as "Example Corp Team"
    assert contacts[0]["job_title"] is None

def test_operating_status_determination_active():
    # Active website with recent copyright, booking signal, and phone
    html = "<html><body><h1>Open Today</h1><a href='/book'>Book Now</a><footer>© 2026 Example Corp</footer></body></html>"
    res = OperatingStatusVerifier.determine_operating_status(
        business_name="Example Corp",
        website_reachable=True,
        http_status=200,
        html_content=html,
        phone_valid=True
    )
    assert res["status"] in ["ACTIVE", "PROBABLY_ACTIVE"]
    assert len(res["evidence"]) >= 2

def test_operating_status_determination_closed():
    # Explicit closed notice
    html = "<html><body><h1>Example Corp</h1><p>We are permanently closed. Thank you for 20 years.</p></body></html>"
    res = OperatingStatusVerifier.determine_operating_status(
        business_name="Example Corp",
        website_reachable=True,
        http_status=200,
        html_content=html
    )
    assert res["status"] == "PERMANENTLY_CLOSED"
    assert res["confidence"] >= 0.8

def test_no_intent_fabrication_from_website_defects():
    # A page with massive performance and layout defects must NOT have buying intent
    bad_page_html = "<html><head><title>Old Plumbing</title></head><body><h1>Welcome</h1><p>Call our office for service.</p></body></html>"
    
    intent = BuyingIntentEngine.detect_intent(bad_page_html, "https://oldplumbing.com")
    assert intent["buying_intent"] == "UNKNOWN"
    assert intent["intent_score"] == 0
    assert len(intent["signals"]) == 0

def test_intent_requires_observable_signals():
    # Only genuine hiring/RFP announcements can trigger intent
    rfp_html = "<html><body><p>We have released a request for proposal (RFP) for agency web redesign and portal development.</p></body></html>"
    intent = BuyingIntentEngine.detect_intent(rfp_html, "https://example.com/rfp")
    assert intent["buying_intent"] in ["HIGH", "MEDIUM"]
    assert intent["intent_score"] > 0
    assert len(intent["signals"]) >= 1

def test_unverified_website_does_not_become_official():
    # Generic parked domain must NOT be verified
    parked_html = "<html><head><title>Domain For Sale</title></head><body><p>This domain is for sale on Sedo.</p></body></html>"
    res = WebsiteVerifier.verify_website(
        business_name="Acme Dental",
        website_url="https://acmedental.com",
        html_content=parked_html,
        status_code=200
    )
    assert res["website_verification_status"] == "PARKED"
    assert res["is_verified"] is False
    assert res["verification_score"] <= 10

def test_business_identity_cross_match_signals():
    # Real brand matching
    html = "<html><head><title>Apex Law Chambers - London</title></head><body><h1>Apex Law Chambers</h1><p>Located in London. Call 02079460123.</p></body></html>"
    res = BusinessIdentityVerifier.verify_identity(
        business_name="Apex Law Chambers",
        website_url="https://apexlaw.co.uk",
        domain="apexlaw.co.uk",
        title="Apex Law Chambers - London",
        h1_tags=["Apex Law Chambers"],
        html_content=html,
        visible_text="Located in London. Call 02079460123.",
        city="London",
        phone="02079460123"
    )
    assert res["status"] in ["HIGH", "MEDIUM"]
    assert res["is_verified"] is True
    assert res["score"] >= 60

def test_contradiction_detection():
    # Discrepancy between OSM phone and Website phone
    conflicts = contradiction_detector.detect_conflicts(
        company_name_source="City Cafe",
        company_name_observed="City Cafe Official",
        phone_source="+44 20 7946 0999",
        phone_observed="+44 20 7123 4567",
        website_source="https://citycafe.co.uk",
        website_observed="https://citycafe.co.uk",
        city_source="London",
        city_observed="London"
    )
    assert conflicts["has_conflicts"] is True
    assert conflicts["conflict_count"] >= 1
    assert conflicts["conflicts"][0]["field"] == "phone"

def test_data_quality_score_calculation():
    dq = data_quality_scorer.calculate_data_quality(
        source_name="OpenStreetMap",
        identity_status="HIGH",
        website_status="OFFICIAL_VERIFIED",
        email_status="DOMAIN_MAIL_ENABLED",
        phone_status="VALID_E164",
        freshness_state="FRESH",
        has_conflicts=False
    )
    assert dq["total_score"] >= 85
    assert dq["breakdown"]["source_reliability"]["points"] > 0
    assert dq["breakdown"]["identity_verification"]["points"] == 20
    assert dq["breakdown"]["website_verification"]["points"] == 20

def test_service_need_evidence_strictly_from_measurements():
    crawl = CrawlResult("https://slow-site.com")
    crawl.is_reachable = True
    crawl.load_time_ms = 4500
    crawl.page_size_bytes = 3500000
    crawl.viewport_meta = None
    crawl.raw_html = "<html><body><h1>Slow Site</h1></body></html>"
    
    audit = audit_engine.audit(crawl)
    needs = service_need_engine.evaluate_services(has_website=True, audit=audit, source_url="https://slow-site.com")
    
    service_types = [n.service_type for n in needs]
    assert "WEB_DESIGN" in service_types or "PERFORMANCE" in service_types
    for n in needs:
        assert len(n.evidence) > 0
