import urllib.request
import urllib.parse
import json
import time

URLS = [
    "http://overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

QL = """
[out:json][timeout:15];
(
  node["amenity"="restaurant"]["website"](51.48,-0.18,51.53,-0.08);
);
out center 25;
"""

def test():
    data = urllib.parse.urlencode({"data": QL}).encode("utf-8")
    for u in URLS:
        try:
            req = urllib.request.Request(
                u,
                data=data,
                headers={"User-Agent": "LeadForge/2.0 (contact@leadforge.dev)"}
            )
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=12) as response:
                body = response.read().decode("utf-8")
                res = json.loads(body)
                elems = res.get("elements", [])
                print(f"URL: {u} -> Success! {len(elems)} elements in {time.time()-t0:.2f}s")
                if elems:
                    print("Sample:", elems[0].get("tags", {}).get("name"), elems[0].get("tags", {}).get("website"))
                return
        except Exception as e:
            print(f"URL: {u} -> Failed: {e}")

if __name__ == "__main__":
    test()
