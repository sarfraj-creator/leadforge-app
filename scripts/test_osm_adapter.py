import asyncio
import time
from backend.app.services.discovery.openstreetmap import OpenStreetMapAdapter

async def main():
    adapter = OpenStreetMapAdapter()
    print("Testing adapter health_check()...")
    health = await adapter.health_check()
    print("Health:", health)

    print("\nTesting adapter discover(location='WORLDWIDE', industry='restaurant', limit=60)...")
    t0 = time.time()
    records = await adapter.discover(query="restaurant", location="WORLDWIDE", industry="restaurant", limit=60)
    elapsed = time.time() - t0
    print(f"\nDiscovered {len(records)} real records in {elapsed:.2f}s!")
    for r in records[:5]:
        print(f" - [{r.source_record_id}] {r.business_name} ({r.city}, {r.country}) | Web: {r.website} | URL: {r.source_url}")

if __name__ == "__main__":
    asyncio.run(main())
