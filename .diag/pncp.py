import json, requests
H = {"User-Agent": "Mozilla/5.0 (RadarDeEditais; coleta semanal sem fins comerciais)", "Accept": "application/json"}
def mostra(nome, url, params):
    print("=" * 15, nome, flush=True)
    try:
        r = requests.get(url, params=params, headers=H, timeout=40)
        print("status", r.status_code, r.url[:200], "tam", len(r.text))
        d = r.json()
        if isinstance(d, dict):
            print("chaves:", list(d.keys())[:20])
            itens = d.get("items") or d.get("data") or d.get("resultado") or []
            print("total:", d.get("total") or d.get("totalRegistros"), "itens nesta página:", len(itens))
            for it in itens[:8]:
                print("  -", json.dumps(it, ensure_ascii=False)[:700])
        else:
            print(str(d)[:500])
    except Exception as e:
        print("erro", type(e).__name__, str(e)[:300])
S = "https://pncp.gov.br/api/search/"
for q in ["CPSI", "\"solução inovadora\"", "\"contrato público para solução inovadora\"", "\"Lei Complementar 182\""]:
    mostra("search " + q, S, {"q": q, "tipos_documento": "edital", "ordenacao": "-data", "pagina": 1, "tam_pagina": 10, "status": "recebendo_proposta"})
mostra("search CPSI sem status", S, {"q": "CPSI", "tipos_documento": "edital", "ordenacao": "-data", "pagina": 1, "tam_pagina": 5})
C = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"
for mod in [3, 10, 12]:
    mostra(f"consulta proposta modalidade {mod}", C, {"dataFinal": "20271231", "codigoModalidadeContratacao": mod, "pagina": 1, "tamanhoPagina": 10})
