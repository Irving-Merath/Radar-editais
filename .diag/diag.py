import re, json, requests, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import xml.etree.ElementTree as ET
H = {"User-Agent": "Mozilla/5.0 (RadarDeEditais; coleta semanal sem fins comerciais)"}
K = re.compile(r"call|challenge|prize|grant|opportunit|convocatoria|edital|chamada|apply|funding|\.pdf", re.I)

print("=" * 20, "EU SEDIA API", flush=True)
try:
    q = {"bool": {"must": [{"terms": {"type": ["1", "2", "8"]}}, {"terms": {"status": ["31094501", "31094502"]}}]}}
    files = {"query": ("blob", json.dumps(q), "application/json"),
             "languages": ("blob", json.dumps(["en"]), "application/json"),
             "sort": ("blob", json.dumps({"field": "sortStatus", "order": "ASC"}), "application/json")}
    r = requests.post("https://api.tech.ec.europa.eu/search-api/prod/rest/search?apiKey=SEDIA&text=***&pageSize=10&pageNumber=1",
                      files=files, headers=H, timeout=30)
    print("status", r.status_code, "tam", len(r.text))
    d = r.json(); print("total", d.get("totalResults"))
    for it in d.get("results", [])[:10]:
        md = it.get("metadata", {})
        print("  -", (md.get("title") or [it.get("content")])[0][:90], "|", md.get("identifier"), "|", md.get("deadlineDate"), "|", it.get("url"))
    if d.get("results"): print("  chaves metadata:", sorted(d["results"][0].get("metadata", {}).keys())[:60])
except Exception as e:
    print("erro", type(e).__name__, str(e)[:200])

for q, lang, cc in [("open call startups Latin America", "en", "US"), ("startup challenge applications open Brazil", "en", "US"),
                    ("convocatoria startups América Latina", "es", "MX"), ("grant call innovation Latin America applications", "en", "US")]:
    print("=" * 20, "Bing RSS", q, flush=True)
    try:
        r = requests.get(f"https://www.bing.com/news/search?q={quote_plus(q)}&format=rss&setlang={lang}&cc={cc}", headers=H, timeout=20)
        raiz = ET.fromstring(r.content); its = list(raiz.iter("item"))
        print("itens", len(its))
        for it in its[:6]: print("  -", (it.findtext("title") or "")[:100])
    except Exception as e:
        print("erro", type(e).__name__, str(e)[:150])

for u in sys.argv[1:]:
    print("=" * 20, u, flush=True)
    try:
        r = requests.get(u, headers=H, timeout=20)
        s = BeautifulSoup(r.text, "html.parser")
        print("status", r.status_code, "final", r.url, "tam", len(r.text), "title:", s.title.get_text(strip=True)[:80] if s.title else None)
        n, vistos = 0, set()
        for a in s.find_all("a", href=True):
            t = a.get_text(" ", strip=True); h = urljoin(r.url, a["href"])
            if h in vistos or len(t) < 12 or not K.search(t + " " + h): continue
            vistos.add(h); print(f"  [{t[:100]}] {h[:140]}"); n += 1
            if n >= 20: break
        if n == 0: print("  nada; trecho:", re.sub(r"\s+", " ", s.get_text(" "))[:300])
    except Exception as e:
        print("erro", type(e).__name__, str(e)[:150])
