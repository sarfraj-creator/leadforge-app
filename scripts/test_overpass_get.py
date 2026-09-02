import urllib.request
import urllib.parse
import json
import time

def test_get():
    ql = '[out:json][timeout:15];node["amenity"="restaurant"]["website"](51.48,-0.18,51.53,-0.08);out center 30;'
    url = f"https://overpass-api.de/api/interpreter?data={urllib.parse.quote(ql)}"
    print(f"Querying: {url[:80]}...")
    req = urllib.request.Request(url, headers={"User-Agent": "LeadForge-Discovery/2.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            data = json.loads(res.read().decode('utf-8'))
            elems = data.get('elements', [])
            print(f"GET Success! Got {len(elems)} elements in {time.time()-t0:.2f}s")
            for el in elems[:5]:
                print(" -", el.get('tags', {}).get('name'), "| Web:", el.get('tags', {}).get('website'))
    except Exception as e:
        print("GET Failed:", e)

if __name__ == "__main__":
    test_get()
