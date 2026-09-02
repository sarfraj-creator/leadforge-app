import hashlib
import json
from typing import Dict, Any, List, Optional
from backend.app.services.ai.factory import ai_factory
from backend.app.core.config import settings

class PromptEngine:
    def get_provider(self, task: Optional[str] = None):
        return ai_factory.get_provider(task=task)

    def get_input_hash(self, payload: Dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    async def analyze_lead(
        self,
        company_name: str,
        industry: str,
        website_url: Optional[str],
        audit_scores: Dict[str, int],
        observed_issues: List[str],
        detected_tech: List[str]
    ) -> Dict[str, Any]:
        """
        Factual AI Lead Analysis using specialized Audit Model.
        """
        system_prompt = """You are a senior digital agency software architect and B2B lead analyst.
Your task is to analyze technical audit evidence and provide a structured qualification report for agency outreach.

STRICT RULES:
1. Distinguish between:
   - OBSERVED: Facts directly extracted from the technical audit and website.
   - INFERRED: Logical service opportunities based directly on observed facts.
   - UNKNOWN: Information not observed in data (do NOT fabricate).
2. DO NOT invent revenue, employee headcount, or business facts that are not provided.
3. Return ONLY valid JSON format matching this schema:
{
  "lead_score": 85,
  "priority": "HIGH",
  "opportunities": ["string"],
  "recommended_services": ["string"],
  "observed_issues": ["string"],
  "reasoning_summary": "string",
  "confidence": 0.90
}"""

        user_prompt = f"""COMPANY: {company_name}
INDUSTRY: {industry}
WEBSITE: {website_url or 'None (No website found)'}

OBSERVED AUDIT METRICS (0-100):
- Overall: {audit_scores.get('overall', 0)}
- Performance: {audit_scores.get('performance', 0)}
- Mobile: {audit_scores.get('mobile', 0)}
- SEO: {audit_scores.get('seo', 0)}
- Security: {audit_scores.get('security', 0)}
- Conversion: {audit_scores.get('conversion', 0)}

OBSERVED ISSUES:
{json.dumps(observed_issues, indent=2)}

DETECTED TECHNOLOGIES:
{', '.join(detected_tech) if detected_tech else 'Standard HTML / Unknown'}

Generate the factual structured lead qualification report."""

        provider = self.get_provider(task="audit")
        return await provider.generate_json(system_prompt, user_prompt, task="audit")

    async def generate_personalized_email(
        self,
        company_name: str,
        contact_name: str,
        website_url: Optional[str],
        opportunity_type: str,
        primary_issue: str,
        recommended_service: str
    ) -> Dict[str, str]:
        """
        Generates cold email outreach using specialized Outreach Copywriting Model.
        """
        system_prompt = """You are an expert agency outreach strategist.
Write a concise, professional cold email (under 125 words) to a business owner.

RULES:
- Never say "I was impressed by your company" or fake compliments.
- Reference the exact observed technical issue on their website.
- Propose the specific recommended solution.
- Include a low-friction, polite call to action (e.g. 10-minute call or free mock-up).
- Return ONLY valid JSON:
{
  "subject": "string",
  "opening": "string",
  "problem": "string",
  "value_proposition": "string",
  "cta": "string",
  "signature": "string"
}"""

        user_prompt = f"""PROSPECT NAME: {contact_name}
COMPANY: {company_name}
WEBSITE: {website_url or 'No website'}
DETECTED SERVICE OPPORTUNITY: {opportunity_type}
OBSERVED ISSUE: {primary_issue}
RECOMMENDED AGENCY SERVICE: {recommended_service}

Generate the personalized outreach email."""

        provider = self.get_provider(task="outreach")
        return await provider.generate_json(system_prompt, user_prompt, task="outreach")

    async def classify_reply(
        self,
        inbound_body: str,
        subject: str,
        previous_outreach_snippet: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classifies incoming responses using specialized Sentiment & Classification Model.
        """
        system_prompt = """You are an AI sales inbox assistant. Classify the incoming prospect email.
Categories allowed:
- "Interested"
- "Meeting Request"
- "Pricing Request"
- "Question"
- "Not Interested"
- "Wrong Person"
- "Out of Office"
- "Unsubscribe"

Return valid JSON:
{
  "classification": "Interested",
  "sentiment": 0.85,
  "reasoning": "Prospect requested a meeting time.",
  "suggested_next_stage": "Interested"
}"""

        user_prompt = f"""SUBJECT: {subject}
INBOUND EMAIL TEXT:
{inbound_body}

PREVIOUS OUTREACH CONTEXT:
{previous_outreach_snippet or 'Initial agency outreach'}

Classify the reply."""

        provider = self.get_provider(task="classification")
        return await provider.generate_json(system_prompt, user_prompt, task="classification")

    async def interpret_natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Translates natural language campaign queries using specialized Extraction Model.
        """
        system_prompt = """You are a natural language search compiler for a B2B prospecting engine.
Translate the user's plain English query into structured search parameters.
Return ONLY valid JSON matching:
{
  "industry": "restaurant",
  "location": "Mumbai",
  "opportunity_type": "Responsive Redesign",
  "keywords": "restaurant cafe dining",
  "min_lead_score": 65,
  "freshness_days": 7,
  "max_leads": 50
}"""

        user_prompt = f"USER QUERY: {query}"
        provider = self.get_provider(task="extraction")
        return await provider.generate_json(system_prompt, user_prompt, task="extraction")

prompt_engine = PromptEngine()
