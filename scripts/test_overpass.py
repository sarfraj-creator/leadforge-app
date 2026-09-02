import asyncio
import httpx
import time

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

async def test_query():
    # Test global Overpass query
    ql = """
    [out:json][timeout:25];
    (
      node["amenity"="restaurant"]["website"](30.0,-125.0,50.0,-70.0);
      node["amenity"="restaurant"]["website"](40.0,-10.0,60.0,30.0);
    );
    out center 60;
    """
    for ep in OVERPASS_ENDPOINTS:
        t0 = time.time()
        print(f"Testing endpoint {ep}...")
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(ep, data={"data": ql})
                elapsed = time.time() - t0
                print(f"Endpoint {ep} returned HTTP {res.status_code} in {elapsed:.2f}s")
                if res.status_code == 200:
                    data = res.json()
                    elements = data.get("elements", [])
                    print(f"Found {len(elements)} elements!")
                    if elements:
                        print("Sample element:", elements[0].get("tags", {}).get("name"), elements[0].get("tags", {}).get("website"))
                    return
        except Exception as e:
            print(f"Error for {ep}: {e}")

if __name__ == "__main__":
    asyncio.run(test_query())
