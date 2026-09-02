import asyncio
import httpx
import time

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.openstreetmap.ru/cgi/interpreter",
]

HEADERS = {"User-Agent": "LeadForge/2.0 (B2B Lead Discovery Platform; contact@leadforge.internal)"}

async def test():
    ql = """
    [out:json][timeout:20];
    node["amenity"="restaurant"]["website"](51.48,-0.18,51.53,-0.08);
    out center 30;
    """
    for m in MIRRORS:
        try:
            t0 = time.time()
            async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
                res = await client.post(m, data={"data": ql})
                print(f"Mirror {m} -> Status: {res.status_code} in {time.time()-t0:.2f}s")
                if res.status_code == 200:
                    elems = res.json().get("elements", [])
                    print(f"Success! {len(elems)} elements retrieved from {m}")
                    for el in elems[:3]:
                        print(" -", el.get("tags", {}).get("name"), el.get("tags", {}).get("website"))
        except Exception as e:
            print(f"Mirror {m} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
