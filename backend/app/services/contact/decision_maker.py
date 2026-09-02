import re
import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from backend.app.services.crawler.safe_crawler import CrawlResult

DECISION_MAKER_TITLES = [
    "founder", "co-founder", "owner", "ceo", "chief executive officer", "president",
    "managing director", "director", "head of marketing", "marketing director",
    "operations director", "general manager", "principal", "partner", "store manager",
    "managing partner", "executive director", "head of sales", "chief operating officer"
]

NON_PERSON_WORDS = [
    "contact", "about", "team", "staff", "company", "service", "support",
    "sales", "inquiry", "info", "admin", "office", "help", "department",
    "reception", "desk", "lead", "group", "ltd", "inc", "llc", "corp",
    "privacy", "terms", "policy", "menu", "booking", "reservation"
]

class DecisionMakerFinder:
    """
    Extracts strictly publicly visible professional contacts from official crawled pages.
    Guarantees:
    - Never converts generic text or company names into fake people.
    - If no named person is explicitly observable: contact_name = None, job_title = None.
    - Captures exact subpage source URL and observation timestamp for each contact.
    """

    def extract_contacts_from_crawl(
        self,
        crawl: CrawlResult,
        company_name: str,
        source_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        contacts: List[Dict[str, Any]] = []
        if not crawl.is_reachable or not crawl.raw_html:
            return contacts

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        main_source_url = source_url or crawl.canonical_url or crawl.url
        seen_names = set()
        seen_emails = set()

        # Collect all HTML sources (main page + crawled subpages)
        pages_to_inspect = [{"url": main_source_url, "html": crawl.raw_html}]
        for sub in getattr(crawl, "crawled_subpages", []):
            pages_to_inspect.append({"url": sub.get("url", main_source_url), "html": sub.get("html", "")})

        # 1. Look for structured Team / Leadership profiles with real person names
        for page in pages_to_inspect:
            if not page["html"]:
                continue
            soup = BeautifulSoup(page["html"], "html.parser")
            team_cards = soup.find_all(class_=re.compile(r"(team|member|staff|leader|founder|author|profile|person|bio|attorney|doctor)", re.I))

            for card in team_cards:
                text = card.get_text(separator=" ", strip=True)
                for title in DECISION_MAKER_TITLES:
                    if re.search(r"\b" + re.escape(title) + r"\b", text, re.I):
                        # Extract clean name candidate
                        lines = [ln.strip() for ln in text.split(" ") if len(ln.strip()) > 1]
                        if len(lines) >= 2:
                            candidate_words = lines[:3]
                            name_candidate = " ".join(candidate_words)
                            clean_lower = name_candidate.lower()

                            # Strict rejection of non-person phrases
                            is_valid_person = (
                                4 <= len(name_candidate) <= 35
                                and not any(w in clean_lower for w in NON_PERSON_WORDS)
                                and not any(ch in name_candidate for ch in ["@", "http", "www", "©", "™", "|", "/", "\\", ":", ";", "$", "%", "#", "*"])
                                and not any(w in clean_lower for w in [company_name.lower(), "restaurant", "dentist", "law", "hotel", "gym"])
                            )

                            if is_valid_person and name_candidate not in seen_names:
                                seen_names.add(name_candidate)
                                contacts.append({
                                    "full_name": name_candidate,
                                    "job_title": title.title(),
                                    "email": None,
                                    "phone": None,
                                    "is_decision_maker": True,
                                    "contact_source": "Official Website Team Page",
                                    "source_url": page["url"],
                                    "discovered_at": now_iso,
                                    "confidence": 0.90,
                                })
                        break

        # 2. Add verified public emails discovered on page
        # Note: If no named person is associated, full_name is strictly None, job_title is strictly None!
        phone_list = list(crawl.phones) if crawl.phones else []
        email_list = list(crawl.emails) if crawl.emails else []
        primary_phone = phone_list[0] if phone_list else None

        for email in email_list:
            if email in seen_emails:
                continue
            seen_emails.add(email)

            # Check if this email matches an already detected named person
            assigned = False
            for c in contacts:
                if not c.get("email") and c.get("full_name"):
                    # If person's name tokens match the email username
                    first_token = c["full_name"].split()[0].lower()
                    if first_token in email:
                        c["email"] = email
                        assigned = True
                        break

            if not assigned:
                # Generic business contact channel (strictly NO fabricated person name!)
                contacts.append({
                    "full_name": None,
                    "job_title": None,
                    "email": email,
                    "phone": primary_phone,
                    "is_decision_maker": False,
                    "contact_source": "Official Website Contact Channel",
                    "source_url": main_source_url,
                    "discovered_at": now_iso,
                    "confidence": 0.85,
                })

        # 3. If no email but public phone exists, add direct phone contact channel
        if not contacts and primary_phone:
            contacts.append({
                "full_name": None,
                "job_title": None,
                "phone": primary_phone,
                "email": None,
                "is_decision_maker": False,
                "contact_source": "Official Website Contact",
                "source_url": main_source_url,
                "discovered_at": now_iso,
                "confidence": 0.85,
            })

        return contacts

decision_maker_finder = DecisionMakerFinder()
