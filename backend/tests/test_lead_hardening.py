import pytest
from backend.app.services.audit.engine import audit_engine, AuditResult
from backend.app.services.crawler.safe_crawler import CrawlResult
from backend.app.services.scoring.lead_scorer import lead_scorer
from backend.app.services.contact.verifier import email_verifier

def test_unreachable_website_audit_incomplete():
    crawl = CrawlResult("https://definitely-offline-domain-12345.com")
    crawl.is_reachable = False
    crawl.error = "Connection refused"
    
    audit = audit_engine.audit(crawl)
    assert audit.status == "AUDIT_INCOMPLETE"
    assert audit.overall_score == 0
    assert "Website Unreachable / Audit Incomplete" in audit.issues[0]["title"]

def test_incomplete_audit_does_not_fabricate_opportunity_score():
    audit = AuditResult()
    audit.status = "AUDIT_INCOMPLETE"
    audit.overall_score = 0
    
    score_res = lead_scorer.calculate_score(
        has_website=True,
        audit=audit,
        opportunities=[],
        has_email=False,
        is_fresh=True,
        website_reachable=False,
        website_official_verified=False
    )
    
    # Opportunity score MUST be 0 when audit is incomplete
    assert score_res["opportunity_score"] == 0
    # Must NOT be qualified
    assert score_res["is_qualified"] is False
    assert score_res["is_sales_ready"] is False
    assert score_res["pipeline_stage"] in ["DISCOVERED", "VERIFIED"]

def test_evidence_based_qualification_and_sales_ready():
    # 1. Complete audit with real measured defect
    crawl = CrawlResult("https://real-test-business.com")
    crawl.is_reachable = True
    crawl.website_reachable = True
    crawl.website_official_verified = True
    crawl.load_time_ms = 4200 # slow
    crawl.page_size_bytes = 4000000
    crawl.raw_html = "<html><head><title>Real Business</title></head><body><h1>Real Business</h1><p>Welcome</p></body></html>"
    
    audit = audit_engine.audit(crawl)
    assert audit.status == "AUDIT_COMPLETE"
    
    # 2. Score with contact
    score_res = lead_scorer.calculate_score(
        has_website=True,
        audit=audit,
        has_email=True,
        email_status="DOMAIN_MAIL_ENABLED",
        has_phone=True,
        has_form=False,
        is_fresh=True,
        website_reachable=True,
        website_official_verified=True,
        has_source_provenance=True
    )
    
    assert score_res["opportunity_score"] >= 60
    assert score_res["data_confidence_score"] >= 70
    assert score_res["is_qualified"] is True
    assert score_res["is_sales_ready"] is False  # requires review_status == 'APPROVED'
    assert score_res["pipeline_stage"] == "QUALIFIED"
    assert score_res["buying_intent"] == "UNKNOWN" # Intent remains UNKNOWN without fabrication

@pytest.mark.anyio
async def test_email_verifier_domain_mail_enabled():
    res = await email_verifier.verify("info@google.com")
    assert res["syntax_valid"] is True
    assert res["domain_valid"] is True
    assert res["mx_valid"] is True
    assert res["mailbox_verified"] is False # strictly False without SMTP handshake
    assert res["status"] == "DOMAIN_MAIL_ENABLED"
