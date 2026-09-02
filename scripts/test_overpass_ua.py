import asyncio
import httpx
import time

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

HEADERS = {
    "User-Agent": "LeadForge/2.0 (B2B Lead Discovery Platform; contact@leadforge.internal)"
}

async def test():
    ql = """
    [out:json][timeout:25];
    (
      node["amenity"="restaurant"]["website"](51.45,-0.25,51.55,0.0);
      node["amenity"="restaurant"]["website"](40.7,-74.05,40.8,-73.9);
    );
    out center 60;
    """
    for ep in OVERPASS_ENDPOINTS:
        try:
            t0 = time.time()
            async with httpx.AsyncClient(timeout=20.0, headers=HEADERS) as client:
                res = await client.post(ep, data={"data": ql})
                elapsed = time.time() - t0
                print(f"Endpoint {ep} -> Status: {res.status_code} in {elapsed:.2f}s")
                if res.status_code == 200:
                    data = res.json()
                    elements = data.get("elements", [])
                    print(f"Elements count: {len(elements)}")
                    for el in elements[:3]:
                        print(" -", el.get("tags", {}).get("name"), "| Website:", el.get("tags", {}).get("website"))
                    return
        except Exception as e:
            print(f"Error {ep}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
