import logging
from typing import Dict, Any, Optional, List
from backend.app.services.ai.base import AIProvider
from backend.app.services.ai.perplexity import PerplexityProvider
from backend.app.services.ai.gemini import GeminiProvider
from backend.app.services.ai.huggingface import HuggingFaceProvider
from backend.app.core.config import settings

logger = logging.getLogger("leadforge.ai.factory")

class AIEngineFactory:
    """
    Unified AI Provider Factory for Reasoning, Live Web Search, and Structured JSON Generation.
    Supports Perplexity AI, Google Gemini, and Hugging Face with task-specialized multi-model routing.
    """

    def __init__(self):
        self.perplexity = PerplexityProvider()
        self.gemini = GeminiProvider()
        self.huggingface = HuggingFaceProvider()

    def get_provider(self, name: Optional[str] = None, task: Optional[str] = None) -> AIProvider:
        provider_name = (name or settings.ACTIVE_AI_PROVIDER or "auto").lower()

        if provider_name == "perplexity":
            return self.perplexity
        elif provider_name == "gemini":
            return self.gemini
        elif provider_name == "huggingface":
            return self.huggingface
        elif provider_name == "auto":
            # Auto-selection priority: Perplexity -> Gemini -> Hugging Face
            if self.perplexity.is_configured:
                return self.perplexity
            elif self.gemini.is_configured:
                return self.gemini
            else:
                return self.huggingface
        return self.huggingface

    def get_search_grounded_provider(self) -> Optional[AIProvider]:
        """
        Returns the optimal provider for real-time web search grounding.
        """
        search_mode = (settings.AI_SEARCH_PROVIDER or "auto").lower()

        if search_mode == "perplexity" and self.perplexity.is_configured:
            return self.perplexity
        elif search_mode == "gemini" and self.gemini.is_configured:
            return self.gemini
        elif search_mode == "auto":
            if self.perplexity.is_configured:
                return self.perplexity
            elif self.gemini.is_configured:
                return self.gemini

        return None

    async def get_all_providers_health(self) -> Dict[str, Any]:
        """Returns live connection and configuration status across all AI engines."""
        p_health = await self.perplexity.health_check()
        g_health = await self.gemini.health_check()
        h_health = await self.huggingface.health_check()

        active = self.get_provider()
        active_name = active.__class__.__name__.replace("Provider", "")

        search_provider = self.get_search_grounded_provider()
        search_name = search_provider.__class__.__name__.replace("Provider", "") if search_provider else "Public Discovery Fallback"

        return {
            "active_ai_provider": active_name,
            "active_search_provider": search_name,
            "providers": {
                "perplexity": p_health,
                "gemini": g_health,
                "huggingface": h_health
            }
        }

ai_factory = AIEngineFactory()
