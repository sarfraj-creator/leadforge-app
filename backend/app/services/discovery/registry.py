from typing import Dict, List, Any, Optional
import asyncio
from backend.app.services.discovery.base import LeadSourceAdapter, DiscoveredRecord
from backend.app.services.discovery.openstreetmap import OpenStreetMapAdapter
from backend.app.services.discovery.search_engine import SearchEngineAdapter
from backend.app.services.discovery.directories import DirectoryAdapter, CSVImportAdapter
from backend.app.services.discovery.google_maps import GoogleMapsAdapter
from backend.app.services.discovery.ai_search import AISearchAdapter
from backend.app.services.discovery.intent_hunter import SocialIntentAdapter

class SourceRegistry:
    def __init__(self):
        self._adapters: Dict[str, LeadSourceAdapter] = {
            "OpenStreetMap": OpenStreetMapAdapter(),
            "GoogleMaps": GoogleMapsAdapter(),
            "AISearch": AISearchAdapter(),
            "SocialIntent": SocialIntentAdapter(),
            "SearchEngine": SearchEngineAdapter(),
            "PublicDirectory": DirectoryAdapter(),
            "CSVImport": CSVImportAdapter(),
        }

    def get_adapter(self, name: str) -> Optional[LeadSourceAdapter]:
        return self._adapters.get(name)

    def list_sources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "type": adapter.__class__.__name__,
                "enabled": True,
            }
            for name, adapter in self._adapters.items()
        ]

    async def run_discovery(
        self,
        sources: List[str],
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit_per_source: int = 30
    ) -> List[DiscoveredRecord]:
        combined_records: List[DiscoveredRecord] = []
        clean_sources = [s.strip() for s in sources if s.strip() and s.strip() in self._adapters]
        if not clean_sources:
            clean_sources = ["OpenStreetMap"]

        tasks = []
        for source_name in clean_sources:
            adapter = self._adapters.get(source_name)
            if adapter:
                tasks.append(
                    adapter.discover(
                        query=query,
                        location=location,
                        industry=industry,
                        limit=limit_per_source
                    )
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, list):
                combined_records.extend(res)
            elif isinstance(res, Exception):
                print(f"Discovery source error: {res}")

        return combined_records

    async def check_all_health(self) -> Dict[str, Any]:
        results = {}
        for name, adapter in self._adapters.items():
            try:
                results[name] = await adapter.health_check()
            except Exception as e:
                results[name] = {"status": "ERROR", "error": str(e)}
        return results

source_registry = SourceRegistry()

