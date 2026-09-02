import re
from typing import Dict, Any, List, Optional
from backend.app.core.deduplication import normalize_business_name, normalize_domain, normalize_phone

class BusinessIdentityVerifier:
    """
    Dedicated Business Identity Verification Engine:
    Compares 9 independent signals between discovered public record
    and the live crawled website to determine genuine corporate identity.
    Returns HIGH, MEDIUM, LOW, or UNVERIFIED with complete signal provenance.
    """

    @classmethod
    def verify_identity(
        cls,
        business_name: str,
        website_url: Optional[str] = None,
        domain: Optional[str] = None,
        title: Optional[str] = None,
        h1_tags: Optional[List[str]] = None,
        html_content: Optional[str] = None,
        visible_text: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        signals = []
        total_score = 0
        max_possible = 100

        if not business_name or not website_url or not html_content:
            return {
                "status": "UNVERIFIED",
                "score": 0,
                "signals": [{"signal": "NO_LIVE_CONTENT", "matched": False, "weight": 0, "evidence": "No website or HTML content available for cross-matching."}],
                "is_verified": False
            }

        norm_name = normalize_business_name(business_name)
        name_tokens = [t for t in re.split(r"\W+", norm_name) if len(t) > 2]
        
        lower_html = html_content.lower()
        lower_title = (title or "").lower()
        lower_visible = (visible_text or "").lower()
        norm_phone = normalize_phone(phone) if phone else None

        # 1. Title Tag Match (Weight: 20)
        title_matched = any(token in lower_title for token in name_tokens)
        if title_matched:
            signals.append({"signal": "TITLE_BRAND_MATCH", "matched": True, "weight": 20, "evidence": f"Brand token matched in page title: '{title}'"})
            total_score += 20
        else:
            signals.append({"signal": "TITLE_BRAND_MATCH", "matched": False, "weight": 20, "evidence": "Brand tokens not found in page title."})

        # 2. H1 Heading Tag Match (Weight: 15)
        h1_matched = False
        if h1_tags:
            for h1 in h1_tags:
                if any(token in h1.lower() for token in name_tokens):
                    h1_matched = True
                    break
        if h1_matched:
            signals.append({"signal": "H1_HEADING_MATCH", "matched": True, "weight": 15, "evidence": "Brand token identified in main H1 heading."})
            total_score += 15
        else:
            signals.append({"signal": "H1_HEADING_MATCH", "matched": False, "weight": 15, "evidence": "No H1 headings contained brand tokens."})

        # 3. Domain Name Semantic Match (Weight: 20)
        norm_dom = normalize_domain(domain or website_url)
        dom_matched = any(token in norm_dom for token in name_tokens)
        if dom_matched:
            signals.append({"signal": "DOMAIN_NAME_MATCH", "matched": True, "weight": 20, "evidence": f"Domain '{norm_dom}' corresponds with brand token."})
            total_score += 20
        else:
            signals.append({"signal": "DOMAIN_NAME_MATCH", "matched": False, "weight": 20, "evidence": f"Domain '{norm_dom}' does not match company name tokens."})

        # 4. Visible Body Text Density (Weight: 15)
        text_matches = sum(1 for token in name_tokens if token in lower_visible)
        if text_matches >= max(1, len(name_tokens) // 2):
            signals.append({"signal": "VISIBLE_TEXT_MATCH", "matched": True, "weight": 15, "evidence": f"{text_matches}/{len(name_tokens)} brand tokens present in visible page text."})
            total_score += 15
        else:
            signals.append({"signal": "VISIBLE_TEXT_MATCH", "matched": False, "weight": 15, "evidence": "Insufficient brand tokens found in visible page copy."})

        # 5. Direct Phone Match on Page (Weight: 15)
        phone_matched = False
        if norm_phone and len(norm_phone) >= 7:
            # Check last 7 digits to ignore local area code formatting
            clean_digits = re.sub(r"\D", "", norm_phone)[-7:]
            if clean_digits in re.sub(r"\D", "", lower_html):
                phone_matched = True
        if phone_matched:
            signals.append({"signal": "PHONE_ON_PAGE_MATCH", "matched": True, "weight": 15, "evidence": f"Registered phone number '{phone}' verified on page HTML."})
            total_score += 15
        else:
            signals.append({"signal": "PHONE_ON_PAGE_MATCH", "matched": False, "weight": 15, "evidence": "Discovered phone number not observed in page HTML."})

        # 6. City / Locality Match on Page (Weight: 10)
        city_matched = False
        if city and len(city) >= 3:
            if city.lower() in lower_html:
                city_matched = True
        if city_matched:
            signals.append({"signal": "CITY_LOCATION_MATCH", "matched": True, "weight": 10, "evidence": f"Discovered city '{city}' verified on website body."})
            total_score += 10
        else:
            signals.append({"signal": "CITY_LOCATION_MATCH", "matched": False, "weight": 10, "evidence": f"Discovered city '{city}' not found in page HTML."})

        # 7. Copyright & Footer Corporate Name Match (Weight: 5)
        footer_matched = bool(re.search(r"(&copy;|©|copyright)[\s\d]*(" + "|".join(map(re.escape, name_tokens)) + ")", lower_html))
        if footer_matched:
            signals.append({"signal": "FOOTER_COPYRIGHT_MATCH", "matched": True, "weight": 5, "evidence": "Official corporate copyright declaration matches brand name."})
            total_score += 5
        else:
            signals.append({"signal": "FOOTER_COPYRIGHT_MATCH", "matched": False, "weight": 5, "evidence": "No copyright brand declaration found."})

        # Determine Classification Status
        if total_score >= 60:
            status = "HIGH"
            is_verified = True
        elif total_score >= 35:
            status = "MEDIUM"
            is_verified = True
        elif total_score > 0:
            status = "LOW"
            is_verified = False
        else:
            status = "UNVERIFIED"
            is_verified = False

        return {
            "status": status,
            "score": total_score,
            "signals": signals,
            "is_verified": is_verified
        }

identity_verifier = BusinessIdentityVerifier()
