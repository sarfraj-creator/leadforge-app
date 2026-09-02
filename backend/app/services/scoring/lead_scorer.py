from typing import List, Dict, Any, Optional
from backend.app.services.audit.engine import AuditResult
from backend.app.services.scoring.opportunity_engine import OpportunityMatch

class LeadScoringEngine:
    """
    Decoupled 5-Part Lead Scoring Engine:
    1. Data Confidence Score (0-100)
    2. Business Fit Score (0-100)
    3. Opportunity Score (0-100) — evaluated strictly when audit.status == 'AUDIT_COMPLETE'
    4. Buying Intent Score (0-100 or UNKNOWN) — never fabricated from website defects
    5. Contactability Score (0-100) — evaluated on verified channels
    -> Overall Priority Score (0-100: HOT / HIGH / MEDIUM / LOW)
    -> Pipeline Stage: DISCOVERED | VERIFIED | AUDITED | OPPORTUNITY | CONTACTABLE | QUALIFIED | SALES_READY
    """

    def calculate_score(
        self,
        has_website: bool,
        audit: Optional[AuditResult] = None,
        opportunities: Optional[List[OpportunityMatch]] = None,
        has_email: bool = False,
        email_status: Optional[str] = None,
        has_phone: bool = False,
        has_form: bool = False,
        is_fresh: bool = True,
        website_reachable: bool = False,
        website_official_verified: bool = False,
        intent_info: Optional[Dict[str, Any]] = None,
        business_fit_ratio: float = 1.0,
        has_source_provenance: bool = True
    ) -> Dict[str, Any]:
        rules = []
        explanation_points = []

        # =====================================================================
        # 1. Data Confidence Score (0-100)
        # =====================================================================
        data_conf_points = 0
        if has_source_provenance:
            data_conf_points += 30
            rules.append({"dimension": "data_confidence", "rule": "Authoritative Source Provenance", "points": +30, "evidence": "Verified origin identifier & source URL recorded"})

        if website_reachable and website_official_verified:
            data_conf_points += 45
            rules.append({"dimension": "data_confidence", "rule": "Official Website Reachable & Verified", "points": +45, "evidence": "Website responds 200 OK and brand matches page markup"})
        elif website_reachable:
            data_conf_points += 20
            rules.append({"dimension": "data_confidence", "rule": "Website Reachable (Unmatched Brand)", "points": +20, "evidence": "Website reachable but brand token confirmation unverified"})
        elif has_website:
            data_conf_points += 5
            rules.append({"dimension": "data_confidence", "rule": "Website URL Discovered (Unreachable)", "points": +5, "evidence": "Discovered URL failed live connectivity probe"})

        if is_fresh:
            data_conf_points += 25
            rules.append({"dimension": "data_confidence", "rule": "Real-Time Fresh Discovered Record", "points": +25, "evidence": "Discovered within past 7 days"})
        else:
            data_conf_points += 10

        data_confidence_score = min(100, max(0, data_conf_points))

        # =====================================================================
        # 2. Business Fit Score (0-100)
        # =====================================================================
        fit_points = int(min(100, max(30, business_fit_ratio * 100)))
        business_fit_score = fit_points
        rules.append({"dimension": "business_fit", "rule": "Industry & Profile Alignment", "points": fit_points, "evidence": f"Target industry criteria fit ratio {business_fit_ratio:.2f}"})

        # =====================================================================
        # 3. Opportunity Score (0-100)
        # Evaluated ONLY when audit is complete. If unreachable/incomplete: 0
        # =====================================================================
        opp_score = 0
        is_audit_complete = bool(audit and audit.status == "AUDIT_COMPLETE")

        if is_audit_complete and audit:
            # Base exploration points for active audited site
            opp_score = 20
            
            if audit.mobile_score < 60:
                opp_score += 25
                rules.append({"dimension": "opportunity", "rule": "Mobile Layout Deficiencies", "points": +25, "evidence": f"Mobile score {audit.mobile_score}/100 — viewport or touch targets deficient"})
                explanation_points.append(f"Mobile layout optimization needed (measured mobile score: {audit.mobile_score}/100).")

            if audit.performance_score < 55:
                opp_score += 20
                rules.append({"dimension": "opportunity", "rule": "Slow Server Latency / Heavy Payload", "points": +20, "evidence": f"Performance score {audit.performance_score}/100"})
                explanation_points.append(f"Performance speed optimization needed (measured score: {audit.performance_score}/100).")

            if audit.seo_score < 65:
                opp_score += 15
                rules.append({"dimension": "opportunity", "rule": "SEO Metadata Gaps", "points": +15, "evidence": f"SEO score {audit.seo_score}/100 — missing title/meta/H1"})
                explanation_points.append(f"On-page SEO structure deficient (measured score: {audit.seo_score}/100).")

            if audit.conversion_score < 60:
                opp_score += 20
                rules.append({"dimension": "opportunity", "rule": "Missing Lead Capture / CTA Funnel", "points": +20, "evidence": f"Conversion score {audit.conversion_score}/100 — no prominent action buttons"})
                explanation_points.append("Inquiry conversion funnel deficient — lacking prominent call-to-action buttons.")

            if audit.security_score < 70:
                opp_score += 15
                rules.append({"dimension": "opportunity", "rule": "TLS / Security Vulnerabilities", "points": +15, "evidence": f"Security score {audit.security_score}/100 — SSL certificate or HSTS issue"})
                explanation_points.append("Security enhancement needed (TLS/SSL certificate issue detected).")

            if audit.overall_score >= 85:
                opp_score = max(15, opp_score - 35)
                rules.append({"dimension": "opportunity", "rule": "Modern High-Performance Site", "points": -35, "evidence": f"Overall health score {audit.overall_score}/100"})
                explanation_points.append("Website is already well-optimized and modern; low urgency for digital services.")
        elif not has_website:
            # Genuine new business without any website
            opp_score = 90
            rules.append({"dimension": "opportunity", "rule": "No Digital Presence", "points": +90, "evidence": "No website registered — prime candidate for new website build"})
            explanation_points.append("No active website exists — strong opportunity for new website design & development.")
        else:
            # Audit incomplete or unreachable: do NOT fabricate opportunity score
            opp_score = 0
            explanation_points.append("Website audit incomplete or unreachable. Opportunity score withheld pending successful connectivity probe.")

        opportunity_score = min(100, max(0, opp_score))

        # =====================================================================
        # 4. Buying Intent Score (0-100 or UNKNOWN)
        # Never fabricated from website defects
        # =====================================================================
        intent_info = intent_info or {}
        intent_status = intent_info.get("buying_intent", "UNKNOWN")
        intent_score = intent_info.get("intent_score", 0) if intent_status != "UNKNOWN" else 0
        
        if intent_status != "UNKNOWN" and intent_score > 0:
            rules.append({"dimension": "intent", "rule": "Observable Buying Intent Signal", "points": intent_score, "evidence": intent_info.get("explanation", "Observable commercial signal")})
            explanation_points.append(f"Commercial intent detected: {intent_info.get('explanation', '')}")
        else:
            intent_status = "UNKNOWN"
            intent_score = 0

        # =====================================================================
        # 5. Contactability Score (0-100)
        # =====================================================================
        contact_points = 0
        if has_email:
            if email_status == "MAILBOX_VERIFIED":
                contact_points += 60
                rules.append({"dimension": "contactability", "rule": "Direct Mailbox Handshake Verified", "points": +60, "evidence": "SMTP probe confirmed mailbox delivery"})
            elif email_status == "DOMAIN_MAIL_ENABLED":
                contact_points += 45
                rules.append({"dimension": "contactability", "rule": "Domain Mail Enabled (DNS MX Verified)", "points": +45, "evidence": "Domain MX records confirmed"})
            else:
                contact_points += 25
                rules.append({"dimension": "contactability", "rule": "Public Contact Email Discovered", "points": +25, "evidence": "Public email extracted from website markup"})

        if has_phone:
            contact_points += 30
            rules.append({"dimension": "contactability", "rule": "Public Business Telephone Available", "points": +30, "evidence": "Direct phone number extracted and validated"})

        if has_form:
            contact_points += 15
            rules.append({"dimension": "contactability", "rule": "Interactive Web Contact / Inquiry Form", "points": +15, "evidence": "Live form submission endpoint detected on website"})

        contactability_score = min(100, max(0, contact_points))

        # =====================================================================
        # 6. Overall Weighted Priority Score
        # Weights: Opportunity (40%), Contactability (25%), Data Confidence (20%), Business Fit (15%)
        # =====================================================================
        weighted_total = (
            opportunity_score * 0.40
            + contactability_score * 0.25
            + data_confidence_score * 0.20
            + business_fit_score * 0.15
        )
        total_score = int(min(100, max(0, round(weighted_total))))

        # =====================================================================
        # 7. Pipeline Lifecycle Stage Determination
        # DISCOVERED -> VERIFIED -> AUDITED -> OPPORTUNITY -> CONTACTABLE -> QUALIFIED -> SALES_READY
        # =====================================================================
        is_verified = (has_source_provenance and (not has_website or (website_reachable and website_official_verified)))
        has_strong_opportunity = (opportunity_score >= 60)
        is_contactable = (contactability_score >= 50)
        is_qualified = (
            is_verified
            and (is_audit_complete or not has_website)
            and has_strong_opportunity
            and (data_confidence_score >= 70)
        )
        # SALES_READY strictly requires QUALIFIED + contactability >= 50 + human review approval (APPROVED)
        is_sales_ready = False

        if is_qualified:
            pipeline_stage = "QUALIFIED"
        elif is_contactable and (has_strong_opportunity or is_audit_complete):
            pipeline_stage = "CONTACTABLE"
        elif has_strong_opportunity:
            pipeline_stage = "OPPORTUNITY"
        elif is_audit_complete:
            pipeline_stage = "AUDITED"
        elif is_verified:
            pipeline_stage = "VERIFIED"
        else:
            pipeline_stage = "DISCOVERED"

        # Priority categorization
        if total_score >= 80 and is_qualified:
            category = "HOT"
        elif total_score >= 65 and is_qualified:
            category = "HIGH"
        elif total_score >= 50:
            category = "MEDIUM"
        else:
            category = "LOW"

        explanation = "\n".join([f"• {pt}" for pt in explanation_points]) if explanation_points else "• Standard baseline profile."

        return {
            "total_score": total_score,
            "category": category,
            "pipeline_stage": pipeline_stage,
            "is_qualified": is_qualified,
            "is_sales_ready": is_sales_ready,
            "data_confidence_score": data_confidence_score,
            "business_fit_score": business_fit_score,
            "opportunity_score": opportunity_score,
            "intent_score": intent_score,
            "buying_intent": intent_status,
            "contactability_score": contactability_score,
            "rules_applied": rules,
            "explanation": explanation
        }

lead_scorer = LeadScoringEngine()
