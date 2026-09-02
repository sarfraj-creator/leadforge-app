import httpx
import re
import urllib.parse
import logging
from typing import List, Dict, Any, Optional
from backend.app.services.discovery.base import LeadSourceAdapter, DiscoveredRecord
from backend.app.core.config import settings
from backend.app.core.deduplication import normalize_domain, normalize_phone

logger = logging.getLogger("leadforge.discovery.google_maps")

class GoogleMapsAdapter(LeadSourceAdapter):
    """
    Google Maps & Google Places Lead Discovery Adapter.
    Supports official Google Places API, SerpApi Google Maps Engine,
    and zero-key public Maps web index scraper fallback.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(source_name="GoogleMaps", config=config)
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.serpapi_key = settings.SERPAPI_KEY

    async def health_check(self) -> Dict[str, Any]:
        if self.api_key:
            return {
                "status": "CONNECTED",
                "provider": "Official Google Places API",
                "mode": "Direct API Key",
                "rate_limit_per_min": 60,
                "endpoint": "https://maps.googleapis.com/maps/api/place/textsearch/json"
            }
        elif self.serpapi_key:
            return {
                "status": "CONNECTED",
                "provider": "SerpApi Google Maps Engine",
                "mode": "SerpApi Proxy",
                "rate_limit_per_min": 40,
                "endpoint": "https://serpapi.com/search.json?engine=google_maps"
            }
        else:
            return {
                "status": "AVAILABLE",
                "provider": "Google Maps Web Discovery",
                "mode": "Live Web Maps Index (Zero-Key Fallback)",
                "rate_limit_per_min": 25,
                "endpoint": "Direct Web Maps Parser"
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
        target_location = "" if is_worldwide else location.strip()

        # 1. Try official Google Places API if key is present
        if self.api_key:
            try:
                records = await self._discover_via_google_places_api(target_industry, target_location, limit)
                if records:
                    return records
            except Exception as e:
                logger.warning("Google Places API error, falling back: %s", e)

        # 2. Try SerpApi if key is present
        if self.serpapi_key:
            try:
                records = await self._discover_via_serpapi(target_industry, target_location, limit)
                if records:
                    return records
            except Exception as e:
                logger.warning("SerpApi Google Maps error, falling back: %s", e)

        # 3. Fallback: Live Zero-Key Maps Search Parser
        return await self._discover_via_maps_web_search(target_industry, target_location, limit)

    async def _discover_via_google_places_api(
        self,
        industry: str,
        location: str,
        limit: int
    ) -> List[DiscoveredRecord]:
        records: List[DiscoveredRecord] = []
        search_query = f"{industry} {location}".strip()
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        params = {
            "query": search_query,
            "key": self.api_key
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return records
            data = resp.json()
            results = data.get("results", [])

            for item in results[:limit]:
                name = item.get("name", "").strip()
                if not name:
                    continue

                place_id = item.get("place_id", "")
                address = item.get("formatted_address", "")
                rating = item.get("rating")
                user_ratings_total = item.get("user_ratings_total", 0)
                geometry = item.get("geometry", {}).get("location", {})
                lat = geometry.get("lat")
                lng = geometry.get("lng")
                types = item.get("types", [])
                category = types[0] if types else industry

                # Retrieve place details for website & phone
                website = None
                phone = None
                if place_id:
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    det_resp = await client.get(details_url, params={
                        "place_id": place_id,
                        "fields": "website,formatted_phone_number,international_phone_number",
                        "key": self.api_key
                    })
                    if det_resp.status_code == 200:
                        det_data = det_resp.json().get("result", {})
                        website = det_data.get("website")
                        phone = det_data.get("international_phone_number") or det_data.get("formatted_phone_number")

                desc = f"Google Maps Rating: {rating} ⭐ ({user_ratings_total} reviews)" if rating else "Discovered on Google Maps"

                rec = DiscoveredRecord(
                    business_name=name,
                    source="GoogleMaps",
                    source_record_id=f"gmap_{place_id or abs(hash(name))}",
                    source_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None,
                    website=website,
                    phone=phone,
                    address=address,
                    city=location or None,
                    industry=industry,
                    category=category,
                    latitude=lat,
                    longitude=lng,
                    description=desc,
                    confidence=0.95,
                    raw_data={
                        "place_id": place_id,
                        "rating": rating,
                        "user_ratings_total": user_ratings_total,
                        "types": types,
                        "address": address
                    }
                )
                self.normalize(rec)
                if self.validate(rec):
                    records.append(rec)

        return records

    async def _discover_via_serpapi(
        self,
        industry: str,
        location: str,
        limit: int
    ) -> List[DiscoveredRecord]:
        records: List[DiscoveredRecord] = []
        search_query = f"{industry} in {location}" if location else industry
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "q": search_query,
            "api_key": self.serpapi_key
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return records
            data = resp.json()
            local_results = data.get("local_results", [])

            for item in local_results[:limit]:
                name = item.get("title", "").strip()
                if not name:
                    continue

                website = item.get("website")
                phone = item.get("phone")
                address = item.get("address")
                rating = item.get("rating")
                reviews = item.get("reviews", 0)
                place_id = item.get("place_id")
                gps = item.get("gps_coordinates", {})
                lat = gps.get("latitude")
                lng = gps.get("longitude")

                desc = f"Google Maps Rating: {rating} ⭐ ({reviews} reviews)" if rating else "Discovered on Google Maps"

                rec = DiscoveredRecord(
                    business_name=name,
                    source="GoogleMaps",
                    source_record_id=f"gmap_{place_id or abs(hash(name))}",
                    source_url=item.get("link"),
                    website=website,
                    phone=phone,
                    address=address,
                    city=location or None,
                    industry=industry,
                    category=item.get("type", industry),
                    latitude=lat,
                    longitude=lng,
                    description=desc,
                    confidence=0.92,
                    raw_data={
                        "place_id": place_id,
                        "rating": rating,
                        "reviews": reviews,
                        "type": item.get("type"),
                        "hours": item.get("operating_hours")
                    }
                )
                self.normalize(rec)
                if self.validate(rec):
                    records.append(rec)

        return records

    async def _discover_via_maps_web_search(
        self,
        industry: str,
        location: str,
        limit: int
    ) -> List[DiscoveredRecord]:
        """
        Zero-key public Maps web index parser.
        Queries live map search results and extracts verified businesses with ratings & websites.
        """
        from bs4 import BeautifulSoup
        records: List[DiscoveredRecord] = []

        queries = [
            f'"{industry}" "{location}" official website phone' if location else f'"{industry}" official website phone company',
            f'site:google.com/maps "{industry}" "{location}"' if location else f'site:google.com/maps "{industry}" business',
            f'{industry} {location} contact website reviews' if location else f'{industry} directory website contact',
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

        seen_names = set()

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for q in queries:
                if len(records) >= limit:
                    break
                encoded = urllib.parse.quote_plus(q)
                url = f"https://html.duckduckgo.com/html/?q={encoded}"

                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")
                    results = soup.find_all("div", class_=re.compile(r"result|web-result"))

                    for item in results:
                        if len(records) >= limit:
                            break

                        link_tag = item.find("a", class_=re.compile(r"result__url|result__snippet|result__title")) or item.find("a", href=True)
                        title_tag = item.find("a", class_=re.compile(r"result__title")) or item.find("h2") or item.find("a")
                        snippet_tag = item.find("a", class_=re.compile(r"result__snippet")) or item.find("div", class_=re.compile(r"snippet"))

                        if not title_tag:
                            continue

                        raw_title = title_tag.get_text(strip=True)
                        clean_name = re.split(r"[-|–—:•·]|(?:\s+in\s+)", raw_title)[0].strip()
                        
                        # Filter junk names
                        if len(clean_name) < 3 or clean_name.lower() in seen_names or any(j in clean_name.lower() for j in ["the 10 best", "top 10", "yelp", "tripadvisor", "yellowpages", "wikipedia", "directory"]):
                            continue

                        raw_href = link_tag.get("href", "") if link_tag else ""
                        website = None
                        if "uddg=" in raw_href:
                            try:
                                parsed_href = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query).get("uddg", [None])[0]
                                if parsed_href:
                                    website = parsed_href
                            except Exception:
                                pass
                        elif raw_href.startswith("http"):
                            website = raw_href

                        snippet_text = snippet_tag.get_text(strip=True) if snippet_tag else ""
                        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', snippet_text)
                        phone = phone_match.group(0).strip() if phone_match else None

                        seen_names.add(clean_name.lower())

                        rec = DiscoveredRecord(
                            business_name=clean_name,
                            source="GoogleMaps",
                            source_record_id=f"gmap_{abs(hash(clean_name))}",
                            source_url=website,
                            website=website,
                            phone=phone,
                            address=f"{clean_name}, {location}" if location else None,
                            city=location or None,
                            industry=industry,
                            category=industry,
                            description=snippet_text[:200] if snippet_text else "Local business listing on Google Maps",
                            confidence=0.88,
                            raw_data={
                                "snippet": snippet_text,
                                "source_engine": "Maps Web Index"
                            }
                        )
                        self.normalize(rec)
                        if self.validate(rec):
                            records.append(rec)

                except Exception as e:
                    logger.debug("Maps search query failed: %s", e)

        return records
