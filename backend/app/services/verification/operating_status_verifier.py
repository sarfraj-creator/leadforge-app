import re
import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

class OperatingStatusVerifier:
    """
    Determines verified operational status of a discovered business.
    Statuses: ACTIVE, PROBABLY_ACTIVE, UNKNOWN, CLOSED, PERMANENTLY_CLOSED.
    Never assumes ACTIVE without concrete, observable evidence.
    """

    CLOSED_KEYWORDS = [
        "permanently closed", "closed permanently", "out of business",
        "ceased operations", "this location is closed", "shut down",
        "has closed down", "no longer operating", "liquidation", "bankruptcy"
    ]

    ACTIVE_SIGNALS = [
        "book now", "schedule appointment", "order online", "reserve a table",
        "opening hours", "open today", "hours of operation", "mon-fri", "monday to friday",
        "business hours", "call us today", "contact our team", "we are open"
    ]

    @classmethod
    def determine_operating_status(
        cls,
        business_name: str,
        website_reachable: bool,
        http_status: Optional[int],
        html_content: Optional[str] = None,
        phone_valid: bool = False,
        observed_at: Optional[datetime.datetime] = None,
        source_name: Optional[str] = None,
        opening_hours: Optional[str] = None,
        raw_source_tags: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        evidence: List[Dict[str, Any]] = []
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        obs_timestamp = observed_at.isoformat() if observed_at else now_utc.isoformat()

        # Check for explicit HTTP 410 Gone or permanent error
        if http_status == 410:
            evidence.append({
                "signal": "HTTP_410_GONE",
                "detail": "Website returned HTTP 410 Gone (Permanently Removed)",
                "observed_at": obs_timestamp
            })
            return {
                "status": "PERMANENTLY_CLOSED",
                "confidence": 0.95,
                "evidence": evidence
            }

        # Check raw OSM/Source tags for disused/closed flags
        tags = raw_source_tags or {}
        if tags.get("disused") == "yes" or tags.get("abandoned") == "yes" or "disused:" in str(tags):
            evidence.append({
                "signal": "SOURCE_TAG_DISUSED",
                "detail": "Discovered source record explicitly tagged as disused or abandoned",
                "observed_at": obs_timestamp
            })
            return {
                "status": "PERMANENTLY_CLOSED",
                "confidence": 0.90,
                "evidence": evidence
            }

        # Analyze Website Content if reachable
        if website_reachable and html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            body_text = soup.get_text(separator=" ", strip=True).lower()

            # 1. Closed keyword detection
            for kw in cls.CLOSED_KEYWORDS:
                if kw in body_text:
                    evidence.append({
                        "signal": "WEBSITE_CLOSED_TEXT",
                        "detail": f"Observed notice on website: '{kw}'",
                        "observed_at": obs_timestamp
                    })
                    return {
                        "status": "PERMANENTLY_CLOSED",
                        "confidence": 0.85,
                        "evidence": evidence
                    }

            # 2. Positive Active Evidence
            current_year = str(now_utc.year)
            prev_year = str(now_utc.year - 1)

            # Footer / Copyright freshness
            footer = soup.find("footer")
            footer_text = footer.get_text() if footer else body_text[-2000:]
            if current_year in footer_text or prev_year in footer_text:
                evidence.append({
                    "signal": "RECENT_COPYRIGHT",
                    "detail": f"Active website copyright for {current_year}/{prev_year}",
                    "observed_at": obs_timestamp
                })

            # Interactive booking / commerce / hours
            found_active_kws = [kw for kw in cls.ACTIVE_SIGNALS if kw in body_text]
            if found_active_kws:
                evidence.append({
                    "signal": "ACTIVE_OPERATING_SIGNALS",
                    "detail": f"Observed live operational elements: {', '.join(found_active_kws[:3])}",
                    "observed_at": obs_timestamp
                })

            # Structured Data (JSON-LD opening hours or restaurant / localbusiness)
            scripts = soup.find_all("script", type="application/ld+json")
            for s in scripts:
                if s.string and any(k in s.string.lower() for k in ["openinghours", "openinghoursspecification", "localbusiness", "restaurant", "store"]):
                    evidence.append({
                        "signal": "STRUCTURED_DATA_BUSINESS_HOURS",
                        "detail": "Verified schema.org LocalBusiness / OpeningHours specification",
                        "observed_at": obs_timestamp
                    })
                    break

        # Check explicit opening hours tag
        if opening_hours and len(opening_hours.strip()) > 1:
            evidence.append({
                "signal": "PUBLIC_OPENING_HOURS",
                "detail": f"Public opening hours registered: '{opening_hours}'",
                "observed_at": obs_timestamp
            })

        # Check verified phone
        if phone_valid:
            evidence.append({
                "signal": "VERIFIED_PHONE_LINE",
                "detail": "Valid telecom routing telephone number confirmed",
                "observed_at": obs_timestamp
            })

        # Determine Final Status
        if len(evidence) >= 3:
            return {
                "status": "ACTIVE",
                "confidence": 0.95,
                "evidence": evidence
            }
        elif len(evidence) >= 1:
            return {
                "status": "PROBABLY_ACTIVE",
                "confidence": 0.75,
                "evidence": evidence
            }
        elif website_reachable:
            evidence.append({
                "signal": "WEBSITE_RESPONDING",
                "detail": f"Website responding with HTTP {http_status or 200}",
                "observed_at": obs_timestamp
            })
            return {
                "status": "PROBABLY_ACTIVE",
                "confidence": 0.60,
                "evidence": evidence
            }
        else:
            return {
                "status": "UNKNOWN",
                "confidence": 0.20,
                "evidence": []
            }

operating_status_verifier = OperatingStatusVerifier()
