import json
from typing import Dict, Any, Optional

class DataQualityScorer:
    """
    Computes a transparent 0-100 Data Quality Score based on 6 verifiable factors:
    1. Source Reliability (30 pts)
    2. Business Identity Verification (20 pts)
    3. Official Website Verification (20 pts)
    4. Contact Provenance & Phone/Email Verification (15 pts)
    5. Data Freshness (10 pts)
    6. Cross-Source Consistency (5 pts)
    """

    @staticmethod
    def calculate_data_quality(
        source_name: str,
        identity_status: str, # HIGH, MEDIUM, LOW, UNVERIFIED
        website_status: str,  # OFFICIAL_VERIFIED, OFFICIAL_MATCH, REACHABLE, UNVERIFIED, BROKEN
        email_status: Optional[str] = None, # DOMAIN_MAIL_ENABLED, MAILBOX_VERIFIED, SYNTAX_VALID_ONLY
        phone_status: Optional[str] = None, # VALID_E164, LOCAL_FORMAT, UNVERIFIED
        freshness_state: str = "FRESH",
        has_conflicts: bool = False
    ) -> Dict[str, Any]:
        breakdown = {}
        score = 0

        # 1. Source Reliability (Max 30)
        source_upper = (source_name or "").upper()
        if "OFFICIAL" in source_upper or "REGISTRY" in source_upper:
            source_pts = 30
        elif "OPENSTREETMAP" in source_upper:
            source_pts = 25
        elif "DIRECTORY" in source_upper:
            source_pts = 18
        else:
            source_pts = 12
        breakdown["source_reliability"] = {"points": source_pts, "max": 30, "detail": f"Source '{source_name}' reliability score"}
        score += source_pts

        # 2. Business Identity Verification (Max 20)
        if identity_status == "HIGH":
            identity_pts = 20
        elif identity_status == "MEDIUM":
            identity_pts = 14
        elif identity_status == "LOW":
            identity_pts = 7
        else:
            identity_pts = 0
        breakdown["identity_verification"] = {"points": identity_pts, "max": 20, "detail": f"Cross-match identity confidence: {identity_status}"}
        score += identity_pts

        # 3. Official Website Verification (Max 20)
        if website_status == "OFFICIAL_VERIFIED":
            web_pts = 20
        elif website_status == "OFFICIAL_MATCH":
            web_pts = 15
        elif website_status == "REACHABLE":
            web_pts = 8
        else:
            web_pts = 0
        breakdown["website_verification"] = {"points": web_pts, "max": 20, "detail": f"Website verification level: {website_status}"}
        score += web_pts

        # 4. Contact Provenance & Email/Phone (Max 15)
        contact_pts = 0
        if email_status in ["DOMAIN_MAIL_ENABLED", "MAILBOX_VERIFIED"]:
            contact_pts += 10
        elif email_status == "SYNTAX_VALID_ONLY":
            contact_pts += 5

        if phone_status == "VALID_E164":
            contact_pts += 5
        elif phone_status == "LOCAL_FORMAT":
            contact_pts += 3
        contact_pts = min(15, contact_pts)
        breakdown["contact_provenance"] = {"points": contact_pts, "max": 15, "detail": f"Email: {email_status or 'None'}, Phone: {phone_status or 'None'}"}
        score += contact_pts

        # 5. Data Freshness (Max 10)
        if freshness_state == "FRESH":
            fresh_pts = 10
        elif freshness_state == "RECENT":
            fresh_pts = 7
        elif freshness_state == "STALE":
            fresh_pts = 3
        else:
            fresh_pts = 0
        breakdown["freshness"] = {"points": fresh_pts, "max": 10, "detail": f"Record observation state: {freshness_state}"}
        score += fresh_pts

        # 6. Cross-Source Consistency (Max 5)
        consistency_pts = 0 if has_conflicts else 5
        breakdown["consistency"] = {"points": consistency_pts, "max": 5, "detail": "Conflict detected across public sources" if has_conflicts else "No contradictions found"}
        score += consistency_pts

        total_score = min(100, max(0, score))
        return {
            "total_score": total_score,
            "breakdown": breakdown
        }

data_quality_scorer = DataQualityScorer()
