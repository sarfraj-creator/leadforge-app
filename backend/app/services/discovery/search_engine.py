import httpx
import re
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from backend.app.services.discovery.base import LeadSourceAdapter, DiscoveredRecord

EXCLUDED_DOMAINS = {
    "wikipedia.org", "yelp.com", "tripadvisor.com", "facebook.com",
    "instagram.com", "linkedin.com", "twitter.com", "x.com",
    "youtube.com", "pinterest.com", "reddit.com", "amazon.com",
    "apple.com", "google.com", "bing.com", "yahoo.com", "yellowpages.com"
}

class SearchEngineAdapter(LeadSourceAdapter):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(source_name="SearchEngine", config=config)

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "CONNECTED",
            "provider": "Multi-Engine Search Discovery",
            "rate_limit_per_min": 20
        }

    async def discover(
        self,
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit: int = 50
    ) -> List[DiscoveredRecord]:
        results: List[DiscoveredRecord] = []
        is_worldwide = (location or "").strip().upper() in ["WORLDWIDE", "GLOBAL", "ALL", "ANY", "EARTH", ""]
        
        search_industry = (industry or query or "business").strip()
        
        if is_worldwide:
            search_terms = [
                f"{search_industry} official website contact",
                f"{search_industry} services company worldwide",
                f"top {search_industry} business",
            ]
        else:
            search_terms = [
                f"{search_industry} in {location} official website",
                f"best {search_industry} {location} contact",
            ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }

        for term in search_terms:
            if len(results) >= limit:
                break
            encoded_query = urllib.parse.quote_plus(term)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            try:
                async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        elements = soup.select(".result__body")
                        for el in elements:
                            title_el = el.select_one(".result__title .result__a")
                            snippet_el = el.select_one(".result__snippet")

                            if not title_el:
                                continue

                            raw_title = title_el.get_text(strip=True)
                            raw_snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                            target_url = title_el.get("href", "")

                            # DuckDuckGo redirect cleaner
                            if "uddg=" in target_url:
                                m = re.search(r"uddg=([^&]+)", target_url)
                                if m:
                                    target_url = urllib.parse.unquote(m.group(1))

                            parsed_url = urllib.parse.urlparse(target_url)
                            netloc = parsed_url.netloc.lower().replace("www.", "")
                            if any(d in netloc for d in EXCLUDED_DOMAINS):
                                continue

                            # Filter out directory aggregators and listicle titles
                            aggregator_patterns = [
                                r"^(the\s+)?\d+\s+best", r"^top\s+\d+", r"^find\s+the\s+best",
                                r"directory", r"best\s+\d+", r"^\d+\s+top", r"list\s+of",
                                r"reviews\s+for", r"rankings\s+of", r"near\s+me"
                            ]
                            if any(re.search(pat, raw_title.lower()) for pat in aggregator_patterns):
                                continue

                            # Extract clean business name
                            b_name = re.split(r"[-|:–—]", raw_title)[0].strip()
                            if len(b_name) < 2 or any(re.search(pat, b_name.lower()) for pat in aggregator_patterns):
                                continue

                            # Never infer phone from unstructured search snippets without verification
                            phone = None

                            record = DiscoveredRecord(
                                business_name=b_name,
                                source="SearchEngine",
                                source_record_id=f"se_{hash(target_url)}",
                                source_url=target_url,
                                website=target_url if target_url.startswith("http") else f"https://{netloc}",
                                phone=phone,
                                city=location if not is_worldwide else None,
                                industry=search_industry.title(),
                                description=raw_snippet,
                                confidence=0.85,
                                raw_data={"snippet": raw_snippet, "full_title": raw_title, "url": target_url}
                            )
                            if self.validate(record):
                                results.append(self.normalize(record))
                            if len(results) >= limit:
                                break
            except Exception:
                continue

        return results[:limit]
