import re, requests, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
H = {"User-Agent": "Mozilla/5.0 (RadarDeEditais; coleta semanal sem fins comerciais)"}
URLS = sys.argv[1:]
K = re.compile(r"edital|chamada|inscri|programa|oportunidade|sele|startup|inova|desafio|premio|\.pdf", re.I)
for u in URLS:
    print("=" * 30, u)
    try:
        r = requests.get(u, headers=H, timeout=25)
        print("status", r.status_code, "final", r.url, "tipo", r.headers.get("content-type"), "tamanho", len(r.text))
        s = BeautifulSoup(r.text, "html.parser")
        print("title:", s.title.get_text(strip=True) if s.title else None)
        n = 0
        for a in s.find_all("a", href=True):
            t = a.get_text(" ", strip=True); h = urljoin(r.url, a["href"])
            if K.search(t + " " + h):
                print(f"  [{t[:110]}] {h[:150]}"); n += 1
                if n >= 70: break
        if n == 0:
            print("  sem links relevantes; trecho:", re.sub(r"\s+", " ", s.get_text(" "))[:400])
    except Exception as e:
        print("erro", e)
