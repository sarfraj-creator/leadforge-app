import httpx
import json
import re
import logging
from typing import Dict, Any, List, Optional
from backend.app.services.ai.base import AIProvider
from backend.app.core.config import settings

logger = logging.getLogger("leadforge.ai.gemini")

class GeminiProvider(AIProvider):
    """
    Google Gemini AI Provider for High-Speed Reasoning and
    Google Search Grounded Real-Time Lead Discovery.
    Models supported: 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro'.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-2.0-flash"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def _get_url(self) -> str:
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    async def health_check(self) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "status": "UNCONFIGURED",
                "provider": "Google Gemini",
                "message": "GEMINI_API_KEY is not configured.",
                "model": self.model
            }
        try:
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": "Respond in one word: 'CONNECTED'."}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self._get_url(), json=payload)
                if res.status_code == 200:
                    return {
                        "status": "CONNECTED",
                        "provider": "Google Gemini",
                        "model": self.model,
                        "google_search_grounding": True,
                        "mode": "Google Search Grounded Intelligence"
                    }
                else:
                    return {
                        "status": "ERROR",
                        "provider": "Google Gemini",
                        "status_code": res.status_code,
                        "error": res.text[:200],
                        "model": self.model
                    }
        except Exception as e:
            return {
                "status": "ERROR",
                "provider": "Google Gemini",
                "error": str(e),
                "model": self.model
            }

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        enable_search_grounding: bool = False
    ) -> str:
        if not self.is_configured:
            return "Gemini API key is not configured."

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"{system_prompt}\n\nUser Request: {user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if enable_search_grounding:
            # Enable Google Search Grounding tool
            payload["tools"] = [{"googleSearch": {}}]

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(self._get_url(), json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                return ""
            else:
                logger.error("Gemini API error: %d %s", resp.status_code, resp.text)
                raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text[:300]}")

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        enable_search_grounding: bool = False
    ) -> Dict[str, Any]:
        json_sys_prompt = system_prompt + "\nIMPORTANT: You must return strictly valid JSON. Do not include markdown or explanations."
        
        text = await self.generate_text(
            system_prompt=json_sys_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            enable_search_grounding=enable_search_grounding
        )

        cleaned = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned.strip())
        cleaned = re.sub(r"```$", "", cleaned.strip()).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
            logger.warning("Failed to decode JSON from Gemini output: %s", text[:200])
            return {"error": "Failed to parse JSON response", "raw": text}

    async def search_grounded_leads(
        self,
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Uses Gemini with Google Search Grounding to discover real operating businesses,
        verified websites, and verified decision-maker LinkedIn profiles.
        """
        if not self.is_configured:
            return []

        target_industry = (industry or query or "business").strip()
        loc_str = location.strip() if location and location.upper() not in ["WORLDWIDE", "GLOBAL", "ALL"] else ""
        loc_context = f"in {loc_str}" if loc_str else "globally"

        system_prompt = f"""You are a senior business intelligence research agent with direct Google Search Grounding.
Search Google in real time to find real, active {target_industry} companies {loc_context}.

DATA TRUTH REQUIREMENTS:
1. Only return real, verifiable operating companies.
2. Provide their official canonical website URL (never directory aggregators like Yelp, Yellowpages, Clutch).
3. Identify the true executive leader / decision maker (Founder, CEO, Owner, Managing Director).
4. Provide their verified public LinkedIn URL (format: https://www.linkedin.com/in/...).
5. If no verified person or LinkedIn profile is found, return null (never fabricate).
6. Return a valid JSON array of up to {limit} companies."""

        user_prompt = f"""Search Google and list {limit} {target_industry} businesses {loc_context} in this JSON schema:
[
  {{
    "business_name": "Company Name",
    "website": "https://company.com",
    "phone": "+1 408 555 0199",
    "email": "info@company.com",
    "address": "123 Street, City, State",
    "city": "City",
    "state": "State",
    "country": "Country",
    "industry": "{target_industry}",
    "description": "Factual overview",
    "decision_maker_name": "Full Name",
    "decision_maker_role": "CEO / Founder",
    "decision_maker_linkedin": "https://www.linkedin.com/in/username",
    "confidence": 0.95
  }}
]"""

        try:
            res = await self.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=3500,
                enable_search_grounding=True
            )
            if isinstance(res, list):
                return res
            elif isinstance(res, dict) and "companies" in res and isinstance(res["companies"], list):
                return res["companies"]
            elif isinstance(res, dict) and "items" in res and isinstance(res["items"], list):
                return res["items"]
            return []
        except Exception as e:
            logger.error("Gemini grounded lead search error: %s", e)
            return []
