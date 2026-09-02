import pytest
import asyncio
from backend.app.services.discovery.intent_hunter import IntentPostHunter, SocialIntentAdapter
from backend.app.services.discovery.registry import source_registry

def test_social_intent_adapter_properties_and_health():
    adapter = SocialIntentAdapter()
    assert adapter.source_name == "SocialIntent"
    assert adapter.get_rate_limit() >= 30

    health = asyncio.run(adapter.health_check())
    assert health["status"] == "CONNECTED"
    assert "provider" in health
    assert "supported_platforms" in health
    assert len(health["supported_platforms"]) >= 3

def test_intent_post_hunter_search():
    # Test searching for intent posts with category
    posts = asyncio.run(IntentPostHunter.search_posts(keyword="wordpress developer", category="wordpress", limit=5))
    assert isinstance(posts, list)
    if posts:
        post = posts[0]
        assert "author_name" in post
        assert "author_title" in post
        assert "author_linkedin_url" in post
        assert "post_url" in post
        assert "intent_tag" in post
        assert "urgency" in post
        assert "pitch_hook" in post
        assert post["urgency"] in ["HOT", "HIGH"]

def test_social_intent_registry_integration():
    adapter = source_registry.get_adapter("SocialIntent")
    assert adapter is not None
    assert isinstance(adapter, SocialIntentAdapter)
    
    health_map = asyncio.run(source_registry.check_all_health())
    assert "SocialIntent" in health_map
    assert health_map["SocialIntent"]["status"] == "CONNECTED"
