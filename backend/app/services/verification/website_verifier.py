import re
import urllib.parse
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List, Tuple
from backend.app.core.ssrf import is_safe_url

PARKED_DOMAIN_SIGNALS = [
    "domain is for sale", "buy this domain", "parked free", "hugedomains",
    "godaddy parked", "dan.com", "sedo.com", "namecheap parked",
    "under construction", "this domain is registered", "renewal pending"
]

class WebsiteVerifier:
    """
    Multi-Signal Official Website Verification Engine:
    Distinguishes:
    - URL_DISCOVERED
    - REACHABLE
    - OFFICIAL_MATCH
    - OFFICIAL_VERIFIED
    - UNVERIFIED
    - PARKED
    - BROKEN
    """

    @staticmethod
    def verify_website(
        business_name: str,
        website_url: Optional[str],
        html_content: Optional[str] = None,
        status_code: Optional[int] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not website_url or not website_url.strip():
            return {
                "website_verification_status": "UNVERIFIED",
                "confidence": "UNVERIFIED",
                "verification_score": 0,
                "score": 0,
                "is_verified": False,
                "verification_reasons": ["No website URL discovered from source."],
                "signals": ["No website provided"]
            }

        url = website_url.strip()
        if not url.startswith("http"):
            url = f"https://{url}"

        # 1. SSRF Safety Check
        if not is_safe_url(url):
            return {
                "website_verification_status": "BROKEN",
                "confidence": "UNVERIFIED",
                "verification_score": 0,
                "score": 0,
                "is_verified": False,
                "verification_reasons": ["SSRF safety check blocked private or disallowed destination."],
                "signals": ["SSRF blocked"]
            }

        if not html_content or status_code is None:
            return {
                "website_verification_status": "URL_DISCOVERED",
                "confidence": "UNVERIFIED",
                "verification_score": 10,
                "score": 10,
                "is_verified": False,
                "verification_reasons": ["Website discovered in public source but not yet reached."],
                "signals": ["Website not yet crawled"]
            }

        # 2. HTTP Status Check
        if status_code >= 400:
            return {
                "website_verification_status": "BROKEN",
                "confidence": "UNVERIFIED",
                "verification_score": 0,
                "score": 0,
                "is_verified": False,
                "verification_reasons": [f"HTTP error status: {status_code}"],
                "signals": [f"HTTP error status: {status_code}"]
            }

        reasons = []
        score = 30 # Base score for reachable site (200 OK)
        reasons.append(f"Reachable with HTTP {status_code}")

        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text().lower()
        title = (soup.title.string or "").lower() if soup.title else ""

        # 3. Check for Parked Domain / For Sale Page
        for parked_sig in PARKED_DOMAIN_SIGNALS:
            if parked_sig in text:
                return {
                    "website_verification_status": "PARKED",
                    "confidence": "LOW",
                    "verification_score": 5,
                    "score": 5,
                    "is_verified": False,
                    "verification_reasons": [f"Parked domain signal detected: '{parked_sig}'"],
                    "signals": [f"Parked domain signal detected: {parked_sig}"]
                }

        # 4. Brand Name Matching
        clean_name = re.sub(r"[^\w\s]", "", business_name).lower()
        name_words = [w for w in clean_name.split() if len(w) > 2]
        
        matches = 0
        if name_words:
            for w in name_words:
                if w in title or w in text:
                    matches += 1
            
            match_ratio = matches / len(name_words)
            if match_ratio >= 0.5:
                score += 35
                reasons.append(f"Brand keywords matched on page ({matches}/{len(name_words)})")
            elif match_ratio > 0:
                score += 15
                reasons.append(f"Partial brand keywords matched ({matches}/{len(name_words)})")

        # 5. Domain Token Matching
        parsed = urllib.parse.urlparse(url)
        domain_name = parsed.netloc.lower().replace("www.", "")
        if any(w in domain_name for w in name_words):
            score += 20
            reasons.append(f"Domain name '{domain_name}' matches business name tokens")

        # 6. Phone / Location Verification
        if phone:
            clean_phone = re.sub(r"\D", "", phone)
            if len(clean_phone) >= 7 and clean_phone[-7:] in re.sub(r"\D", "", text):
                score += 15
                reasons.append(f"Discovered phone {phone} confirmed on page")

        if city and city.lower() in text:
            score += 10
            reasons.append(f"Location city '{city}' confirmed on website")

        # Final Status
        if score >= 80:
            status = "OFFICIAL_VERIFIED"
            confidence = "HIGH"
            is_verified = True
        elif score >= 50:
            status = "OFFICIAL_MATCH"
            confidence = "MEDIUM"
            is_verified = True
        elif score >= 30:
            status = "REACHABLE"
            confidence = "LOW"
            is_verified = False
        else:
            status = "UNVERIFIED"
            confidence = "UNVERIFIED"
            is_verified = False

        return {
            "website_verification_status": status,
            "confidence": confidence,
            "verification_score": min(100, score),
            "score": min(100, score),
            "is_verified": is_verified,
            "verification_reasons": reasons,
            "signals": reasons
        }

website_verifier = WebsiteVerifier()
