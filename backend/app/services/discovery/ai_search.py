import httpx
import re
import json
import urllib.parse
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from backend.app.services.discovery.base import LeadSourceAdapter, DiscoveredRecord
from backend.app.services.ai.factory import ai_factory
from backend.app.core.config import settings
from backend.app.core.deduplication import normalize_domain, normalize_phone, normalize_email

logger = logging.getLogger("leadforge.discovery.ai_search")

DISALLOWED_DOMAINS = [
    "yelp.com", "yellowpages.com", "tripadvisor.com", "clutch.co", "upcity.com",
    "facebook.com", "twitter.com", "x.com", "instagram.com", "youtube.com",
    "wikipedia.org", "mapquest.com", "bbb.org", "glassdoor.com", "indeed.com",
    "linkedin.com", "google.com", "bing.com", "duckduckgo.com", "yahoo.com"
]

NON_PERSON_WORDS = [
    "contact", "about", "team", "staff", "company", "service", "support",
    "sales", "inquiry", "info", "admin", "office", "help", "department",
    "reception", "desk", "lead", "group", "ltd", "inc", "llc", "corp",
    "privacy", "terms", "policy", "menu", "booking", "reservation", "page",
    "official", "website", "best", "top", "reviews", "locations"
]

class AISearchAdapter(LeadSourceAdapter):
    """
    Enterprise AI Web Search & Executive Discovery Agent.
    Powered by Perplexity AI (Sonar Live Grounding) and Google Gemini (Search Grounding)
    with resilient public web fallback.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(source_name="AISearch", config=config)

    async def health_check(self) -> Dict[str, Any]:
        grounded_ai = ai_factory.get_search_grounded_provider()
        if grounded_ai:
            health = await grounded_ai.health_check()
            return {
                "status": health.get("status", "CONNECTED"),
                "provider": f"Real-Time Grounded AI ({grounded_ai.__class__.__name__.replace('Provider', '')})",
                "model": getattr(grounded_ai, "model", "Live Model"),
                "real_time_web": True,
                "rate_limit_per_min": 60,
                "mode": "Active Real-Time Web Grounded Intelligence"
            }
        else:
            return {
                "status": "AVAILABLE",
                "provider": "AI Web Discovery (Public Engine Fallback)",
                "model": "Multi-Engine Web Heuristic",
                "real_time_web": True,
                "rate_limit_per_min": 25,
                "mode": "Configure PERPLEXITY_API_KEY or GEMINI_API_KEY in Settings for Premium Grounded Intelligence"
            }

    async def discover(
        self,
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit: int = 50
    ) -> List[DiscoveredRecord]:
        target_industry = (industry or query or "business").strip()
        is_worldwide = (location or "").strip().upper() in ["WORLDWIDE", "GLOBAL", "ALL", "ANY", "EARTH", ""]
        loc_str = "" if is_worldwide else location.strip()

        records: List[DiscoveredRecord] = []
        seen_domains = set()
        seen_names = set()

        # 1. Try Premium Real-Time Grounded AI Engine (Perplexity Sonar / Gemini Grounding)
        grounded_ai = ai_factory.get_search_grounded_provider()
        if grounded_ai and hasattr(grounded_ai, "search_grounded_leads"):
            try:
                ai_leads = await grounded_ai.search_grounded_leads(
                    query=query,
                    location=location,
                    industry=target_industry,
                    limit=limit
                )
                for item in ai_leads:
                    if len(records) >= limit:
                        break

                    b_name = (item.get("business_name") or "").strip()
                    website = (item.get("website") or "").strip() or None
                    if not b_name or len(b_name) < 2:
                        continue

                    # Validate domain
                    norm_dom = normalize_domain(website) if website else None
                    if norm_dom:
                        if any(dis in norm_dom for dis in DISALLOWED_DOMAINS):
                            website = None
                            norm_dom = None
                        elif norm_dom in seen_domains:
                            continue
                        else:
                            seen_domains.add(norm_dom)

                    # Validate Decision Maker & LinkedIn URL
                    dm_name = (item.get("decision_maker_name") or "").strip() or None
                    dm_role = (item.get("decision_maker_role") or "").strip() or "Executive / Owner"
                    dm_linkedin = (item.get("decision_maker_linkedin") or "").strip() or None

                    if dm_name:
                        # Validate that name is a real person name
                        clean_lower = dm_name.lower()
                        if any(w in clean_lower for w in NON_PERSON_WORDS) or len(dm_name.split()) < 2:
                            dm_name = None
                            dm_role = None
                            dm_linkedin = None

                    if dm_linkedin and "linkedin.com/in/" not in dm_linkedin.lower():
                        dm_linkedin = None

                    rec = DiscoveredRecord(
                        business_name=b_name,
                        source="AISearch",
                        source_record_id=f"ai_{abs(hash(b_name + (website or '')))}",
                        source_url=website or item.get("source_url"),
                        website=website,
                        phone=normalize_phone(item.get("phone")),
                        email=normalize_email(item.get("email")),
                        address=item.get("address"),
                        city=item.get("city") or loc_str or None,
                        state=item.get("state"),
                        country=item.get("country"),
                        industry=item.get("industry") or target_industry,
                        category=item.get("category") or target_industry,
                        description=item.get("description") or f"Verified {target_industry} lead discovered via Grounded AI Search.",
                        confidence=float(item.get("confidence", 0.95)),
                        raw_data={
                            "decision_maker_name": dm_name,
                            "decision_maker_role": dm_role,
                            "decision_maker_linkedin": dm_linkedin,
                            "ai_grounded": True,
                            "ai_provider": grounded_ai.__class__.__name__
                        }
                    )
                    self.normalize(rec)
                    if self.validate(rec):
                        records.append(rec)

                if len(records) >= max(5, limit // 2):
                    logger.info("AISearch discovered %d verified leads via Real-time AI Grounding", len(records))
                    return records
            except Exception as e:
                logger.error("Grounded AI lead discovery error: %s", e)

        # 2. Resilient Public Search Discovery Engine (Fallback Mode)
        # Uses multi-query web search dorks with strict entity validation
        search_dorks = [
            f'"{target_industry}" "{loc_str}" official website' if loc_str else f'"{target_industry}" top companies official website',
            f'{target_industry} {loc_str} (founder OR CEO OR owner) site:linkedin.com/in/' if loc_str else f'{target_industry} founder CEO linkedin.com/in/',
            f'best {target_industry} {loc_str} contact email phone' if loc_str else f'{target_industry} services official contact'
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

        raw_web_hits = []
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for dork in search_dorks:
                if len(raw_web_hits) >= limit * 2:
                    break
                encoded = urllib.parse.quote_plus(dork)
                url = f"https://html.duckduckgo.com/html/?q={encoded}"

                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")
                    results = soup.find_all("div", class_=re.compile(r"result|web-result"))

                    for item in results:
                        link_tag = item.find("a", class_=re.compile(r"result__url|result__snippet|result__title")) or item.find("a", href=True)
                        title_tag = item.find("a", class_=re.compile(r"result__title")) or item.find("h2") or item.find("a")
                        snippet_tag = item.find("a", class_=re.compile(r"result__snippet")) or item.find("div", class_=re.compile(r"snippet"))

                        if not title_tag:
                            continue

                        raw_title = title_tag.get_text(strip=True)
                        snippet_text = snippet_tag.get_text(strip=True) if snippet_tag else ""
                        raw_href = link_tag.get("href", "") if link_tag else ""

                        clean_href = raw_href
                        if "uddg=" in raw_href:
                            try:
                                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query).get("uddg", [None])[0]
                                if parsed:
                                    clean_href = parsed
                            except Exception:
                                pass

                        raw_web_hits.append({
                            "title": raw_title,
                            "snippet": snippet_text,
                            "url": clean_href
                        })
                except Exception as e:
                    logger.debug("Web search query fetch failed: %s", e)

        # Process raw web hits with strict entity verification
        for hit in raw_web_hits:
            if len(records) >= limit:
                break

            title = hit["title"]
            snippet = hit["snippet"]
            hit_url = hit["url"]

            # Parse Business Name from title
            clean_name = re.split(r"[-|–—:•·]|(?:\s+-\s+)|(?:\s+\|\s+)", title)[0].strip()
            if len(clean_name) < 3 or any(j in clean_name.lower() for j in ["the 10 best", "top 10", "yelp", "tripadvisor", "wikipedia", "directory", "clutch", "upcity"]):
                continue

            # Check if hit is a LinkedIn profile
            decision_maker_name = None
            decision_maker_role = None
            linkedin_url = None

            if "linkedin.com/in/" in hit_url:
                linkedin_url = hit_url
                parts = [p.strip() for p in re.split(r"[-|–—]", title) if p.strip()]
                if len(parts) >= 2:
                    cand_name = parts[0]
                    cand_role = parts[1]
                    if len(cand_name.split()) >= 2 and not any(w in cand_name.lower() for w in NON_PERSON_WORDS):
                        decision_maker_name = cand_name
                        decision_maker_role = cand_role
                    if len(parts) >= 3 and not any(j in parts[2].lower() for j in ["linkedin", "profile"]):
                        clean_name = parts[2]

            website = None
            if hit_url and "linkedin.com" not in hit_url:
                website = hit_url

            norm_dom = normalize_domain(website) if website else None
            if norm_dom:
                if any(dis in norm_dom for dis in DISALLOWED_DOMAINS) or norm_dom in seen_domains:
                    continue
                seen_domains.add(norm_dom)

            email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}', snippet)
            phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', snippet)

            email = email_match.group(0).lower() if email_match else None
            phone = phone_match.group(0) if phone_match else None

            rec = DiscoveredRecord(
                business_name=clean_name,
                source="AISearch",
                source_record_id=f"ai_{abs(hash(clean_name + (website or '')))}",
                source_url=hit_url,
                website=website,
                phone=phone,
                email=email,
                address=f"{clean_name}, {loc_str}" if loc_str else None,
                city=loc_str or None,
                industry=target_industry,
                category=target_industry,
                description=snippet[:220] if snippet else f"Discovered {target_industry} lead",
                confidence=0.88,
                raw_data={
                    "snippet": snippet,
                    "decision_maker_name": decision_maker_name,
                    "decision_maker_role": decision_maker_role,
                    "decision_maker_linkedin": linkedin_url,
                    "ai_grounded": False
                }
            )
            self.normalize(rec)
            if self.validate(rec):
                records.append(rec)

        return records
