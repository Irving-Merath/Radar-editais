import re, requests, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
H = {"User-Agent": "Mozilla/5.0 (RadarDeEditais; coleta semanal sem fins comerciais)"}
K = re.compile(r"edital|chamada|call|\.pdf", re.I)
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
            if n >= 25: break
        if n == 0: print("  nada; trecho:", re.sub(r"\s+", " ", s.get_text(" "))[:300])
    except Exception as e:
        print("erro", type(e).__name__, str(e)[:150])
