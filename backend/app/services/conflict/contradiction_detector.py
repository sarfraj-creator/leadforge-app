import re
from typing import Dict, Any, List, Optional
from backend.app.core.deduplication import normalize_phone, normalize_business_name

class ContradictionDetector:
    """
    Cross-Source Contradiction Detection Engine:
    Compares values across multiple public sources (e.g. OpenStreetMap vs Official Website Crawl vs Registries).
    Preserves all evidence and flags conflicts without silently overwriting.
    """

    @staticmethod
    def detect_conflicts(
        company_name_source: str,
        company_name_observed: Optional[str],
        phone_source: Optional[str],
        phone_observed: Optional[str],
        website_source: Optional[str],
        website_observed: Optional[str],
        city_source: Optional[str],
        city_observed: Optional[str]
    ) -> Dict[str, Any]:
        conflicts = []

        # 1. Phone Conflict (Normalized comparison)
        if phone_source and phone_observed:
            norm_s = normalize_phone(phone_source)
            norm_o = normalize_phone(phone_observed)
            if norm_s and norm_o and norm_s[-7:] != norm_o[-7:]:
                conflicts.append({
                    "field": "phone",
                    "source_a": "Public Source Record",
                    "value_a": phone_source,
                    "source_b": "Official Website Crawl",
                    "value_b": phone_observed,
                    "resolution": "SHOW_BOTH_SOURCES"
                })

        # 2. City / Location Conflict
        if city_source and city_observed:
            if city_source.strip().lower() != city_observed.strip().lower():
                conflicts.append({
                    "field": "city",
                    "source_a": "Public Source Record",
                    "value_a": city_source,
                    "source_b": "Official Website Crawl",
                    "value_b": city_observed,
                    "resolution": "SHOW_BOTH_SOURCES"
                })

        # 3. Company Name Major Conflict
        if company_name_source and company_name_observed:
            norm_s = normalize_business_name(company_name_source)
            norm_o = normalize_business_name(company_name_observed)
            # If no common tokens
            tokens_s = set(re.split(r"\W+", norm_s))
            tokens_o = set(re.split(r"\W+", norm_o))
            if not tokens_s.intersection(tokens_o) and len(tokens_s) > 0 and len(tokens_o) > 0:
                conflicts.append({
                    "field": "company_name",
                    "source_a": "Public Source Record",
                    "value_a": company_name_source,
                    "source_b": "Official Website Header",
                    "value_b": company_name_observed,
                    "resolution": "SHOW_BOTH_SOURCES"
                })

        return {
            "has_conflicts": len(conflicts) > 0,
            "conflict_count": len(conflicts),
            "conflicts": conflicts
        }

contradiction_detector = ContradictionDetector()
