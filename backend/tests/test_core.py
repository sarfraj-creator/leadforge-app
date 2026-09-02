import pytest
import asyncio
from backend.app.core.ssrf import validate_url_for_ssrf
from backend.app.core.deduplication import normalize_domain, normalize_business_name, normalize_phone, normalize_email, compute_dedup_hash
from backend.app.services.audit.engine import audit_engine
from backend.app.services.crawler.safe_crawler import CrawlResult
from backend.app.services.scoring.opportunity_engine import opportunity_engine
from backend.app.services.scoring.lead_scorer import lead_scorer
from backend.app.services.freshness.freshness_tracker import freshness_tracker
from backend.app.services.contact.verifier import email_verifier
from backend.app.services.email.sender import email_sender

def test_ssrf_validation():
    # Dangerous URLs must be blocked
    assert validate_url_for_ssrf("http://localhost")[0] is False
    assert validate_url_for_ssrf("http://127.0.0.1:8000")[0] is False
    assert validate_url_for_ssrf("http://169.254.169.254/latest/meta-data/")[0] is False
    assert validate_url_for_ssrf("file:///etc/passwd")[0] is False
    assert validate_url_for_ssrf("javascript:alert(1)")[0] is False
    assert validate_url_for_ssrf("http://user:pass@example.com")[0] is False
    
    # Safe public URLs must pass
    assert validate_url_for_ssrf("https://example.com")[0] is True
    assert validate_url_for_ssrf("https://google.com")[0] is True

def test_deduplication_and_normalization():
    assert normalize_domain("https://www.GrandBistroMumbai.in/about?ref=1") == "grandbistromumbai.in"
    assert normalize_business_name("Grand Bistro Pvt Ltd.") == "grand bistro"
    assert normalize_phone("+91 (22) 2495-1100") == "+912224951100"
    assert normalize_email(" Contact@GrandBistro.in ") == "contact@grandbistro.in"
    
    h1 = compute_dedup_hash("Grand Bistro", "https://grandbistromumbai.in")
    h2 = compute_dedup_hash("Grand Bistro Pvt Ltd", "http://www.grandbistromumbai.in")
    assert h1 == h2

def test_deterministic_audit_and_opportunity():
    crawl = CrawlResult("https://example.com")
    crawl.is_reachable = True
    crawl.load_time_ms = 4200 # Slow
    crawl.page_size_bytes = 1024 * 1024
    crawl.viewport_meta = None # Missing viewport
    crawl.title = "Example"
    crawl.meta_description = ""
    crawl.raw_html = "<html><body><h1>Hello</h1></body></html>"
    
    audit = audit_engine.audit(crawl)
    assert audit.mobile_score < 60
    assert audit.performance_score < 60
    assert len(audit.issues) > 0
    
    opps, rec = opportunity_engine.evaluate(has_website=True, audit=audit)
    assert any(op.opportunity_type == "Responsive Redesign" for op in opps)
    
    score_res = lead_scorer.calculate_score(
        has_website=True,
        audit=audit,
        opportunities=opps,
        has_email=True,
        website_reachable=True,
        website_official_verified=True,
        has_source_provenance=True
    )
    assert score_res["opportunity_score"] >= 60
    assert score_res["data_confidence_score"] >= 70

def test_freshness_tracker():
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    assert freshness_tracker.calculate_state(now) == "FRESH"
    assert freshness_tracker.calculate_state(now - datetime.timedelta(days=15)) == "RECENT"
    assert freshness_tracker.calculate_state(now - datetime.timedelta(days=45)) == "STALE"
    assert freshness_tracker.calculate_state(None) == "NEEDS_RECHECK"

def test_email_verifier():
    res = asyncio.run(email_verifier.verify("invalid-format"))
    assert res["status"] == "INVALID"
    
    res_role = asyncio.run(email_verifier.verify("info@gmail.com"))
    assert res_role["status"] in ["ROLE_BASED", "VALID", "DOMAIN_MAIL_ENABLED"]
    assert res_role["mx_valid"] is True

def test_email_template_rendering():
    success, rendered, err = email_sender.render_template(
        "Hi {{first_name}}, we noticed {{website_issue}} on {{website}}.",
        {"first_name": "Rajesh", "website_issue": "slow mobile speed", "website": "example.com"}
    )
    assert success is True
    assert rendered == "Hi Rajesh, we noticed slow mobile speed on example.com."
