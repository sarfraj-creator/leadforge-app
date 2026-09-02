import asyncio
import httpx
import time

OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"
HTTP_HEADERS = {"User-Agent": "LeadForge/2.0 (B2B Lead Discovery Platform; contact@leadforge.internal)"}

# Global regions covering Americas, Europe, Asia, Oceania
GLOBAL_BBOXES = [
    ("London & UK", "(51.2,-0.5,51.7,0.3)"),
    ("New York & US East", "(40.5,-74.3,41.0,-73.6)"),
    ("San Francisco & US West", "(37.6,-122.6,37.9,-122.3)"),
    ("Paris & France", "(48.7,2.1,49.0,2.6)"),
    ("Tokyo & Japan", "(35.5,139.5,35.8,139.9)"),
    ("Sydney & Australia", "(-34.0,151.0,-33.7,151.4)"),
    ("Berlin & Germany", "(52.4,13.2,52.6,13.6)"),
    ("Singapore", "(1.2,103.6,1.5,104.0)"),
]

async def test_fast_multi_region():
    total_elements = []
    t_start = time.time()
    
    for name, bbox in GLOBAL_BBOXES:
        ql = f"""
        [out:json][timeout:15];
        (
          node["amenity"="restaurant"]["website"]{bbox};
          node["amenity"="restaurant"]["phone"]{bbox};
        );
        out center 25;
        """
        try:
            t0 = time.time()
            async with httpx.AsyncClient(timeout=10.0, headers=HTTP_HEADERS) as client:
                res = await client.post(OVERPASS_ENDPOINT, data={"data": ql})
                if res.status_code == 200:
                    elems = res.json().get("elements", [])
                    print(f"Region {name}: {len(elems)} elements in {time.time()-t0:.2f}s")
                    total_elements.extend(elems)
        except Exception as e:
            print(f"Region {name} error: {e}")

    print(f"\nTotal discovered elements: {len(total_elements)} in {time.time()-t_start:.2f}s")
    for el in total_elements[:5]:
        print(f" - {el.get('tags', {}).get('name')} | Website: {el.get('tags', {}).get('website')}")

if __name__ == "__main__":
    asyncio.run(test_fast_multi_region())
