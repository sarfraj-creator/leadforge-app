import re
import urllib.parse
from typing import Optional, Dict, Any

def normalize_domain(url_or_domain: Optional[str]) -> Optional[str]:
    """
    Normalizes a domain or URL:
    - strips protocol (http://, https://)
    - strips 'www.'
    - strips trailing slashes, paths, query parameters
    - lowercases
    """
    if not url_or_domain or not isinstance(url_or_domain, str):
        return None
        
    raw = url_or_domain.strip().lower()
    if not raw.startswith("http://") and not raw.startswith("https://"):
        raw = "http://" + raw
        
    try:
        parsed = urllib.parse.urlparse(raw)
        netloc = parsed.netloc or parsed.path
        # Remove port if default
        netloc = netloc.split(":")[0]
        # Remove www.
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc.strip().strip("/")
    except Exception:
        clean = re.sub(r"^(https?://)?(www\.)?", "", url_or_domain.strip().lower())
        clean = clean.split("/")[0].split("?")[0].split(":")[0]
        return clean.strip() if clean else None

def normalize_business_name(name: Optional[str]) -> Optional[str]:
    """
    Normalizes a company/business name:
    - removes corporate suffixes (Inc, LLC, Ltd, Pvt Ltd, Co)
    - strips special punctuation
    - trims whitespace and lowercases
    """
    if not name or not isinstance(name, str):
        return None
        
    clean = name.strip().lower()
    # Remove common legal suffixes
    clean = re.sub(r"\b(inc|incorporated|llc|ltd|limited|pvt|private|corp|corporation|gmbh|sa|co|company)\b", "", clean)
    # Remove non-alphanumeric except spaces
    clean = re.sub(r"[^\w\s]", "", clean)
    # Collapse multiple spaces
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean if clean else None

def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """
    Normalizes phone numbers:
    - extracts digits
    - standardizes country code or clean sequence
    """
    if not phone or not isinstance(phone, str):
        return None
        
    digits = re.sub(r"[^\d+]", "", phone.strip())
    if len(digits) < 6:
        return None
    return digits

def normalize_email(email: Optional[str]) -> Optional[str]:
    """
    Normalizes email:
    - trims
    - lowercases
    """
    if not email or not isinstance(email, str):
        return None
    clean = email.strip().lower()
    if "@" not in clean or "." not in clean.split("@")[-1]:
        return None
    return clean

def compute_dedup_hash(
    business_name: Optional[str],
    domain: Optional[str] = None,
    phone: Optional[str] = None,
    city: Optional[str] = None
) -> str:
    """
    Computes a deterministic entity resolution key for deduplication.
    Priority 1: Normalized domain (if present, unique for websites)
    Priority 2: Normalized name + normalized city / phone
    """
    norm_domain = normalize_domain(domain)
    if norm_domain:
        return f"domain:{norm_domain}"
        
    norm_name = normalize_business_name(business_name) or "unknown"
    norm_phone = normalize_phone(phone) or ""
    norm_city = (city or "").strip().lower()
    
    if norm_phone:
        return f"name_phone:{norm_name}_{norm_phone}"
    elif norm_city:
        return f"name_city:{norm_name}_{norm_city}"
    else:
        return f"name:{norm_name}"
