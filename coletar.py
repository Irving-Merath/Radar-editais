
#!/usr/bin/env python3
"""Coleta semanal de editais de inovação (roda grátis no GitHub Actions).

Lê páginas de órgãos de fomento e buscas de notícias, classifica cada
oportunidade por palavras-chave e atualiza o arquivo editais.json.
Para incluir uma fonte nova, basta acrescentar um item em FONTES_HTML.
"""
import json, re, hashlib, unicodedata, datetime as dt, html as htmllib
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, quote_plus, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

ARQUIVO = "editais.json"
HOJE = dt.date.today()
HEADERS = {"User-Agent": "Mozilla/5.0 (RadarDeEditais; coleta semanal sem fins comerciais)"}
MAX_POR_FONTE = 15

# Páginas oficiais. Confira se os endereços continuam válidos de tempos em tempos.
FONTES_HTML = [
    {"orgao": "FAPERJ", "url": "https://www.faperj.br/", "ufs": ["RJ"]},
    {"orgao": "Finep", "url": "http://www.finep.gov.br/chamadas-publicas", "ufs": []},
    {"orgao": "AgeRio", "url": "https://www.agerio.com.br/", "ufs": ["RJ"]},
    {"orgao": "FAPESP", "url": "https://fapesp.br/oportunidades", "ufs": ["SP"]},
    {"orgao": "FAPEMIG", "url": "https://fapemig.br/", "ufs": ["MG"]},
]

# Buscas no Bing Notícias (RSS gratuito). A notícia serve só como pista:
# o robô abre a matéria, procura o link do edital oficial e salva esse link.
# Se não achar o edital, a notícia é descartada.
BUSCAS = [
    "edital inovação startups",
    "CPSI contrato público para solução inovadora",
    "encomenda tecnológica edital",
    "chamada pública subvenção econômica inovação",
    "edital negócios de impacto socioambiental",
    "desafio inovação aberta startups prova de conceito",
    "edital fomento não reembolsável inovação",
    "programa de inovação inscrições abertas startups",
]

OPORTUNIDADE = re.compile(r"edital|chamada|cpsi|encomenda tecnol|desafio|premio|programa|selecao|inscric|open call|aceleracao|grant", re.I)
INOVACAO = re.compile(r"inova|startup|tecnolog|impacto|pesquisa|cpsi|empreend|ciencia", re.I)

SEG_KW = {
    "bigdata": ["big data", "ciencia de dados", "analise de dados", "dados abertos", "analytics"],
    "ia": ["inteligencia artificial", " ia ", "machine learning", "aprendizado de maquina", "ia generativa", " ai "],
    "visao": ["visao computacional", "computer vision", "reconhecimento de imagem", "processamento de imagens"],
    "iot": [" iot ", "internet das coisas", "sensores", "sensor "],
    "educacao": ["educacao", "ensino", "escola", "aprendizagem", "edtech"],
    "cultura": ["cultura", "cultural", "economia criativa", "audiovisual", " artes "],
    "residuos": ["residuos", "reciclagem", "economia circular", " lixo", "coleta seletiva"],
    "saude": ["saude", "hospital", " sus ", "healthtech", "medic", "clinic"],
    "logistica": ["logistica", "mobilidade", "transporte", "cadeia de suprimentos", "frete"],
    "agro": ["agro", "agricultura", "alimentos", "agtech", " rural"],
    "energia": ["energia", " solar", "eolica", "hidrogenio"],
    "clima": ["clima", "carbono", "meio ambiente", "ambiental", "sustentab", "biodiversidade", "floresta", "amazonia"],
    "cidades": ["cidades inteligentes", "smart cit", "gestao publica", "govtech", "urbano", "saneamento"],
    "financas": ["fintech", "financas", "inclusao financeira", "credito", "pagamento"],
    "social": ["impacto social", "socioambiental", "vulnerab", "comunidade", "periferia", "diversidade"],
}
TIPO_KW = [  # a ordem importa: o primeiro que aparecer define o tipo
    ("cpsi", ["cpsi", "contrato publico para solucao inovadora", "solucao inovadora", "lei complementar 182", "marco legal das startups"]),
    ("etec", ["encomenda tecnologica", " etec "]),
    ("poc", ["prova de conceito", " poc ", "inovacao aberta", "open innovation", "desafio"]),
    ("aceleracao", ["aceleracao", "incubacao", "pre-aceleracao", "accelerator"]),
    ("premio", ["premio", "premiacao", " award"]),
]
PROP_KW = {
    "cpf": ["pessoa fisica", " cpf ", "pesquisador", "estudante", "bolsa", "bolsista"],
    "mei": [" mei ", "microempreendedor"],
    "startup": ["startup", " empresa", "micro e pequena", " pme", "base tecnologica"],
    "osc": [" osc ", " ong ", "sociedade civil", "negocio de impacto", "negocios de impacto", "associac", "cooperativa"],
    "parceria": ["consorcio", "parceria", "em rede", " ict ", "cooperacao", "coexecutor"],
}
UF_RE = {
    "AC": r"\bacre\b|\bfapac\b", "AL": r"\balagoas\b|\bfapeal\b", "AP": r"\bamapa\b|\bfapeap\b",
    "AM": r"\bamazonas\b|\bmanaus\b|\bfapeam\b", "BA": r"\bbahia\b|\bfapesb\b", "CE": r"\bceara\b|\bfuncap\b",
    "DF": r"distrito federal|\bfapdf\b", "ES": r"espirito santo|\bfapes\b", "GO": r"\bgoias\b|\bfapeg\b",
    "MA": r"\bmaranhao\b|\bfapema\b", "MT": r"mato grosso\b(?! do sul)|\bfapemat\b", "MS": r"mato grosso do sul|\bfundect\b",
    "MG": r"minas gerais|\bfapemig\b", "PA": r"estado do para\b|\bparaense\b|\bfapespa\b", "PB": r"\bparaiba\b|\bfapesq\b",
    "PR": r"\bparana\b|fundacao araucaria", "PE": r"\bpernambuco\b|\bfacepe\b", "PI": r"\bpiaui\b|\bfapepi\b",
    "RJ": r"rio de janeiro|\bfluminense\b|\bfaperj\b|\bagerio\b", "RN": r"rio grande do norte|\bfapern\b",
    "RS": r"rio grande do sul|\bfapergs\b", "RO": r"\brondonia\b|\bfapero\b", "RR": r"\broraima\b|\bfaperr\b",
    "SC": r"santa catarina|\bfapesc\b", "SP": r"sao paulo|\bpaulista\b|\bfapesp\b", "SE": r"\bsergipe\b|\bfapitec\b",
    "TO": r"\btocantins\b|\bfapt\b",
}
INTERNACIONAL = re.compile(r"internacional|international|global|worldwide|america latina|latin america", re.I)
MESES = {m: i + 1 for i, m in enumerate(["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho",
                                          "agosto", "setembro", "outubro", "novembro", "dezembro"])}


def normalizar(t):
    t = unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode().lower()
    return " " + re.sub(r"[^a-z0-9/]+", " ", t) + " "


def tem(texto, palavras):
    return any(p in texto for p in palavras)


def achar_prazo(texto):
    """Procura datas futuras perto de palavras como 'inscrições até' ou 'prazo'."""
    achados = []
    for m in re.finditer(r"(\d{1,2})/(\d{1,2})/(\d{4})", texto):
        achados.append((m.start(), m.group(1), m.group(2), m.group(3)))
    for m in re.finditer(r"(\d{1,2}) de (" + "|".join(MESES) + r") de (\d{4})", texto):
        achados.append((m.start(), m.group(1), MESES[m.group(2)], m.group(3)))
    datas = []
    for pos, d, mth, a in achados:
        try:
            data = dt.date(int(a), int(mth), int(d))
        except ValueError:
            continue
        perto = texto[max(0, pos - 90):pos]
        if HOJE <= data <= HOJE + dt.timedelta(days=400) and re.search(r"inscri|prazo|submiss|ate |encerra|limite|deadline", perto):
            datas.append(data)
    return min(datas).isoformat() if datas else None


def achar_valor(texto_original):
    m = re.search(r"(R\$|US\$|€)\s?[\d.,]+\s?(milh[õo]es|milh[ãa]o|bilh[õo]es|mil)?", texto_original or "", re.I)
    return m.group(0).strip() if m else ""


def classificar(titulo, corpo, ufs_padrao=None):
    original = f"{titulo}\n{corpo}"
    t = normalizar(original)
    segmentos = [s for s, kws in SEG_KW.items() if tem(t, kws)]
    tipo = next((k for k, kws in TIPO_KW if tem(t, kws)), "fomento")
    proponentes = [p for p, kws in PROP_KW.items() if tem(t, kws)]
    ufs = sorted({uf for uf, rx in UF_RE.items() if re.search(rx, t)} | set(ufs_padrao or []))
    if INTERNACIONAL.search(t) and not ufs_padrao:
        abrangencia, ufs = "internacional", []
    elif ufs:
        abrangencia = "regional"
    else:
        abrangencia = "nacional"
    return {"tipo": tipo, "segmentos": segmentos, "proponentes": proponentes,
            "abrangencia": abrangencia, "ufs": ufs, "prazo": achar_prazo(t), "valor": achar_valor(original)}


def gerar_id(chave):
    return hashlib.sha1(normalizar(chave).encode()).hexdigest()[:12]


def baixar(url):
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r


def texto_da_pagina(url):
    """Abre o edital para ler resumo, prazo e público. PDFs ficam só com o título."""
    try:
        r = baixar(url)
        if "html" not in r.headers.get("content-type", ""):
            return "", ""
        sopa = BeautifulSoup(r.text, "html.parser")
        for tag in sopa(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        meta = sopa.find("meta", attrs={"name": "description"})
        resumo = meta.get("content", "") if meta else ""
        if not resumo:
            p = next((p.get_text(" ", strip=True) for p in sopa.find_all("p") if len(p.get_text(strip=True)) > 80), "")
            resumo = p
        return resumo[:280], sopa.get_text(" ", strip=True)[:20000]
    except Exception as e:
        print("  não abriu", url, e)
        return "", ""


def coletar_html(fonte, conhecidos):
    novos = []
    try:
        sopa = BeautifulSoup(baixar(fonte["url"]).text, "html.parser")
    except Exception as e:
        print("Falha em", fonte["orgao"], e)
        return novos
    for a in sopa.find_all("a", href=True):
        titulo = a.get_text(" ", strip=True)
        link = urljoin(fonte["url"], a["href"])
        if len(titulo) < 15 or not OPORTUNIDADE.search(normalizar(titulo)):
            continue
        uid = gerar_id(link)
        if uid in conhecidos:
            continue
        conhecidos.add(uid)
        resumo, corpo = texto_da_pagina(link)
        item = {"id": uid, "titulo": titulo[:200], "orgao": fonte["orgao"], "link": link, "resumo": resumo,
                "adicionado_em": HOJE.isoformat(), "fonte": "html:" + fonte["orgao"]}
        item.update(classificar(titulo, corpo, fonte["ufs"]))
        novos.append(item)
        if len(novos) >= MAX_POR_FONTE:
            break
    print(fonte["orgao"], "→", len(novos), "novos")
    return novos


DOMINIOS_IGNORADOS = re.compile(r"facebook|instagram|twitter|x\.com|linkedin|youtube|whatsapp|t\.me|"
                                r"google\.|bing\.|tiktok|flipboard|msn\.com|globo\.com/(?!.*edital)", re.I)
SINAL_EDITAL = re.compile(r"edital|chamada|inscri|regulamento|cpsi|encomenda|selecao|programa|desafio|premio|"
                          r"call|apply|candidat|submiss", re.I)
OFICIAL = re.compile(r"\.gov\.br|\.org\.br|\.edu\.br|\.jus\.br|\.leg\.br|fap|finep|sebrae|bndes|"
                     r"prosas|embrapii|cnpq|capes|fundacao|instituto", re.I)


def link_real_bing(link):
    """O Bing embrulha o endereço da matéria em apiclick.aspx?url=...; aqui ele é desembrulhado."""
    q = parse_qs(urlparse(link).query)
    return q.get("url", [link])[0]


def achar_link_do_edital(url_materia):
    """Abre a matéria e escolhe o link que mais parece ser o edital oficial."""
    try:
        r = baixar(url_materia)
    except Exception as e:
        print("  matéria não abriu", url_materia, e)
        return None, ""
    sopa = BeautifulSoup(r.text, "html.parser")
    corpo_materia = sopa.get_text(" ", strip=True)[:20000]
    dominio_materia = urlparse(r.url).netloc.replace("www.", "")
    melhor, melhor_nota = None, 0
    for a in sopa.find_all("a", href=True):
        href = urljoin(r.url, a["href"])
        if not href.startswith("http") or DOMINIOS_IGNORADOS.search(href):
            continue
        dominio = urlparse(href).netloc.replace("www.", "")
        texto = normalizar(a.get_text(" ", strip=True) + " " + href)
        nota = 0
        if dominio and dominio != dominio_materia:
            nota += 2
        if OFICIAL.search(dominio):
            nota += 3
        if SINAL_EDITAL.search(texto):
            nota += 3
        if href.lower().endswith(".pdf"):
            nota += 2
        if nota > melhor_nota:
            melhor, melhor_nota = href, nota
    # Exige pelo menos: domínio externo + cara de edital (nota 5) para não salvar link qualquer.
    return (melhor if melhor_nota >= 5 else None), corpo_materia


def coletar_noticias(busca, conhecidos):
    url = f"https://www.bing.com/news/search?q={quote_plus(busca)}&format=rss&setlang=pt-BR&cc=BR"
    novos = []
    try:
        raiz = ET.fromstring(baixar(url).content)
    except Exception as e:
        print("Falha na busca", busca, e)
        return novos
    for it in raiz.iter("item"):
        titulo = (it.findtext("title") or "").strip()
        desc = BeautifulSoup(htmllib.unescape(it.findtext("description") or ""), "html.parser").get_text(" ", strip=True)
        t = normalizar(titulo)
        if not (OPORTUNIDADE.search(t) and INOVACAO.search(t)):
            continue
        uid_titulo = gerar_id(titulo)
        if uid_titulo in conhecidos:
            continue
        conhecidos.add(uid_titulo)
        materia = link_real_bing(it.findtext("link") or "")
        link, corpo_materia = achar_link_do_edital(materia)
        if not link:
            print("  sem link de edital, descartada:", titulo[:70])
            continue
        uid = gerar_id(link)
        if uid in conhecidos:
            continue
        conhecidos.add(uid)
        resumo, corpo_edital = texto_da_pagina(link)
        item = {"id": uid, "titulo": titulo[:200], "orgao": urlparse(link).netloc.replace("www.", ""),
                "link": link, "resumo": resumo or desc[:280], "adicionado_em": HOJE.isoformat(),
                "fonte": "noticia:" + urlparse(materia).netloc.replace("www.", "")}
        item.update(classificar(titulo, corpo_edital or corpo_materia))
        novos.append(item)
        print("  ok:", titulo[:60], "→", link)
    print("Busca:", busca, "→", len(novos), "novos")
    return novos


def main():
    try:
        with open(ARQUIVO, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        dados = {"editais": []}
    itens = dados["editais"] if isinstance(dados, dict) else dados
    conhecidos = {i["id"] for i in itens} | {gerar_id(i["titulo"]) for i in itens}

    novos = []
    for fonte in FONTES_HTML:
        novos += coletar_html(fonte, conhecidos)
    for busca in BUSCAS:
        novos += coletar_noticias(busca, conhecidos)

    # Exemplos fictícios e itens antigos sem link de edital saem a cada coleta.
    itens = [i for i in itens if i.get("fonte") != "exemplo"
             and "news.google.com" not in (i.get("link") or "")
             and "google.com/search" not in (i.get("link") or "")]
    itens += novos

    limite_prazo = (HOJE - dt.timedelta(days=90)).isoformat()
    limite_sem_prazo = (HOJE - dt.timedelta(days=180)).isoformat()
    itens = [i for i in itens if (i.get("prazo") or "9999") >= limite_prazo
             and (i.get("prazo") or i.get("adicionado_em", "9999") >= limite_sem_prazo)]
    itens.sort(key=lambda i: i.get("adicionado_em", ""), reverse=True)

    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump({"atualizado_em": HOJE.isoformat(), "editais": itens}, f, ensure_ascii=False, indent=1)
    print(f"Total: {len(itens)} oportunidades ({len(novos)} novas)")


if __name__ == "__main__":
    main()
