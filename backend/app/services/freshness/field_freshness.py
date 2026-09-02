import datetime
from typing import Optional, Dict, Any

class FieldFreshnessEngine:
    """
    Field-Level Freshness Tracking:
    0-7 days = FRESH
    8-30 days = RECENT
    31-90 days = STALE
    90+ days = EXPIRED
    None = UNKNOWN
    """

    @staticmethod
    def calculate_freshness(timestamp: Optional[datetime.datetime]) -> str:
        if not timestamp:
            return "UNKNOWN"
            
        now = datetime.datetime.now(datetime.timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
            
        age_days = (now - timestamp).total_seconds() / 86400.0

        if age_days <= 7:
            return "FRESH"
        elif age_days <= 30:
            return "RECENT"
        elif age_days <= 90:
            return "STALE"
        else:
            return "EXPIRED"

    @classmethod
    def evaluate_lead_freshness(
        cls,
        company_observed_at: Optional[datetime.datetime],
        website_observed_at: Optional[datetime.datetime] = None,
        contact_observed_at: Optional[datetime.datetime] = None,
        audit_observed_at: Optional[datetime.datetime] = None
    ) -> Dict[str, str]:
        return {
            "company_freshness": cls.calculate_freshness(company_observed_at),
            "website_freshness": cls.calculate_freshness(website_observed_at),
            "contact_freshness": cls.calculate_freshness(contact_observed_at),
            "audit_freshness": cls.calculate_freshness(audit_observed_at),
            "overall_freshness": cls.calculate_freshness(company_observed_at)
        }

field_freshness_engine = FieldFreshnessEngine()
