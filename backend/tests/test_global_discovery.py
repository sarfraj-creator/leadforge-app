import pytest
from backend.app.services.discovery.openstreetmap import OpenStreetMapAdapter
from backend.app.services.verification.website_verifier import WebsiteVerifier
from backend.app.services.intent.intent_engine import BuyingIntentEngine
from backend.app.services.scoring.lead_scorer import lead_scorer
from backend.app.services.domain.domain_intel import DomainIntelligence

def test_osm_adapter_worldwide_query():
    adapter = OpenStreetMapAdapter()
    assert adapter.source_name == "OpenStreetMap"
    assert adapter.get_rate_limit() == 30

def test_website_verifier_signals():
    # Test high confidence
    html = "<html><head><title>Apex Dental Clinic - Official Website</title></head><body><h1>Welcome to Apex Dental Clinic</h1><p>Call us at 555-123-4567</p><a href='/contact'>Contact Us</a></body></html>"
    res = WebsiteVerifier.verify_website(
        business_name="Apex Dental Clinic",
        website_url="https://apexdental.com",
        html_content=html,
        status_code=200,
        phone="555-123-4567"
    )
    assert res["is_verified"] is True
    assert res["confidence"] in ["HIGH", "MEDIUM"]
    assert res["score"] >= 60

    # Test parked domain
    parked_html = "<html><head><title>Domain For Sale</title></head><body><p>This domain is for sale. Buy this domain now on HugeDomains.</p></body></html>"
    parked_res = WebsiteVerifier.verify_website(
        business_name="Apex Dental",
        website_url="https://apexdental.com",
        html_content=parked_html,
        status_code=200
    )
    assert parked_res["confidence"] == "LOW"
    assert parked_res["is_verified"] is False

    # Test unreachable site
    unreachable_res = WebsiteVerifier.verify_website(
        business_name="Apex Dental",
        website_url="https://apexdental.com",
        html_content=None,
        status_code=None
    )
    assert unreachable_res["confidence"] == "UNVERIFIED"
    assert unreachable_res["is_verified"] is False

def test_intent_engine_unknown_fallback():
    # Regular page with no intent
    html = "<html><body><p>Welcome to our family restaurant. Serving Italian food since 1998.</p></body></html>"
    intent = BuyingIntentEngine.detect_intent(html, "https://restaurant.com")
    assert intent["buying_intent"] == "UNKNOWN"
    assert intent["intent_score"] == 0
    assert len(intent["signals"]) == 0

    # Page with explicit hiring for developer
    hiring_html = "<html><body><p>We are expanding! We are seeking frontend developer and UI/UX designer for our digital portal.</p></body></html>"
    hiring_intent = BuyingIntentEngine.detect_intent(hiring_html, "https://restaurant.com/careers")
    assert hiring_intent["buying_intent"] in ["HIGH", "MEDIUM"]
    assert hiring_intent["intent_score"] > 0
    assert len(hiring_intent["signals"]) >= 1

def test_five_part_lead_scoring():
    # Calculate score for lead with website deficiency
    res = lead_scorer.calculate_score(
        has_website=True,
        audit=None,
        has_email=True,
        has_phone=True,
        is_fresh=True,
        website_reachable=True,
        website_official_verified=True,
        intent_info={"buying_intent": "UNKNOWN", "intent_score": 0}
    )
    assert "data_confidence_score" in res
    assert "business_fit_score" in res
    assert "opportunity_score" in res
    assert "intent_score" in res
    assert "contactability_score" in res
    assert "total_score" in res
    assert res["data_confidence_score"] >= 70
    assert res["contactability_score"] >= 45
    assert res["buying_intent"] == "UNKNOWN"
