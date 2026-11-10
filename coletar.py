
#!/usr/bin/env python3
"""Coleta semanal de editais de inovação (roda grátis no GitHub Actions).

Lê páginas de órgãos de fomento e buscas de notícias, classifica cada
oportunidade por palavras-chave e atualiza o arquivo editais.json.
Para incluir uma fonte nova, basta acrescentar um item em FONTES_HTML.
"""
import sys, json, re, hashlib, unicodedata, datetime as dt, html as htmllib
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, quote_plus, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

ARQUIVO = "editais.json"
HOJE = dt.date.today()
HEADERS = {"User-Agent": "Mozilla/5.0 (RadarDeEditais; coleta semanal sem fins comerciais)"}
MAX_POR_FONTE = 15

# Páginas oficiais. Confira se os endereços continuam válidos de tempos em tempos.
# O robô lê os links da página, ignora menus e resultados, entra em cada anúncio
# e salva o link da página/PDF do edital (não o da notícia).
FONTES_HTML = [
    {"orgao": "FAPERJ", "url": "https://www.faperj.br/", "ufs": ["RJ"]},
    {"orgao": "Finep", "url": "http://www.finep.gov.br/chamadas-publicas", "ufs": []},
    {"orgao": "AgeRio", "url": "https://www.agerio.com.br/", "ufs": ["RJ"]},
    {"orgao": "Petrobras", "url": "https://conexoes-inovacao.petrobras.com.br/", "ufs": []},
    {"orgao": "Embrapii", "url": "https://embrapii.org.br/chamadas/", "ufs": []},
    {"orgao": "Sebrae Startups", "url": "https://programas.sebraestartups.com.br/", "ufs": []},
    {"orgao": "FAPESP", "url": "https://fapesp.br/oportunidades", "ufs": ["SP"]},
    {"orgao": "FAPEMIG", "url": "https://fapemig.br/", "ufs": ["MG"]},
]

# Buscas no Bing (RSS gratuito).
# - BUSCAS (notícias): a notícia é só uma pista; o robô abre a matéria e procura
#   o link do edital oficial. Sem edital, a notícia é descartada.
# - BUSCAS_WEB (resultados da web): costumam cair direto na página do edital.
# Para cobrir outro estado, copie as linhas do RJ trocando o nome do estado/órgãos.
BUSCAS = [
    "edital inovação startups",
    "CPSI contrato público para solução inovadora",
    "encomenda tecnológica edital",
    "chamada pública subvenção econômica inovação",
    "edital negócios de impacto socioambiental",
    "desafio inovação aberta startups prova de conceito",
    "edital fomento não reembolsável inovação",
    "programa de inovação inscrições abertas startups",
    # Rio de Janeiro
    "edital inovação Rio de Janeiro inscrições abertas",
    "Prefeitura do Rio edital startups inovação",
    "Sebrae RJ edital inovação",
    "Firjan Senai edital inovação",
    "Governo do Estado do Rio de Janeiro chamada pública inovação",
    "AgeRio edital inovação",
]
BUSCAS_WEB = [
    "edital inovação inscrições abertas 2026",
    "chamada pública inovação startups inscrições abertas",
    "edital CPSI startups inscrições",
    "Finep chamada pública aberta",
    "BNDES chamada pública inovação inscrições",
    "Embrapii chamada pública empresas",
    # Rio de Janeiro
    "edital inovação \"Rio de Janeiro\" inscrições abertas",
    "FAPERJ edital inscrições abertas empresas startups",
    "Prefeitura do Rio de Janeiro edital inovação startups",
    "Sebrae RJ edital startups",
    "Firjan Senai edital inovação inscrições",
    "edital empreendedorismo \"Rio de Janeiro\" inscrições",
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


UF_DOMINIO = re.compile(r"\.(ac|al|ap|am|ba|ce|df|es|go|ma|mt|ms|mg|pa|pb|pr|pe|pi|rj|rn|rs|ro|rr|sc|sp|se|to)\.gov\.br$|"
                        r"\.rio$|faperj|agerio")


def uf_do_dominio(link):
    m = UF_DOMINIO.search(urlparse(link or "").netloc.lower())
    if not m:
        return set()
    return {m.group(1).upper()} if m.group(1) else {"RJ"}


def classificar(titulo, corpo, ufs_padrao=None, link="", resumo=""):
    original = f"{titulo}\n{resumo}\n{corpo}"
    t = normalizar(original)
    # Região: só o título, o resumo e o começo do texto, para menus e rodapés
    # (que citam vários estados) não contaminarem a classificação.
    t_regiao = normalizar(f"{titulo}\n{resumo}\n{(corpo or '')[:3000]}")
    t_curto = normalizar(f"{titulo}\n{resumo}")
    segmentos = [s for s, kws in SEG_KW.items() if tem(t, kws)]
    tipo = next((k for k, kws in TIPO_KW if tem(t, kws)), "fomento")
    proponentes = [p for p, kws in PROP_KW.items() if tem(t, kws)]
    ufs = {uf for uf, rx in UF_RE.items() if re.search(rx, t_regiao)} | set(ufs_padrao or []) | uf_do_dominio(link)
    if len(ufs) > 3 and not ufs_padrao:  # cita muitos estados: provavelmente vale para o país todo
        ufs = uf_do_dominio(link)
    ufs = sorted(ufs)
    if INTERNACIONAL.search(t_curto) and not ufs_padrao:
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


def dominio(url):
    return urlparse(url or "").netloc.lower().replace("www.", "")


# ---------------------------------------------------------------- filtros de qualidade
# Notícias que não são oportunidade aberta (resultados, eventos, balanços…).
RUIDO = re.compile(r"resultado|foram selecionad|sao selecionad|lista de selecionad|aprovados|homologa|"
                   r"contemplad|vencedor|premiados|classificados|inscricoes encerradas|encerrad|saem os|"
                   r"balanco|seminario|palestra|webinar|workshop|entrevista|opiniao|retrospectiva|"
                   r"visita|assinam|assina acordo|posse|nomead|cerimonia|exposicao", re.I)
# Links de menu: títulos curtos e genéricos que apontam para listas, não para um edital.
MENU = re.compile(r"^ ?(acoes e programas|programas|editais|chamadas|chamadas e editais|chamadas publicas|"
                  r"editais abertos|chamadas abertas|oportunidades|explorar chamadas|ver todos|ver todas|"
                  r"todos os editais|todas as chamadas|saiba mais|leia mais|clique aqui|programas e editais|"
                  r"editais e chamadas|editais encerrados|chamadas encerradas|resultados) ?$")
DOMINIOS_IGNORADOS = re.compile(r"facebook|instagram|twitter|x\.com|linkedin|youtube|youtu\.be|whatsapp|wa\.me|"
                                r"t\.me|telegram|threads\.net|addtoany|neoflip|pinterest|reddit|tiktok|flipboard|"
                                r"google\.|bing\.|msn\.com|mailto:|sharer|share\?|/share|intent/|"
                                r"susep\.gov\.br|globo\.com/(?!.*edital)", re.I)
ARQUIVO_NAO_EDITAL = re.compile(r"\.(jpe?g|png|gif|webp|svg|mp4|mp3|zip|css|js)(\?|$)", re.I)
SINAL_EDITAL = re.compile(r"edital|chamada|inscri|regulamento|cpsi|encomenda|selecao|programa|desafio|premio|"
                          r"call|apply|candidat|submiss|oportunidade", re.I)
SINAL_FORTE = re.compile(r"edital|chamada|regulamento|inscric|inscreva|formulario|submiss", re.I)
OFICIAL = re.compile(r"\.gov\.br|\.org\.br|\.edu\.br|\.jus\.br|\.leg\.br|\.rio$|fap|finep|sebrae|bndes|firjan|senai|"
                     r"petrobras|prosas|embrapii|cnpq|capes|fiocruz|fundacao|instituto|agerio", re.I)
NUMERO_EDITAL = re.compile(r"\b(\d{1,3})\s?/\s?(20\d\d)\b")


def eh_ruido(titulo):
    """True para links de menu, notícias de resultado/evento e editais de anos passados."""
    t = normalizar(titulo)
    if MENU.match(t) or RUIDO.search(t):
        return True
    anos = [int(a) for a in re.findall(r"\b(20\d\d)\b", t)]
    return bool(anos) and max(anos) < HOJE.year


def link_valido(href):
    return href.startswith("http") and not DOMINIOS_IGNORADOS.search(href) and not ARQUIVO_NAO_EDITAL.search(href)


def conteudo_principal(sopa, lista=False):
    """Tira menus, cabeçalho e rodapé; devolve o bloco principal da página.
    Em páginas de lista (lista=True) não usa <article>, que costuma ser só o 1º item."""
    for tag in sopa(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    for tag in sopa.select("[class*=menu], [id*=menu], [class*=navbar], [class*=rodape], [id*=rodape], "
                           "[class*=footer], [class*=share], [class*=social], [class*=breadcrumb]"):
        tag.decompose()
    if lista:
        return sopa.find("main") or sopa.find(attrs={"role": "main"}) or sopa.body or sopa
    return sopa.find("article") or sopa.find("main") or sopa.find(attrs={"role": "main"}) or sopa.body or sopa


def ler_pagina(url):
    """Abre a página. Devolve (url_final, sopa_principal, resumo, texto) ou None se não for HTML."""
    try:
        r = baixar(url)
    except Exception as e:
        print("  não abriu", url, e)
        return None
    if "html" not in r.headers.get("content-type", ""):
        return r.url, None, "", ""
    sopa = BeautifulSoup(r.text, "html.parser")
    meta = sopa.find("meta", attrs={"name": "description"}) or sopa.find("meta", attrs={"property": "og:description"})
    resumo = (meta.get("content", "") if meta else "").strip()
    principal = conteudo_principal(sopa)
    if not resumo:
        resumo = next((p.get_text(" ", strip=True) for p in principal.find_all("p")
                       if len(p.get_text(strip=True)) > 80), "")
    return r.url, principal, resumo[:280], principal.get_text(" ", strip=True)[:20000]


def texto_da_pagina(url):
    """Resumo e texto do edital para achar prazo e público. PDFs ficam só com o título."""
    lido = ler_pagina(url)
    if not lido or lido[1] is None:
        return "", ""
    return lido[2], lido[3]


def escolher_link_edital(principal, url_pagina, titulo, ignorar=frozenset()):
    """Dentro do conteúdo de um anúncio, escolhe o link que mais parece ser o edital.

    `ignorar` são links que aparecem na página de origem (menus do site), descartados aqui.
    Devolve (link, nota). Nota 0 = nada parecido com edital.
    """
    dom_pagina = dominio(url_pagina)
    pagina_oficial = bool(OFICIAL.search(dom_pagina))
    numeros = {f"{n}/{a}" for n, a in NUMERO_EDITAL.findall(titulo or "")}
    melhor, melhor_nota = None, 0
    for a in principal.find_all("a", href=True):
        href = urljoin(url_pagina, a["href"]).split("#")[0]
        if not link_valido(href) or href in ignorar or href.rstrip("/") == url_pagina.rstrip("/"):
            continue
        texto_a = a.get_text(" ", strip=True)
        texto = normalizar(texto_a + " " + href)
        if not SINAL_EDITAL.search(texto) or MENU.match(normalizar(texto_a)) and not href.lower().endswith(".pdf"):
            continue
        if RUIDO.search(normalizar(texto_a)):
            continue
        dom = dominio(href)
        nota = 1
        if SINAL_FORTE.search(texto):
            nota += 3
        if href.lower().endswith(".pdf"):
            nota += 2
        if OFICIAL.search(dom):
            nota += 3
        elif not pagina_oficial and dom != dom_pagina:
            nota += 1
        if dom == dom_pagina and not pagina_oficial:
            nota -= 3  # em site de notícia, link interno é outra matéria
        if numeros and any(n in normalizar(texto_a + " " + href).replace(" ", "") for n in numeros):
            nota += 3
        if nota > melhor_nota:
            melhor, melhor_nota = href, nota
    return melhor, melhor_nota


def montar_item(titulo, orgao, link, anuncio, fonte, resumo_reserva="", ufs_padrao=None, corpo_reserva=""):
    resumo, corpo = texto_da_pagina(link) if link != anuncio else ("", "")
    item = {"id": gerar_id(link), "titulo": titulo[:200], "orgao": orgao, "link": link,
            "resumo": resumo or resumo_reserva[:280], "adicionado_em": HOJE.isoformat(), "fonte": fonte}
    item["anuncio"] = anuncio or link
    item.update(classificar(titulo, corpo or corpo_reserva, ufs_padrao, link, item["resumo"]))
    return item


def resolver_anuncio(titulo, url, ignorar=frozenset(), aceitar_propria=False):
    """Abre um anúncio e devolve (link_do_edital, resumo, texto_do_anuncio).

    Em site oficial, se não houver link melhor e a própria página tiver cara de edital,
    a própria página é a publicação do edital (aceitar_propria=True).
    """
    lido = ler_pagina(url)
    if not lido:
        return None, "", ""
    url_final, principal, resumo, texto = lido
    if principal is None:  # o link já é um PDF/arquivo: é o próprio edital
        return url_final, "", ""
    link, nota = escolher_link_edital(principal, url_final, titulo, ignorar)
    if link and nota >= 5:
        return link, resumo, texto
    if aceitar_propria and OFICIAL.search(dominio(url_final)) and SINAL_FORTE.search(normalizar(titulo + " " + texto[:3000])):
        return url_final, resumo, texto
    return None, resumo, texto


# ---------------------------------------------------------------- coletores
def coletar_html(fonte, conhecidos):
    novos = []
    try:
        r = baixar(fonte["url"])
    except Exception as e:
        print("Falha em", fonte["orgao"], e)
        return novos
    sopa = BeautifulSoup(r.text, "html.parser")
    # Links de menu do site (dentro de nav/rodapé ou com texto curto/genérico) se repetem em todas
    # as páginas; ao abrir um anúncio, eles são ignorados na hora de achar o edital.
    menus_links = set()
    for bloco in sopa.select("nav, header, footer, [class*=menu], [id*=menu], [class*=footer], [class*=rodape]"):
        menus_links |= {urljoin(r.url, a["href"]).split("#")[0] for a in bloco.find_all("a", href=True)}
    ignorar = set(menus_links)
    for a in sopa.find_all("a", href=True):
        texto = a.get_text(" ", strip=True)
        if len(texto) < 15 or MENU.match(normalizar(texto)):
            ignorar.add(urljoin(r.url, a["href"]).split("#")[0])
    principal = conteudo_principal(sopa, lista=True)
    vistos = set()
    for a in principal.find_all("a", href=True):
        titulo = a.get_text(" ", strip=True)
        link = urljoin(r.url, a["href"]).split("#")[0]
        if link in vistos or link in menus_links or not link_valido(link):
            continue
        vistos.add(link)
        if len(titulo) < 15 or not OPORTUNIDADE.search(normalizar(titulo)) or eh_ruido(titulo):
            continue
        if gerar_id(link) in conhecidos or gerar_id(titulo) in conhecidos:
            continue
        edital, resumo, texto = resolver_anuncio(titulo, link, ignorar - {link}, aceitar_propria=True)
        if not edital:
            print("  sem edital, descartado:", titulo[:70])
            continue
        uid = gerar_id(edital)
        if uid in conhecidos:
            continue
        conhecidos |= {uid, gerar_id(titulo), gerar_id(link)}
        item = montar_item(titulo, fonte["orgao"], edital, link, "html:" + fonte["orgao"],
                           resumo, fonte["ufs"], texto)
        novos.append(item)
        print("  ok:", titulo[:60], "→", edital)
        if len(novos) >= MAX_POR_FONTE:
            break
    print(fonte["orgao"], "→", len(novos), "novos")
    return novos


def link_real_bing(link):
    """O Bing embrulha o endereço da matéria em apiclick.aspx?url=...; aqui ele é desembrulhado."""
    q = parse_qs(urlparse(link).query)
    return q.get("url", [link])[0]


def itens_rss(url):
    raiz = ET.fromstring(baixar(url).content)
    for it in raiz.iter("item"):
        titulo = (it.findtext("title") or "").strip()
        desc = BeautifulSoup(htmllib.unescape(it.findtext("description") or ""), "html.parser").get_text(" ", strip=True)
        yield titulo, desc, link_real_bing(it.findtext("link") or "")


def coletar_busca(busca, conhecidos, web=False):
    """Notícias (web=False) ou resultados da web (web=True) do Bing → link do edital oficial."""
    caminho = "search" if web else "news/search"
    url = f"https://www.bing.com/{caminho}?q={quote_plus(busca)}&format=rss&setlang=pt-BR&cc=BR&mkt=pt-BR"
    novos = []
    try:
        resultados = list(itens_rss(url))
    except Exception as e:
        print("Falha na busca", busca, e)
        return novos
    for titulo, desc, pagina in resultados:
        t = normalizar(titulo + " " + (desc if web else ""))
        if not (OPORTUNIDADE.search(t) and INOVACAO.search(t)) or eh_ruido(titulo) or not link_valido(pagina):
            continue
        if gerar_id(titulo) in conhecidos or gerar_id(pagina) in conhecidos:
            continue
        conhecidos |= {gerar_id(titulo), gerar_id(pagina)}
        oficial = bool(OFICIAL.search(dominio(pagina)))
        # Em site oficial, a própria página pode ser a publicação do edital.
        edital, resumo, texto = resolver_anuncio(titulo, pagina, aceitar_propria=oficial)
        if not edital:
            print("  sem link de edital, descartada:", titulo[:70])
            continue
        uid = gerar_id(edital)
        if uid in conhecidos:
            continue
        conhecidos.add(uid)
        origem = ("web:" if web else "noticia:") + dominio(pagina)
        item = montar_item(titulo, dominio(edital), edital, pagina, origem, resumo or desc, None, texto)
        novos.append(item)
        print("  ok:", titulo[:60], "→", edital)
    print("Busca", "web" if web else "notícias", ":", busca, "→", len(novos), "novos")
    return novos


def coletar_noticias(busca, conhecidos):
    return coletar_busca(busca, conhecidos, web=False)


def item_ruim(i):
    """Itens antigos que não passam nos filtros atuais (menus, resultados, links de compartilhamento)."""
    link = i.get("link") or ""
    if i.get("fonte") == "exemplo" or "news.google.com" in link or "google.com/search" in link:
        return True
    if not link_valido(link) or eh_ruido(i.get("titulo", "")):
        return True
    # Notícias de órgão salvas sem o link do edital (coletas antigas).
    return i.get("fonte", "").startswith("html:") and "anuncio" not in i


def main():
    try:
        with open(ARQUIVO, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        dados = {"editais": []}
    itens = dados["editais"] if isinstance(dados, dict) else dados
    itens = [i for i in itens if not item_ruim(i)]
    conhecidos = {i["id"] for i in itens} | {gerar_id(i["titulo"]) for i in itens}

    novos = []
    if "--so-limpar" not in sys.argv:
        for fonte in FONTES_HTML:
            novos += coletar_html(fonte, conhecidos)
        for busca in BUSCAS:
            novos += coletar_busca(busca, conhecidos, web=False)
        for busca in BUSCAS_WEB:
            novos += coletar_busca(busca, conhecidos, web=True)
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
