import urllib.request
import urllib.parse
import json
import time

MIRRORS = [
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

QL = '[out:json][timeout:15];node["amenity"="restaurant"]["website"](51.48,-0.18,51.53,-0.08);out center 30;'

def test_mirrors():
    for m in MIRRORS:
        try:
            url = f"{m}?data={urllib.parse.quote(QL)}"
            req = urllib.request.Request(url, headers={"User-Agent": "LeadForge/2.0 (B2B Lead Discovery)"})
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=8) as res:
                data = json.loads(res.read().decode('utf-8'))
                elems = data.get('elements', [])
                print(f"Mirror {m} -> SUCCESS! Got {len(elems)} elements in {time.time()-t0:.2f}s")
                for el in elems[:2]:
                    print("  -", el.get('tags', {}).get('name'), "|", el.get('tags', {}).get('website'))
        except Exception as e:
            print(f"Mirror {m} -> Error: {e}")

if __name__ == "__main__":
    test_mirrors()
