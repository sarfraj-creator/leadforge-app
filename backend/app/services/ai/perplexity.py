import httpx
import json
import re
import logging
from typing import Dict, Any, List, Optional
from backend.app.services.ai.base import AIProvider
from backend.app.core.config import settings

logger = logging.getLogger("leadforge.ai.perplexity")

class PerplexityProvider(AIProvider):
    """
    Perplexity AI Provider for Real-Time Live Web Search, Grounded Reasoning,
    and High-Precision Executive & LinkedIn Lead Discovery.
    Models supported: 'sonar', 'sonar-pro', 'sonar-reasoning'.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.PERPLEXITY_API_KEY
        self.model = model or settings.PERPLEXITY_MODEL or "sonar"
        self.base_url = "https://api.perplexity.ai/chat/completions"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def health_check(self) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "status": "UNCONFIGURED",
                "provider": "Perplexity AI",
                "message": "PERPLEXITY_API_KEY is not configured.",
                "model": self.model
            }
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a test assistant. Respond in one word: 'CONNECTED'."},
                    {"role": "user", "content": "ping"}
                ],
                "max_tokens": 10
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.base_url, headers=self._get_headers(), json=payload)
                if res.status_code == 200:
                    return {
                        "status": "CONNECTED",
                        "provider": "Perplexity AI",
                        "model": self.model,
                        "real_time_web": True,
                        "mode": "Live Web Grounded Search"
                    }
                else:
                    return {
                        "status": "ERROR",
                        "provider": "Perplexity AI",
                        "status_code": res.status_code,
                        "error": res.text[:200],
                        "model": self.model
                    }
        except Exception as e:
            return {
                "status": "ERROR",
                "provider": "Perplexity AI",
                "error": str(e),
                "model": self.model
            }

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> str:
        if not self.is_configured:
            return "Perplexity API key is not configured."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(self.base_url, headers=self._get_headers(), json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                logger.error("Perplexity error: %d %s", resp.status_code, resp.text)
                raise RuntimeError(f"Perplexity API error {resp.status_code}: {resp.text[:300]}")

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        json_sys_prompt = system_prompt + "\nIMPORTANT: You must return ONLY raw valid JSON. Do not include markdown code blocks, explanations, or commentary."

        text = await self.generate_text(json_sys_prompt, user_prompt, temperature, max_tokens)
        
        # Clean markdown code blocks if returned
        cleaned = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned.strip())
        cleaned = re.sub(r"```$", "", cleaned.strip()).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback regex extraction
            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
            logger.warning("Failed to decode JSON from Perplexity output: %s", text[:200])
            return {"error": "Failed to parse JSON response", "raw": text}

    async def search_grounded_leads(
        self,
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Specialized real-time grounded research function.
        Finds live businesses, verified official websites, and real executive LinkedIn profiles.
        """
        if not self.is_configured:
            return []

        target_industry = (industry or query or "business").strip()
        loc_str = location.strip() if location and location.upper() not in ["WORLDWIDE", "GLOBAL", "ALL"] else ""
        loc_context = f"in {loc_str}" if loc_str else "globally"

        system_prompt = f"""You are a specialized B2B real-time market intelligence and executive contact researcher.
Your task is to search the live web and find real, operating {target_industry} companies {loc_context}.

STRICT DATA TRUTH RULES:
1. Every business must be an actual, real operating entity.
2. Find their OFFICIAL business website (not directory aggregators like Yelp, Clutch, YellowPages, TripAdvisor).
3. Find the REAL Decision Maker (Founder, CEO, Owner, Managing Director, Partner, VP).
4. Find their direct, verified public LinkedIn profile URL (format: https://www.linkedin.com/in/username).
5. If a LinkedIn URL or person name cannot be verified for a company, set it to null (do NOT fabricate).
6. Find their public business phone and email if available.
7. Return a JSON array of up to {limit} distinct company objects.

Return ONLY a JSON array with objects matching:
[
  {{
    "business_name": "Acme Healthcare Clinic",
    "website": "https://www.acmeclinic.com",
    "phone": "+1 408 555 0199",
    "email": "contact@acmeclinic.com",
    "address": "123 Main St, Sunnyvale, CA",
    "city": "Sunnyvale",
    "state": "CA",
    "country": "US",
    "industry": "{target_industry}",
    "description": "Short factual description of services",
    "decision_maker_name": "Dr. Sarah Jenkins",
    "decision_maker_role": "Founder & Managing Director",
    "decision_maker_linkedin": "https://www.linkedin.com/in/sarah-jenkins-clinic",
    "confidence": 0.95
  }}
]"""

        user_prompt = f"Search live web: Find {limit} top {target_industry} businesses {loc_context} with verified websites, founder/CEO identities, and LinkedIn URLs."

        try:
            res = await self.generate_json(system_prompt, user_prompt, temperature=0.1, max_tokens=3500)
            if isinstance(res, list):
                return res
            elif isinstance(res, dict) and "companies" in res and isinstance(res["companies"], list):
                return res["companies"]
            elif isinstance(res, dict) and "items" in res and isinstance(res["items"], list):
                return res["items"]
            return []
        except Exception as e:
            logger.error("Perplexity grounded lead search error: %s", e)
            return []
