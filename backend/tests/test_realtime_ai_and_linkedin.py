import pytest
from backend.app.services.ai.perplexity import PerplexityProvider
from backend.app.services.ai.gemini import GeminiProvider
from backend.app.services.ai.factory import ai_factory
from backend.app.services.discovery.ai_search import AISearchAdapter
from backend.app.models.contact import Contact

@pytest.mark.anyio
async def test_perplexity_provider_unconfigured():
    provider = PerplexityProvider(api_key="", model="sonar")
    assert provider.is_configured is False
    health = await provider.health_check()
    assert health["status"] == "UNCONFIGURED"
    assert health["provider"] == "Perplexity AI"

@pytest.mark.anyio
async def test_gemini_provider_unconfigured():
    provider = GeminiProvider(api_key="", model="gemini-2.0-flash")
    assert provider.is_configured is False
    health = await provider.health_check()
    assert health["status"] == "UNCONFIGURED"
    assert health["provider"] == "Google Gemini"

@pytest.mark.anyio
async def test_ai_factory_fallback_and_health():
    health = await ai_factory.get_all_providers_health()
    assert "active_ai_provider" in health
    assert "providers" in health
    assert "perplexity" in health["providers"]
    assert "gemini" in health["providers"]
    assert "huggingface" in health["providers"]

@pytest.mark.anyio
async def test_ai_search_adapter_health():
    adapter = AISearchAdapter()
    health = await adapter.health_check()
    assert health["status"] in ["CONNECTED", "AVAILABLE"]
    assert health["real_time_web"] is True

@pytest.mark.anyio
async def test_ai_search_adapter_public_fallback():
    adapter = AISearchAdapter()
    records = await adapter.discover(query="dentist", location="Sunnyvale", limit=3)
    assert isinstance(records, list)
    for r in records:
        assert r.business_name is not None
        assert r.source == "AISearch"

def test_contact_linkedin_field():
    c = Contact(
        company_id=1,
        full_name="Sarah Connor",
        job_title="CEO",
        is_decision_maker=True,
        linkedin_url="https://www.linkedin.com/in/sarah-connor-test"
    )
    assert c.full_name == "Sarah Connor"
    assert c.is_decision_maker is True
    assert c.linkedin_url == "https://www.linkedin.com/in/sarah-connor-test"
