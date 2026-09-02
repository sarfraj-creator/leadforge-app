import asyncio
import httpx
import time

OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"
HTTP_HEADERS = {"User-Agent": "LeadForge/2.0 (B2B Lead Discovery Platform; contact@leadforge.internal)"}

async def test():
    # Focused multi-continent query
    ql = """
    [out:json][timeout:30];
    (
      node["amenity"="restaurant"]["website"](51.45,-0.20,51.55,0.0);
      node["amenity"="restaurant"]["website"](40.70,-74.05,40.80,-73.90);
      node["amenity"="restaurant"]["website"](48.80,2.25,48.90,2.40);
    );
    out center 100;
    """
    t0 = time.time()
    async with httpx.AsyncClient(timeout=30.0, headers=HTTP_HEADERS) as client:
        res = await client.post(OVERPASS_ENDPOINT, data={"data": ql})
        elapsed = time.time() - t0
        print(f"Status: {res.status_code} in {elapsed:.2f}s")
        if res.status_code == 200:
            elems = res.json().get("elements", [])
            print(f"Total returned elements: {len(elems)}")
            for el in elems[:10]:
                tags = el.get("tags", {})
                print(f" - {tags.get('name')} | City: {tags.get('addr:city', 'Global')} | Web: {tags.get('website')}")

if __name__ == "__main__":
    asyncio.run(test())
