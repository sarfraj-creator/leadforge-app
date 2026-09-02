import pytest
import asyncio
from backend.app.services.discovery.google_maps import GoogleMapsAdapter
from backend.app.services.discovery.ai_search import AISearchAdapter
from backend.app.services.discovery.registry import source_registry, SourceRegistry
from backend.app.services.discovery.base import DiscoveredRecord

def test_google_maps_adapter_properties_and_health():
    adapter = GoogleMapsAdapter()
    assert adapter.source_name == "GoogleMaps"
    assert adapter.get_rate_limit() >= 25
    
    health = asyncio.run(adapter.health_check())
    assert health["status"] in ["CONNECTED", "AVAILABLE"]
    assert "provider" in health
    assert "Google" in health["provider"]

def test_ai_search_adapter_properties_and_health():
    adapter = AISearchAdapter()
    assert adapter.source_name == "AISearch"
    assert adapter.get_rate_limit() >= 20
    
    health = asyncio.run(adapter.health_check())
    assert health["status"] in ["CONNECTED", "AVAILABLE", "UNCONFIGURED"]
    assert "provider" in health

def test_source_registry_registration():
    registry = SourceRegistry()
    assert "GoogleMaps" in registry._adapters
    assert "AISearch" in registry._adapters
    assert "OpenStreetMap" in registry._adapters
    assert "SearchEngine" in registry._adapters
    
    gmap = registry.get_adapter("GoogleMaps")
    assert isinstance(gmap, GoogleMapsAdapter)
    
    aisearch = registry.get_adapter("AISearch")
    assert isinstance(aisearch, AISearchAdapter)

def test_discovered_record_normalization():
    record = DiscoveredRecord(
        business_name="  Metro Dental Care LLC  ",
        source="GoogleMaps",
        website="http://www.metrodental.com/index.html",
        phone="(555) 234-5678",
        email="CONTACT@MetroDental.COM",
        city="Austin",
        industry="dental"
    )
    adapter = GoogleMapsAdapter()
    adapter.normalize(record)
    
    assert record.normalized_name == "metro dental care"
    assert record.domain == "metrodental.com"
    assert record.email == "contact@metrodental.com"
    assert record.dedup_hash is not None
    assert adapter.validate(record) is True

def test_registry_health_all():
    health_map = asyncio.run(source_registry.check_all_health())
    assert "GoogleMaps" in health_map
    assert "AISearch" in health_map
    assert "OpenStreetMap" in health_map
    assert health_map["GoogleMaps"]["status"] in ["CONNECTED", "AVAILABLE"]
    assert health_map["AISearch"]["status"] in ["CONNECTED", "AVAILABLE", "UNCONFIGURED"]
