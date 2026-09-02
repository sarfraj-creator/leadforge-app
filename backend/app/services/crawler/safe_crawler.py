import httpx
import time
import hashlib
import re
import urllib.parse
import ssl
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Set, Tuple
from backend.app.core.ssrf import validate_url_for_ssrf
from backend.app.core.config import settings

CONTACT_SUBPAGE_PATHS = [
    "/contact", "/contact-us", "/contactus", "/get-in-touch",
    "/about", "/about-us", "/aboutus", "/our-story",
    "/team", "/our-team", "/staff", "/leadership", "/management",
    "/locations", "/find-us", "/book", "/reservations", "/appointment"
]

class CrawlResult:
    def __init__(self, url: str):
        self.url = url
        self.domain = urllib.parse.urlparse(url).netloc
        self.canonical_url: Optional[str] = None
        self.is_reachable: bool = False
        self.website_reachable: bool = False
        self.website_official_verified: bool = False
        self.http_status: Optional[int] = None
        self.ssl_valid: Optional[bool] = None
        self.ssl_error: Optional[str] = None
        self.redirect_target: Optional[str] = None
        self.load_time_ms: int = 0
        self.page_size_bytes: int = 0
        self.html_hash: str = ""
        self.content_hash: str = ""
        self.raw_html: str = ""
        self.headers: Dict[str, str] = {}
        
        # Extracted Content
        self.title: Optional[str] = None
        self.meta_description: Optional[str] = None
        self.h1_tags: List[str] = []
        self.h2_tags: List[str] = []
        self.visible_text: str = ""
        self.links: List[str] = []
        self.images: List[Dict[str, Any]] = []
        self.forms: List[Dict[str, Any]] = []
        self.buttons: List[str] = []
        self.cta_texts: List[str] = []
        self.emails: Set[str] = set()
        self.phones: Set[str] = set()
        self.social_links: Dict[str, str] = {}
        self.viewport_meta: Optional[str] = None
        self.has_robots_txt: bool = False
        self.has_sitemap: bool = False
        self.error: Optional[str] = None
        self.match_evidence: List[str] = []
        self.crawled_subpages: List[Dict[str, Any]] = [] # [{url, path, status, html}]

class SafeCrawler:
    def __init__(self, timeout: int = 15, max_pages: int = 4):
        self.timeout = timeout
        self.max_pages = max_pages

    async def crawl_site(
        self,
        target_url: str,
        business_name: Optional[str] = None,
        city: Optional[str] = None,
        crawl_subpages: bool = True
    ) -> CrawlResult:
        result = CrawlResult(target_url)
        
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url
            
        is_safe, msg = validate_url_for_ssrf(target_url)
        if not is_safe:
            result.error = f"SSRF Security Violation: {msg}"
            result.is_reachable = False
            result.website_reachable = False
            return result
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        
        start_time = time.time()
        response = None
        
        # Primary Attempt with standard TLS verification
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                verify=True
            ) as client:
                response = await client.get(target_url, headers=headers)
                result.ssl_valid = str(response.url).startswith("https://")
        except (httpx.ConnectError, ssl.SSLCertVerificationError, ssl.SSLError) as ssl_err:
            result.ssl_valid = False
            result.ssl_error = f"SSL Certificate Verification Issue: {str(ssl_err)}"
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    verify=False
                ) as insecure_client:
                    response = await insecure_client.get(target_url, headers=headers)
            except Exception as e2:
                result.error = f"Failed to connect to host: {str(e2)}"
                result.is_reachable = False
                result.website_reachable = False
                return result
        except httpx.TimeoutException:
            result.error = "Connection timed out"
            result.is_reachable = False
            result.website_reachable = False
            return result
        except Exception as e:
            result.error = str(e)
            result.is_reachable = False
            result.website_reachable = False
            return result

        if response:
            result.load_time_ms = int((time.time() - start_time) * 1000)
            result.http_status = response.status_code
            result.headers = dict(response.headers)
            result.canonical_url = str(response.url)
            
            # Ensure final redirected destination is safe
            is_dest_safe, dest_reason = validate_url_for_ssrf(result.canonical_url)
            if not is_dest_safe or "192.168." in result.canonical_url or "10." in result.canonical_url:
                result.error = f"Target redirected to blocked address: {dest_reason}"
                result.is_reachable = False
                result.website_reachable = False
                result.website_official_verified = False
                return result

            result.is_reachable = (200 <= response.status_code < 400)
            result.website_reachable = result.is_reachable
            result.page_size_bytes = len(response.content)
            result.raw_html = response.text
            
            if result.page_size_bytes > settings.CRAWL_MAX_RESPONSE_SIZE:
                result.raw_html = result.raw_html[:settings.CRAWL_MAX_RESPONSE_SIZE]
                
            result.html_hash = hashlib.sha256(result.raw_html.encode('utf-8')).hexdigest()
            
            # Parse main page
            self._parse_page_content(result, result.raw_html, result.canonical_url)
            
            # Deep permitted subpage crawling for contact information
            if crawl_subpages and result.is_reachable:
                await self._crawl_permitted_subpages(result, headers)
            
            # Verify official ownership against business details
            self._verify_official_match(result, business_name, city)

        return result

    async def _crawl_permitted_subpages(self, result: CrawlResult, headers: Dict[str, str]):
        """
        Visits permitted subpages like /contact, /about, /team to discover publicly displayed contact channels.
        """
        parsed_base = urllib.parse.urlparse(result.canonical_url or result.url)
        base_origin = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        # Discover subpage candidates from internal links or known paths
        discovered_paths: Set[str] = set()
        soup = BeautifulSoup(result.raw_html, "html.parser")
        
        for a in soup.find_all("a", href=True):
            href = a['href'].strip()
            for cp in CONTACT_SUBPAGE_PATHS:
                if cp in href.lower():
                    clean_url = urllib.parse.urljoin(base_origin, href)
                    if clean_url.startswith(base_origin) and clean_url != result.canonical_url:
                        discovered_paths.add(clean_url)
                        
        # Also probe top standard contact paths if not found in links
        if len(discovered_paths) < 2:
            discovered_paths.add(f"{base_origin}/contact")
            discovered_paths.add(f"{base_origin}/about")

        paths_to_crawl = list(discovered_paths)[:self.max_pages]

        async with httpx.AsyncClient(timeout=8, follow_redirects=True, verify=False) as sub_client:
            for sub_url in paths_to_crawl:
                is_safe, _ = validate_url_for_ssrf(sub_url)
                if not is_safe:
                    continue
                try:
                    resp = await sub_client.get(sub_url, headers=headers)
                    if 200 <= resp.status_code < 400 and resp.text:
                        sub_html = resp.text[:settings.CRAWL_MAX_RESPONSE_SIZE]
                        result.crawled_subpages.append({
                            "url": str(resp.url),
                            "path": urllib.parse.urlparse(str(resp.url)).path,
                            "status": resp.status_code,
                            "html": sub_html
                        })
                        # Extract additional contact information from subpage
                        self._extract_contact_channels(result, sub_html, str(resp.url))
                except Exception:
                    pass

    def _parse_page_content(self, result: CrawlResult, html: str, page_url: str):
        soup = BeautifulSoup(html, "html.parser")
        
        # Title & Meta
        title_el = soup.find("title")
        if title_el:
            result.title = title_el.get_text(strip=True)
            
        meta_desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        if meta_desc:
            result.meta_description = meta_desc.get("content", "").strip()
            
        viewport_el = soup.find("meta", attrs={"name": re.compile(r"viewport", re.I)})
        if viewport_el:
            result.viewport_meta = viewport_el.get("content", "").strip()
            
        # Headings
        result.h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
        result.h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]
        
        # Visible Text & Content Hash
        for script_or_style in soup(["script", "style", "noscript", "svg", "header", "footer"]):
            script_or_style.extract()
        
        visible_text = soup.get_text(separator=" ", strip=True)
        result.visible_text = visible_text[:10000]
        result.content_hash = hashlib.sha256(result.visible_text.encode('utf-8')).hexdigest()
        
        # Buttons & CTAs
        buttons = []
        for btn in soup.find_all(["button", "a"]):
            text = btn.get_text(strip=True)
            if text and len(text) < 50:
                if re.search(r"\b(book|contact|quote|call|schedule|demo|start|buy|order|get in touch|talk to|request|reserve|menu)\b", text, re.I):
                    result.cta_texts.append(text)
                if btn.name == "button":
                    buttons.append(text)
        result.buttons = buttons[:20]
        
        # Images & Alt Attributes
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src", "")
            alt = img.get("alt")
            result.images.append({
                "src": src,
                "has_alt": bool(alt and alt.strip()),
                "alt": alt or ""
            })
            
        # Forms
        for form in soup.find_all("form"):
            inputs = [inp.get("type", "text") for inp in form.find_all("input")]
            has_submit = bool(form.find(["input", "button"], attrs={"type": "submit"})) or bool(form.find("button"))
            result.forms.append({
                "action": form.get("action", ""),
                "inputs": inputs,
                "has_submit": has_submit
            })
            
        # Extract direct contact channels
        self._extract_contact_channels(result, html, page_url)

    def _extract_contact_channels(self, result: CrawlResult, html: str, page_url: str):
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. mailto: links (highest reliability)
        for a in soup.find_all("a", href=True):
            href = a['href'].strip()
            if href.lower().startswith("mailto:"):
                clean_email = href.split("?")[0].replace("mailto:", "").strip().lower()
                if "@" in clean_email and "." in clean_email:
                    result.emails.add(clean_email)
            elif href.lower().startswith("tel:"):
                clean_phone = href.replace("tel:", "").strip()
                if len(clean_phone) >= 7:
                    result.phones.add(clean_phone)
                    
        # 2. Text regex extraction
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,12}'
        for em in re.findall(email_pattern, html):
            clean_em = em.lower().strip()
            if not re.search(r'\.(png|jpg|jpeg|gif|svg|webp|css|js|woff|woff2|json|txt|md|html)$', clean_em):
                domain_part = clean_em.split("@")[-1]
                tld = domain_part.split(".")[-1]
                if tld.isalpha() and len(tld) >= 2 and not any(dummy in clean_em for dummy in ["example.com", "domain.com", "sentry.io", "wixpress.com", "schema.org", "core-js"]):
                    result.emails.add(clean_em)
                
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        for ph in re.findall(phone_pattern, html):
            if ph and len(ph.strip()) >= 7:
                result.phones.add(ph.strip())
                
        # 3. Social links
        for a in soup.find_all("a", href=True):
            href = a['href'].lower()
            if "linkedin.com" in href:
                result.social_links["linkedin"] = a['href']
            elif "facebook.com" in href:
                result.social_links["facebook"] = a['href']
            elif "instagram.com" in href:
                result.social_links["instagram"] = a['href']
            elif "twitter.com" in href or "x.com" in href:
                result.social_links["twitter"] = a['href']
            elif "youtube.com" in href:
                result.social_links["youtube"] = a['href']

    def _verify_official_match(self, result: CrawlResult, business_name: Optional[str], city: Optional[str]):
        """
        Evidence-based matching verifying whether the reachable website
        genuinely corresponds to the discovered business entity.
        Never fabricates official verification without observable evidence.
        """
        if not result.is_reachable:
            result.website_official_verified = False
            return

        evidence = []
        is_verified = False
        
        if business_name:
            clean_name = business_name.lower().strip()
            name_tokens = [t for t in re.findall(r'[a-zA-Z0-9]+', clean_name) if len(t) > 2 and t not in ["the", "and", "bar", "restaurant", "cafe", "ltd", "inc", "llc"]]
            
            # Check domain name token overlap
            matching_domain_tokens = [t for t in name_tokens if t in result.domain.lower()]
            if matching_domain_tokens:
                evidence.append(f"Domain '{result.domain}' matches business brand keyword(s): {', '.join(matching_domain_tokens)}")
                is_verified = True

            # Check Page Title match
            if result.title and any(t in result.title.lower() for t in name_tokens):
                evidence.append(f"Page title '{result.title}' contains business brand name")
                is_verified = True

            # Check H1 / Heading match
            if any(any(t in h.lower() for t in name_tokens) for h in result.h1_tags):
                evidence.append(f"Page H1 heading references business name")
                is_verified = True

            # Check Visible Text presence
            if clean_name in result.visible_text.lower():
                evidence.append("Full business name identified in primary page text")
                is_verified = True

        # Check City presence in text / title
        if city and city.lower() != "worldwide" and city.lower() in result.visible_text.lower():
            evidence.append(f"Location '{city}' confirmed on website markup")

        result.website_official_verified = is_verified
        result.match_evidence = evidence

safe_crawler = SafeCrawler()
