
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
    {"orgao": "AgeRio", "url": "https://www.agerio.com.br/", "ufs": ["RJ"]},
    {"orgao": "Centelha RJ", "url": "https://rj.programacentelha.com.br/", "ufs": ["RJ"]},
    {"orgao": "InovAtiva", "url": "https://inovativa.online/painel-de-oportunidades/", "ufs": []},
    {"orgao": "FAPESP PIPE", "url": "https://fapesp.br/pipe", "ufs": ["SP"]},
    {"orgao": "FACEPE", "url": "https://www.facepe.br/editais/todos/?c=aberto", "ufs": ["PE"]},
    {"orgao": "FAPES", "url": "https://fapes.es.gov.br/editais-abertos", "ufs": ["ES"]},
    {"orgao": "FAPERGS", "url": "https://fapergs.rs.gov.br/chamadas-e-editais", "ufs": ["RS"]},
    {"orgao": "CNPq", "url": "https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao", "ufs": [],
     "sem_sublistas": True},  # as outras listas do CNPq descrevem programas, não chamadas abertas
    # Confap: a página de cada chamada reúne o edital e as regras de cada FAP; ela é o link salvo.
    {"orgao": "Confap", "url": "https://confap.org.br/pt/editais", "ufs": [], "abrangencia": "internacional",
     "link_proprio": True},
]
# Agências estrangeiras: só entram chamadas que citam Brasil, América Latina ou chamada global ("exige").
LATAM = r"brasil|brazil|latin america|america latina|latinoamerica|latam|south america|global south|sul global|global call|worldwide|open to all|any country"
FONTES_HTML += [
    {"orgao": "IDRC (Canadá)", "url": "https://idrc-crdi.ca/en/funding", "ufs": [], "abrangencia": "internacional",
     "exige": r"brasil|brazil|latin america|america latina|latinoamerica|south america|caribbean", "sem_sublistas": True, "exige_prazo": True},
    {"orgao": "Governo do Reino Unido", "url": "https://www.gov.uk/international-development-funding", "ufs": [],
     "abrangencia": "internacional", "exige": r"brasil|brazil|latin america|america latina|south america", "sem_sublistas": True},
    # XPRIZE: competições globais, abertas a equipes de qualquer país. Os títulos são curtos ("Water Scarcity"),
    # então os links são reconhecidos pelo endereço.
    {"orgao": "XPRIZE", "url": "https://www.xprize.org/competitions?status=Active", "ufs": [], "abrangencia": "internacional",
     "padrao_link": r"xprize\.org/competitions/[a-z0-9-]+$", "link_proprio": True, "sem_sublistas": True,
     "exige_prazo": True},  # a lista também mostra competições já encerradas
]
# FAPs de SC, CE, DF e PR têm certificado de segurança incompleto (o robô não acessa sem
# desligar a verificação, o que não é seguro); FAPEMIG, Finep e Sebrae dependem de JavaScript.
# Finep, FAPEMIG, Prosas e Sebrae Startups montam a lista de editais com JavaScript (o robô não
# consegue ler); a Finep entra pelas buscas de notícias. O site do BNDES recusa conexões do GitHub.

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
    "FAPERJ edital inscrições",
    "FAPERJ lança edital",
    "Finep chamada pública",
    "BNDES inscrições abertas startups",
    "Sebrae edital startups inscrições",
    "chamada pública inovação empresas inscrições",
    "programa de aceleração startups inscrições abertas",
    "edital startups inscrições abertas",
    # Internacional
    "chamada internacional startups brasileiras inscrições",
    "programa internacional aceleração startups Brasil inscrições abertas",
    "edital cooperação internacional inovação empresas brasileiras",
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

OPORTUNIDADE = re.compile(r"edital|chamada|cpsi|encomenda tecnol|desafio|premio|programa|selecao|seleciona|inscric|"
                          r"open call|aceleracao|acelerar|grant|vagas|propostas|concorrer|subvencao|convocatoria|call for|challenge|"
                          r"prize|accelerator|aceleradora|applications|funding", re.I)
INOVACAO = re.compile(r"inova|startup|tecnolog|impacto|pesquisa|cpsi|empreend|ciencia|finep|bndes|faperj|fapesp|"
                      r"sebrae|embrapii|sustentab|acelera|negocio|subvencao|empresa|industria|digital", re.I)

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
    # CPSI só com menção explícita: a Lei Complementar 182 (Marco Legal das Startups) e "solução inovadora"
    # aparecem também em editais de fomento e aceleração (ex.: Centelha).
    ("cpsi", [" cpsi ", "contrato publico para solucao inovadora", "contratos publicos para solucao inovadora",
              "contrato publico para solucoes inovadoras"]),
    ("etec", ["encomenda tecnologica", " etec "]),
    ("aceleracao", ["centelha", "ideacao", "pre aceleracao"]),  # programas para startups em ideação/validação
    ("poc", ["prova de conceito", " poc ", "inovacao aberta", "open innovation", "desafio"]),
    ("aceleracao", ["aceleracao", "incubacao", "pre-aceleracao", "accelerator"]),
    ("premio", ["premio", "premiacao", " award"]),
]
PROP_KW = {
    "cpf": ["pessoa fisica", " cpf ", "pesquisador", "estudante", "bolsa", "bolsista", "researcher", "investigador",
            "individual", "fellowship"],
    "mei": [" mei ", "microempreendedor"],
    "startup": ["startup", " empresa", "micro e pequena", " pme", "base tecnologica", " sme", " smes ", "compan",
                "enterprise", "emprendedor"],
    "osc": [" osc ", " ong ", "sociedade civil", "negocio de impacto", "negocios de impacto", "associac", "cooperativa",
            " ngo", "civil society", "non profit", "nonprofit", "sociedad civil"],
    "parceria": ["consorcio", "parceria", "em rede", " ict ", "cooperacao", "coexecutor", "consortium", "partnership",
                 "partners", "cooperation", "consorcio"],
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
INTERNACIONAL = re.compile(r"internacional|international|transnacional|global|worldwide|america latina|latin america|"
                           r"uniao europeia|europa|horizon|cooperacao bilateral|brasil suecia|reino unido|"
                           r"alemanha|franca|espanha|portugal|belgica|canada|estados unidos|japao|china", re.I)
MESES = {m: i + 1 for i, m in enumerate(["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho",
                                          "agosto", "setembro", "outubro", "novembro", "dezembro"])}
# Meses em espanhol e inglês (chamadas estrangeiras), já sem acento.
MESES.update({m: i + 1 for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                                              "agosto", "septiembre", "octubre", "noviembre", "diciembre"])})
MESES_EN = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july",
                                            "august", "september", "october", "november", "december"])}


def normalizar(t):
    t = unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode().lower()
    return " " + re.sub(r"[^a-z0-9/]+", " ", t) + " "


def tem(texto, palavras):
    return any(p in texto for p in palavras)


def achar_prazo(texto):
    """Procura datas perto de palavras como 'inscrições até' ou 'prazo'.

    Devolve a data futura mais próxima. Se só houver datas passadas, devolve a mais recente:
    assim um edital já encerrado fica marcado como encerrado (e sai do site depois de 90 dias)."""
    achados = []
    for m in re.finditer(r"(\d{1,2})/(\d{1,2})/(\d{4})", texto):
        achados.append((m.start(), m.group(1), m.group(2), m.group(3)))
    for m in re.finditer(r"(\d{1,2}) de (" + "|".join(MESES) + r") de (\d{4})", texto):
        achados.append((m.start(), m.group(1), MESES[m.group(2)], m.group(3)))
    meses_en = "|".join(MESES_EN)
    for m in re.finditer(r"\b(" + meses_en + r") (\d{1,2})(?:st|nd|rd|th)? (\d{4})", texto):  # February 15 2027
        achados.append((m.start(), m.group(2), MESES_EN[m.group(1)], m.group(3)))
    for m in re.finditer(r"(\d{1,2}) (" + meses_en + r") (\d{4})", texto):  # 15 February 2027
        achados.append((m.start(), m.group(1), MESES_EN[m.group(2)], m.group(3)))
    datas, passadas = [], []
    for pos, d, mth, a in achados:
        try:
            data = dt.date(int(a), int(mth), int(d))
        except ValueError:
            continue
        perto = texto[max(0, pos - 90):pos]
        if not re.search(r"inscri|prazo|submiss|ate |encerra|limite|deadline|until|closes|closing|apply by|due|"
                         r"hasta|cierre|plazo|fecha limite", perto):
            continue
        if HOJE <= data <= HOJE + dt.timedelta(days=400):
            datas.append(data)
        elif HOJE - dt.timedelta(days=400) <= data < HOJE:
            passadas.append(data)
    if datas:
        return min(datas).isoformat()
    return max(passadas).isoformat() if passadas else None


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
    # Tipo pelo título, resumo e começo do texto (onde fica o objeto do edital), não pelo documento inteiro.
    t_tipo = normalizar(f"{titulo}\n{resumo}\n{(corpo or '')[:8000]}")
    tipo = next((k for k, kws in TIPO_KW if tem(t_tipo, kws)), "fomento")
    proponentes = [p for p, kws in PROP_KW.items() if tem(t, kws)]
    if ufs_padrao:  # fonte de um estado (ex.: FAPERJ): vale para esse estado
        ufs = set(ufs_padrao) | uf_do_dominio(link)
    else:
        ufs = {uf for uf, rx in UF_RE.items() if re.search(rx, t_regiao)} | uf_do_dominio(link)
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
                   r"visita|assinam|assina acordo|posse|nomead|cerimonia|exposicao|"
                   r"eliminacao de doc|licitacao|pregao|concurso publico|processo seletivo simplificado|"
                   r"contratacao de pessoal|aviso de|errata|como submeter|manual|tutorial|perguntas frequentes|faq|"
                   r"graduacao|vestibular|vagas para curso|adendo|lista de espera|enquadramento|convocacao|"
                   r"rerratifica|prorrogacao|prorrogad|novo prazo|novo cronograma|prestacao de contas|"
                   # documentos de apoio de uma chamada (não são o edital em si)
                   r"^ ?anexo|anexo [ivx]+\b|modelo|termo de adesao|diretrizes fapes|^ ?divulgacao|announcement|"
                   r"formulario|plano de trabalho|cronograma|enquadrad|premiad|agraciad|anunciados|lista |"
                   r"fornecedores|dispensa|rodada de submiss|publicacao confap|aditivo|minuta|busca de chamadas|"
                   r"a submissao de propostas|conselho nacional das fundacoes|saiba mais|sobre o programa", re.I)
# Vagas de bolsa em projetos acadêmicos (ex.: "Bolsa de PD em Química") não são editais de inovação.
BOLSA_ACADEMICA = re.compile(r"^ ?bolsas? de (pd|pos doutorado|mestrado|doutorado|ic|iniciacao|tt |tt i|jp|"
                             r"treinamento tecnico)")
# Links de menu: títulos curtos e genéricos que apontam para listas, não para um edital.
MENU = re.compile(r"^ ?(acoes e programas|programas|editais|chamadas|chamadas e editais|chamadas publicas|"
                  r"editais abertos|chamadas abertas|oportunidades|explorar chamadas|ver todos|ver todas|"
                  r"todos os editais|todas as chamadas|saiba mais|leia mais|clique aqui|programas e editais|"
                  r"editais e chamadas|editais encerrados|chamadas encerradas|resultados) ?$")
DOMINIOS_IGNORADOS = re.compile(r"facebook|instagram|twitter|x\.com|linkedin|youtube|youtu\.be|whatsapp|wa\.me|"
                                r"t\.me|telegram|threads\.net|addtoany|neoflip|pinterest|reddit|tiktok|flipboard|"
                                r"google\.|bing\.|msn\.com|mailto:|sharer|share\?|/share|intent/|"
                                r"susep\.gov\.br", re.I)
ARQUIVO_NAO_EDITAL = re.compile(r"\.(jpe?g|png|gif|webp|svg|mp4|mp3|zip|css|js|docx?|xlsx?|odt|ods|pptx?)(\?|$)", re.I)
SINAL_EDITAL = re.compile(r"edital|chamada|inscri|regulamento|cpsi|encomenda|selecao|programa|desafio|premio|"
                          r"call|apply|candidat|submiss|oportunidade", re.I)
SINAL_FORTE = re.compile(r"edital|chamada|regulamento|inscric|inscreva|formulario|submiss|call for|global call|"
                         r"convocatoria|grant|prize|challenge|apply|applications|open call|open-call", re.I)
OFICIAL = re.compile(r"(^|\.)(gov|org|edu|jus|leg)\.br$|\.gov\.br|\.rio$|fap|finep|sebrae|bndes|firjan|senai|"
                     r"petrobras|prosas|embrapii|cnpq|capes|fiocruz|fundacao|instituto|agerio|facepe|confap|"
                     r"europa\.eu|idrc|xprize|gov\.uk|ukri|\.gov$|\.int$|\.edu$", re.I)
# Endereços e títulos com cara de notícia: o robô não aceita uma notícia como "o edital".
URL_NOTICIA = re.compile(r"noticia|/news|imprensa|agencia|/materia|/blog|/artigo|/post/|/20\d\d/[01]\d/[0-3]\d/|"
                         r"faperj\.br/\?id=\d+\.7\.", re.I)
TITULO_NOTICIA = re.compile(r"\b(lanca|lancou|lancam|abre|abriu|anuncia|anunciou|divulga|divulgou|apresenta|"
                            r"recebe|prorroga|prorrogou|participa|aderiu|adesao|nesta (segunda|terca|quarta|quinta|"
                            r"sexta)|neste (sabado|domingo)|vai premiar|vai selecionar|seleciona|oferece|"
                            r"lanza|lanzo|anuncio|presenta|launches|launched|announces|opens)\b")
ARQUIVO_EDITAL = re.compile(r"pdf|msword|officedocument|opendocument", re.I)
# Páginas que pedem login/cadastro para ver o conteúdo não servem como "o edital".
URL_LOGIN = re.compile(r"login|signin|sign-in|/auth|/sso|cadastr|/entrar|/registr|account|minha-conta|"
                       r"/sage/?$|sisfaperj|sigfapes|@@search|searchabletext|/busca|buscador", re.I)
NUMERO_EDITAL = re.compile(r"\b(\d{1,3})\s?/\s?(20\d\d)\b")


def parece_noticia(url, titulo=""):
    return bool(URL_NOTICIA.search(url or "")) or bool(TITULO_NOTICIA.search(normalizar(titulo)))


def eh_ruido(titulo):
    """True para links de menu, notícias de resultado/evento e editais de anos passados."""
    t = normalizar(titulo)
    if MENU.match(t) or RUIDO.search(t) or BOLSA_ACADEMICA.match(t):
        return True
    anos = [int(a) for a in re.findall(r"\b(20\d\d)\b", t)]
    if anos and max(anos) < HOJE.year:
        return True
    # Número do edital de ano passado (ex.: "Edital 40/2025"), mesmo que o título cite uma data atual.
    anos_edital = [int(a) for _, a in NUMERO_EDITAL.findall(t.replace(" / ", "/"))]
    return bool(anos_edital) and max(anos_edital) < HOJE.year


def eh_pagina_inicial(href):
    """Página inicial de um site (ex.: programas.sebraestartups.com.br/) não é um edital."""
    u = urlparse(href)
    query_real = [k for k in parse_qs(u.query) if not k.startswith("utm_")]  # utm_* é só propaganda
    return u.path.strip("/") in ("", "pt", "pt-br", "index.html", "index.php", "home") and not query_real


def link_valido(href):
    return href.startswith("http") and not DOMINIOS_IGNORADOS.search(href) and not ARQUIVO_NAO_EDITAL.search(href)


def link_antigo(href):
    """Arquivo com ano no endereço (ex.: /2018/...) anterior ao ano passado: edital velho."""
    u = urlparse(href)
    anos = [int(a) for a in re.findall(r"(?<!\d)(20\d\d)(?!\d)", u.path)]
    if anos and max(anos) < HOJE.year - 1:
        return True
    um_ano = HOJE - dt.timedelta(days=365)
    m = re.search(r"/(20\d\d)/(0[1-9]|1[0-2])/", u.path)  # pasta de upload, ex.: /wp-content/uploads/2025/02/
    if m and dt.date(int(m.group(1)), int(m.group(2)), 28) < um_ano:
        return True
    v = parse_qs(u.query).get("v", [""])[0]  # carimbo de envio em milissegundos (?v=1759164126000)
    if re.fullmatch(r"1\d{12}", v) and dt.date.fromtimestamp(int(v) / 1000) < um_ano:
        return True
    return False


def link_de_edital_valido(href):
    return (link_valido(href) and not eh_pagina_inicial(href) and not URL_LOGIN.search(href)
            and not link_antigo(href) and not re.search(r"resultado|errata|adendo|anexo", href, re.I))


def conteudo_principal(sopa, lista=False):
    """Tira menus, cabeçalho e rodapé; devolve o bloco principal da página.
    Em páginas de lista (lista=True) não usa <article>, que costuma ser só o 1º item."""
    for tag in sopa(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    # Blocos com classe "menu", "rodape" etc. só saem se forem pequenos: em vários sites de órgão
    # públicos a página inteira fica dentro de um <div class="...menu...">.
    total = len((sopa.body or sopa).get_text(" ", strip=True)) or 1
    for tag in sopa.select("[class*=menu], [id*=menu], [class*=navbar], [class*=rodape], [id*=rodape], "
                           "[class*=footer], [class*=share], [class*=social], [class*=breadcrumb]"):
        if not tag.decomposed and len(tag.get_text(" ", strip=True)) < 0.3 * total:
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
    tipo = r.headers.get("content-type", "")
    if "html" not in tipo:
        # Só PDF/documento conta como arquivo de edital; imagem, vídeo etc. são descartados.
        return (r.url, None, "", "") if ARQUIVO_EDITAL.search(tipo) or r.url.lower().endswith(".pdf") else None
    sopa = BeautifulSoup(r.text, "html.parser")
    titulo_pag = sopa.title.get_text(" ", strip=True) if sopa.title else ""
    anos = [int(a) for a in re.findall(r"(?<!\d)(20\d\d)(?!\d)", titulo_pag)]
    if anos and max(anos) < HOJE.year:
        print("  página de ano passado, ignorada:", titulo_pag[:70])
        return None
    if URL_LOGIN.search(r.url) or sopa.find("input", attrs={"type": "password"}):
        print("  pede login/cadastro, ignorada:", r.url)
        return None
    meta = sopa.find("meta", attrs={"name": "description"}) or sopa.find("meta", attrs={"property": "og:description"})
    resumo = (meta.get("content", "") if meta else "").strip()
    principal = conteudo_principal(sopa)
    if not resumo:
        resumo = next((p.get_text(" ", strip=True) for p in principal.find_all("p")
                       if len(p.get_text(strip=True)) > 80), "")
    return r.url, principal, resumo[:280], principal.get_text(" ", strip=True)[:20000]


def texto_pdf(url, paginas=8, limite_mb=15):
    """Texto das primeiras páginas de um PDF (para achar prazo e público). Vazio se não der."""
    try:
        from pypdf import PdfReader
        import io
        r = requests.get(url, headers=HEADERS, timeout=40, stream=True)
        r.raise_for_status()
        dados = r.raw.read(limite_mb * 1024 * 1024, decode_content=True)
        leitor = PdfReader(io.BytesIO(dados))
        return " ".join((pg.extract_text() or "") for pg in leitor.pages[:paginas])[:30000]
    except Exception as e:
        print("  PDF não lido", url[:90], type(e).__name__)
        return ""


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
        if not link_de_edital_valido(href) or href in ignorar or href.rstrip("/") == url_pagina.rstrip("/"):
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
        if href.lower().endswith((".pdf", ".doc", ".docx", ".odt")):
            nota += 3
        if URL_NOTICIA.search(href):
            nota -= 1  # notícia: só é usada como ponte (o robô entra nela e procura o edital)
        if OFICIAL.search(dom):
            nota += 3
        elif dom != dom_pagina:
            nota += 1  # link para fora: em notícia, costuma ser o edital; em comunicado oficial, a convocatória
        if dom == dom_pagina and not pagina_oficial:
            nota -= 3  # em site de notícia, link interno é outra matéria
        if numeros and any(n in normalizar(texto_a + " " + href).replace(" ", "") for n in numeros):
            nota += 3
        if nota > melhor_nota:
            melhor, melhor_nota = href, nota
    return melhor, melhor_nota


def montar_item(titulo, orgao, link, anuncio, fonte, resumo_reserva="", ufs_padrao=None, corpo_reserva=""):
    if link.lower().endswith(".pdf"):
        # PDF: as primeiras páginas do edital somam-se ao texto do anúncio (prazo e público).
        resumo, corpo = "", (corpo_reserva or "") + " " + texto_pdf(link)
    else:
        resumo, corpo = texto_da_pagina(link) if link != anuncio else ("", "")
    item = {"id": gerar_id(link), "titulo": titulo[:200], "orgao": orgao, "link": link,
            "resumo": resumo or resumo_reserva[:280], "adicionado_em": HOJE.isoformat(), "fonte": fonte}
    item["anuncio"] = anuncio or link
    item.update(classificar(titulo, corpo or corpo_reserva, ufs_padrao, link, item["resumo"]))
    return item


def pdfs_de_edital(principal, url_pagina, ignorar=frozenset()):
    """Todos os PDFs de edital citados num anúncio oficial (um anúncio pode lançar vários editais).
    Devolve [(texto_do_link, href)], usando o texto do link como título do edital."""
    achados = []
    for a in principal.find_all("a", href=True):
        href = urljoin(url_pagina, a["href"]).split("#")[0]
        texto = a.get_text(" ", strip=True)
        if (href.lower().split("?")[0].endswith(".pdf") and href not in ignorar and len(texto) >= 15
                and link_de_edital_valido(href)
                and re.search(r"edital|chamada", normalizar(texto)) and not eh_ruido(texto)
                and href not in [h for _, h in achados]):
            achados.append((texto, href))
    return achados


def resolver_anuncio(titulo, url, ignorar=frozenset(), aceitar_propria=False, nivel=0):
    """Abre um anúncio e devolve (link_do_edital, resumo, texto_do_anuncio, outros_pdfs).

    outros_pdfs: em site oficial, todos os PDFs de edital do anúncio [(título, link)].

    O link devolvido é sempre o edital (PDF ou página do edital/programa), nunca uma notícia:
    - se o melhor link achado ainda parece notícia, o robô entra nele e procura de novo (1 nível);
    - a própria página só é aceita (aceitar_propria=True) se for de site oficial e não tiver
      cara de notícia (endereço com /noticia/, título "FAPERJ lança…", etc.).
    """
    lido = ler_pagina(url)
    if not lido:
        return None, "", "", []
    url_final, principal, resumo, texto = lido
    if principal is None:  # o link já é um PDF/documento: é o próprio edital
        return url_final, "", "", []
    pdfs = pdfs_de_edital(principal, url_final, ignorar) if OFICIAL.search(dominio(url_final)) else []
    link, nota = escolher_link_edital(principal, url_final, titulo, ignorar)
    if nivel == 0 and not (link and nota >= 5):
        print(f"    melhor link em {url_final[:80]}: {link} (nota {nota})")
    if link and nota >= 5 and not link.lower().split("?")[0].endswith(".pdf") and nivel == 0 \
            and not ler_pagina(link):  # página do edital não abre, pede login ou é de ano passado
        link, nota = None, 0
    propria_ok = (aceitar_propria and OFICIAL.search(dominio(url_final)) and not parece_noticia(url_final, titulo)
                  and link_de_edital_valido(url_final) and SINAL_FORTE.search(normalizar(titulo + " " + texto[:3000])))
    if propria_ok and not (link and nota >= 5 and link.lower().split("?")[0].endswith(".pdf")):
        return url_final, resumo, texto, pdfs  # a própria página oficial é a publicação da chamada
    if link and nota >= 5:
        if not parece_noticia(link) or link.lower().endswith(".pdf"):
            return link, resumo, texto, pdfs
        if nivel == 0:
            mais, _, _, pdfs2 = resolver_anuncio(titulo, link, ignorar, aceitar_propria=False, nivel=1)
            if mais:
                return mais, resumo, texto, pdfs2
    if (aceitar_propria and OFICIAL.search(dominio(url_final)) and not parece_noticia(url_final, titulo)
            and link_de_edital_valido(url_final)
            and SINAL_FORTE.search(normalizar(titulo + " " + texto[:3000]))):
        return url_final, resumo, texto, pdfs
    return None, resumo, texto, pdfs


# ---------------------------------------------------------------- coletores
# Links de lista que valem a pena abrir dentro do site do órgão (ex.: "Editais abertos").
LISTA_EDITAIS = re.compile(r"^ ?(editais|chamadas|chamadas publicas|editais abertos|chamadas abertas|"
                           r"editais e chamadas|chamadas e editais|programas e editais|inscricoes abertas|"
                           r"oportunidades|oportunidades abertas|programas abertos|editais vigentes|"
                           r"chamadas vigentes|explorar chamadas|programas com inscricoes abertas|"
                           r"acoes e programas|programas|chamadas internacionais|chamamento publico|"
                           r"chamadas nacionais|editais abertos chamadas internacionais) ?$")
MAX_SUBLISTAS = 4


TEXTO_GENERICO = re.compile(r"^ ?(ver detalhes|detalhes|saiba mais|leia mais|acesse|acessar|ver mais|mais informacoes|"
                            r"clique aqui|confira|ver edital|ver chamada) ?$")


def titulo_do_card(a):
    """Para links "Ver detalhes": usa o título (h2/h3/h4/strong) do bloco em volta do link."""
    bloco = a
    for _ in range(4):
        bloco = bloco.parent
        if bloco is None:
            return ""
        h = bloco.find(["h1", "h2", "h3", "h4", "h5", "strong"])
        if h and len(h.get_text(strip=True)) >= 15:
            return h.get_text(" ", strip=True)
    return ""


def ler_lista(url):
    """Abre uma página de lista. Devolve (url_final, links, ignorar, sublistas, links_de_menu) ou None."""
    try:
        r = baixar(url)
    except Exception as e:
        print("  falha ao abrir", url, e)
        return None
    sopa = BeautifulSoup(r.text, "html.parser")
    def abs_(a):
        return urljoin(r.url, a["href"]).split("#")[0]
    # Links dentro de nav/cabeçalho/rodapé se repetem em todas as páginas: não são anúncios.
    menus_links = {abs_(a) for bloco in sopa.select("nav, header, footer") for a in bloco.find_all("a", href=True)}
    ignorar, sublistas = set(menus_links), []
    for a in sopa.find_all("a", href=True):
        texto, href = a.get_text(" ", strip=True), abs_(a)
        if len(texto) < 15 or MENU.match(normalizar(texto)):
            ignorar.add(href)
        if (LISTA_EDITAIS.match(normalizar(texto)) and dominio(href) == dominio(r.url)
                and href.rstrip("/") != r.url.rstrip("/") and href not in sublistas):
            sublistas.append(href)
    # Em páginas de lista, todos os links são lidos (os de menu caem nos filtros de título e de
    # nav/cabeçalho/rodapé): cortar blocos por classe fazia a lista de notícias sumir em alguns sites.
    # O mesmo endereço costuma aparecer em vários links (foto sem texto + título): fica o texto mais longo.
    melhores = {}
    for a in sopa.find_all("a", href=True):
        texto, href = a.get_text(" ", strip=True), abs_(a)
        if TEXTO_GENERICO.match(normalizar(texto)):
            texto = titulo_do_card(a) or texto
        if href not in melhores or len(texto) > len(melhores[href]):
            melhores[href] = texto
    links = [(t, h) for h, t in melhores.items()]
    return r.url, links, ignorar, sublistas, menus_links


def coletar_html(fonte, conhecidos):
    """Lê a página do órgão e as páginas de "Editais"/"Chamadas" ligadas a ela (1 nível)."""
    novos, visitadas = [], set()
    fila = [fonte["url"]]
    while fila and len(novos) < MAX_POR_FONTE:
        url = fila.pop(0)
        if url in visitadas:
            continue
        visitadas.add(url)
        lido = ler_lista(url)
        if not lido:
            continue
        url_final, links, ignorar, sublistas, menus_links = lido
        print(f"{fonte['orgao']}: {url_final} → {len(links)} links, {len(sublistas)} listas de editais")
        if url == fonte["url"] and not fonte.get("sem_sublistas"):
            fila += [u for u in sublistas if u not in visitadas][:MAX_SUBLISTAS]
        vistos, motivos = set(), {}
        for titulo, link in links:
            if link in vistos or link in visitadas or link in menus_links or not link_valido(link):
                continue
            if link.lower().split("?")[0].endswith(".pdf") and not link_de_edital_valido(link):
                continue
            vistos.add(link)
            n = normalizar(titulo)
            por_endereco = fonte.get("padrao_link") and re.search(fonte["padrao_link"], link)
            motivo = ("já conhecido" if por_endereco and gerar_id(link) in conhecidos else None) if por_endereco else (
                      "curto" if len(titulo) < 15 else "sem cara de oportunidade" if not OPORTUNIDADE.search(n)
                      else "ruído/resultado" if eh_ruido(titulo) else "lista" if LISTA_EDITAIS.match(n)
                      else "já conhecido" if gerar_id(link) in conhecidos or gerar_id(titulo) in conhecidos
                      else None)
            if motivo:
                motivos[motivo] = motivos.get(motivo, 0) + 1
                continue
            edital, resumo, texto, pdfs = resolver_anuncio(titulo, link, ignorar - {link},
                                                           aceitar_propria=not por_endereco)
            if por_endereco and texto:  # página da competição/chamada (ex.: XPRIZE)
                edital = edital or link
            if fonte.get("exige") and not re.search(fonte["exige"], normalizar(titulo + " " + resumo + " " + texto[:8000])):
                conhecidos |= {gerar_id(titulo), gerar_id(link)}
                print("  não cita Brasil/América Latina, ignorado:", titulo[:70])
                continue
            ja_vistos = {gerar_id(titulo), gerar_id(link)}  # marcados só depois de criar os itens
            # Um anúncio oficial pode lançar vários editais: cada PDF vira um item, com o nome do edital.
            achados = pdfs or ([(titulo, edital)] if edital else [])
            if fonte.get("link_proprio") and (edital or pdfs):
                achados = [(titulo, link)]
            # Link com texto genérico ("Clique aqui e leia o edital") fica com o título do anúncio.
            achados = [(re.sub(r"[_]+", " ", re.sub(r"\.pdf$", "", t, flags=re.I)), h) for t, h in achados]
            achados = [(titulo if re.match(r" ?(clique|acesse|leia|confira|baixe|veja|consulte|link|http|www)", normalizar(t))
                        else t, h) for t, h in achados]
            if not achados:
                conhecidos |= ja_vistos
                print("  sem edital, descartado:", titulo[:70])
                continue
            for titulo_edital, link_edital in achados:
                uid = gerar_id(link_edital)
                if uid in conhecidos:
                    continue
                conhecidos.add(uid)
                item = montar_item(titulo_edital, fonte["orgao"], link_edital, link, "html:" + fonte["orgao"],
                                   resumo, fonte["ufs"], texto)
                if fonte.get("exige_prazo") and not (item.get("prazo") and item["prazo"] >= HOJE.isoformat()):
                    print("  sem prazo de inscrição futuro, ignorado:", titulo_edital[:60])
                    continue
                if fonte.get("abrangencia"):  # ex.: Confap só publica chamadas internacionais
                    item["abrangencia"], item["ufs"] = fonte["abrangencia"], []
                novos.append(item)
                print("  ok:", titulo_edital[:60], "→", link_edital)
            conhecidos |= ja_vistos
            if len(novos) >= MAX_POR_FONTE:
                break
        print("  descartes por motivo:", motivos)
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


def busca_duckduckgo(busca):
    """Resultados da web pelo DuckDuckGo (versão HTML, sem chave). Usado quando o Bing não devolve nada."""
    r = requests.post("https://html.duckduckgo.com/html/", data={"q": busca, "kl": "br-pt"},
                      headers=HEADERS, timeout=25)
    r.raise_for_status()
    sopa = BeautifulSoup(r.text, "html.parser")
    for a in sopa.select("a.result__a"):
        href = a.get("href", "")
        if "uddg=" in href:
            href = parse_qs(urlparse(href).query).get("uddg", [href])[0]
        trecho = a.find_parent(class_="result")
        desc = trecho.select_one(".result__snippet").get_text(" ", strip=True) if trecho and trecho.select_one(".result__snippet") else ""
        yield a.get_text(" ", strip=True), desc, href


def coletar_busca(busca, conhecidos, web=False, idioma=("pt-BR", "BR")):
    """Notícias (web=False) ou resultados da web (web=True) do Bing → link do edital oficial."""
    # Notícias: RSS do Bing Notícias. Web: DuckDuckGo (o RSS de busca web do Bing ignora a pergunta
    # e devolve resultados aleatórios).
    novos = []
    try:
        if web:
            resultados = list(busca_duckduckgo(busca))
        else:
            lang, cc = idioma
            url = f"https://www.bing.com/news/search?q={quote_plus(busca)}&format=rss&setlang={lang}&cc={cc}"
            resultados = list(itens_rss(url))
    except Exception as e:
        print("Falha na busca", busca, e)
        resultados = []
    print(f"Busca {'web (DuckDuckGo)' if web else 'notícias (Bing)'}: {busca} → {len(resultados)} resultados")
    for titulo, desc, pagina in resultados:
        t = normalizar(titulo + " " + (desc if web else ""))
        if not link_valido(pagina):
            print("  site ignorado:", dominio(pagina), "|", titulo[:60])
            continue
        if not (OPORTUNIDADE.search(t) and INOVACAO.search(t)) or eh_ruido(titulo):
            print("  fora do tema/ruído:", titulo[:70])
            continue
        if gerar_id(titulo) in conhecidos or gerar_id(pagina) in conhecidos:
            continue
        conhecidos.add(gerar_id(titulo))
        oficial = bool(OFICIAL.search(dominio(pagina)))
        # Em site oficial, a própria página pode ser a publicação do edital.
        edital, resumo, texto, _ = resolver_anuncio(titulo, pagina, aceitar_propria=oficial)
        if not edital:
            conhecidos.add(gerar_id(pagina))
            print("  sem link de edital, descartada:", titulo[:70])
            continue
        uid = gerar_id(edital)
        if uid in conhecidos:
            continue
        conhecidos |= {uid, gerar_id(pagina)}
        origem = ("web:" if web else "noticia:") + dominio(pagina)
        item = montar_item(titulo, dominio(edital), edital, pagina, origem, resumo or desc, None, texto)
        novos.append(item)
        print("  ok:", titulo[:60], "→", edital)
    print("Busca", "web" if web else "notícias", ":", busca, "→", len(novos), "novos")
    return novos


# Notícias em espanhol e inglês sobre chamadas abertas a startups e pesquisadores da América Latina.
BUSCAS_EXTERIOR = [
    ("convocatoria startups América Latina", ("es", "MX")),
    ("convocatoria abierta innovación Latinoamérica", ("es", "MX")),
    ("aceleradora convocatoria startups latinoamericanas", ("es", "AR")),
    ("open call startups Latin America", ("en", "US")),
    ("challenge prize applications open Latin America innovation", ("en", "US")),
    ("grant call Brazil researchers international", ("en", "US")),
]


def coletar_ue(conhecidos):
    """Chamadas abertas da União Europeia (Horizon Europe e outros) que citam Brasil ou América Latina.

    Usa a API pública do portal Funding & Tenders (a página do portal depende de JavaScript)."""
    novos, vistos = [], set()
    filtro = re.compile(r"\bbrazil|\bbrasil|latin america|latin american|\blac\b|eu-lac|celac|south america|mercosur|"
                        r"caribbean|andean|amazon", re.I)
    # 31094501 = aberta, 31094502 = em breve (abre nos próximos meses, já com prazo definido)
    q = {"bool": {"must": [{"terms": {"type": ["1", "2", "8"]}}, {"terms": {"status": ["31094501", "31094502"]}}]}}
    arquivos = {"query": ("blob", json.dumps(q), "application/json"),
                "languages": ("blob", json.dumps(["en"]), "application/json")}
    total_lidas = citam = 0
    for pagina in range(1, 21):
        try:
            r = requests.post("https://api.tech.ec.europa.eu/search-api/prod/rest/search?apiKey=SEDIA"
                              f"&text=***&pageSize=100&pageNumber={pagina}", files=arquivos, headers=HEADERS, timeout=40)
            r.raise_for_status()
            resultados = r.json().get("results", [])
        except Exception as e:
            print("Falha na API da União Europeia, página", pagina, e)
            break
        if not resultados:
            break
        total_lidas += len(resultados)
        for res in resultados:
            md = res.get("metadata", {})
            ident = (md.get("identifier") or [""])[0]
            titulo = (md.get("title") or [res.get("content") or ""])[0]
            link = res.get("url") or ""
            if not ident or ident in vistos or not link or gerar_id(link) in conhecidos:
                continue
            vistos.add(ident)
            desc = BeautifulSoup(" ".join(md.get("description", [])), "html.parser").get_text(" ", strip=True)
            # A menção à América Latina pode estar em qualquer campo (descrição, destino, condições...).
            todo_texto = BeautifulSoup(json.dumps(md, ensure_ascii=False), "html.parser").get_text(" ")
            if not filtro.search(todo_texto):
                continue  # só chamadas que citam Brasil ou América Latina
            citam += 1
            prazos = sorted(d[:10] for d in md.get("deadlineDate", []) if d[:10] >= HOJE.isoformat())
            if not prazos:
                continue
            item = {"id": gerar_id(link), "titulo": f"{titulo} ({ident})"[:200], "orgao": "União Europeia",
                    "link": link, "anuncio": link, "resumo": desc[:280], "adicionado_em": HOJE.isoformat(),
                    "fonte": "api:ue"}
            item.update(classificar(titulo, desc, None, link, desc[:280]))
            item.update({"abrangencia": "internacional", "ufs": [], "prazo": prazos[0]})
            conhecidos.add(item["id"])
            novos.append(item)
            print("  ok:", titulo[:60], "→", prazos[0])
    print(f"União Europeia: {total_lidas} chamadas abertas ou em breve lidas, {citam} citam Brasil/América Latina")
    print("União Europeia →", len(novos), "novos")
    return novos


# ---------------------------------------------------------------- PNCP (contratações públicas)
# O PNCP é o portal oficial onde órgãos de todo o país publicam suas contratações. CPSI (Lei Complementar
# 182/2021) e encomendas tecnológicas aparecem lá. A busca usa frases exatas: a palavra solta "CPSI"
# casa com qualquer edital.
BUSCAS_PNCP = [
    ("\"contrato público para solução inovadora\"", "cpsi"),
    ("\"solução inovadora\"", "cpsi"),
    ("\"Lei Complementar 182\"", "cpsi"),
    ("\"marco legal das startups\"", "cpsi"),
    ("\"CPSI\"", "cpsi"),
    ("\"encomenda tecnológica\"", "etec"),
]
CONFIRMA_PNCP = {
    "cpsi": re.compile(r"cpsi|solucao inovadora|solucoes inovadoras|complementar n? ?182|marco legal das startups"),
    "etec": re.compile(r"encomenda tecnologica|encomendas tecnologicas"),
}
UFS_VALIDAS = set(UF_RE)


def pncp_get(url, params=None, tentativas=4):
    """GET no PNCP com novas tentativas (o servidor às vezes derruba a conexão)."""
    for t in range(tentativas):
        try:
            r = requests.get(url, params=params, headers={**HEADERS, "Accept": "application/json"}, timeout=40)
            if r.status_code == 200:
                return r.json()
            print("  PNCP respondeu", r.status_code, url[:90])
        except Exception as e:
            print("  PNCP falhou (tentativa", t + 1, ")", type(e).__name__)
        import time
        time.sleep(2 * (t + 1))
    return None


def coletar_pncp(conhecidos):
    novos, mostrou_campos = [], False
    for frase, tipo in BUSCAS_PNCP:
        for pagina in range(1, 6):
            d = pncp_get("https://pncp.gov.br/api/search/", {
                "q": frase, "tipos_documento": "edital", "ordenacao": "-data", "pagina": pagina,
                "tam_pagina": 50, "status": "recebendo_proposta"})
            itens = (d or {}).get("items") or []
            if pagina == 1:
                print(f"PNCP: {frase} → {(d or {}).get('total', 0)} editais recebendo propostas")
            if itens and not mostrou_campos:
                print("  campos:", sorted(itens[0].keys()))
                mostrou_campos = True
            for it in itens:
                texto = normalizar(f"{it.get('title', '')} {it.get('description', '')}")
                if not CONFIRMA_PNCP[tipo].search(texto):
                    continue  # a busca do PNCP é aproximada: confere se o objeto fala mesmo de CPSI/ETEC
                partes = (it.get("item_url") or "").strip("/").split("/")  # compras/<cnpj>/<ano>/<sequencial>
                if len(partes) != 4:
                    continue
                _, cnpj, ano, seq = partes
                link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
                if gerar_id(link) in conhecidos:
                    continue
                conhecidos.add(gerar_id(link))
                # Prazo de propostas e link do arquivo do edital (API oficial de consulta do PNCP).
                prazo, arquivo = None, None
                det = pncp_get(f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}", tentativas=2)
                if det and det.get("dataEncerramentoProposta"):
                    prazo = det["dataEncerramentoProposta"][:10]
                arqs = pncp_get(f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos",
                                tentativas=2)
                for a in arqs or []:
                    if re.search(r"edital", normalizar(f"{a.get('tipoDocumentoNome', '')} {a.get('titulo', '')}")):
                        arquivo = a.get("url") or a.get("uri")
                        break
                if prazo and prazo < HOJE.isoformat():
                    continue
                orgao = (it.get("orgao_nome") or "").title()
                municipio = it.get("municipio_nome") or ""
                uf = (it.get("uf") or "").upper()
                titulo = f"{it.get('title', 'Edital')} – {orgao}"
                desc = it.get("description") or ""
                item = {"id": gerar_id(link), "titulo": titulo[:200], "orgao": orgao or "PNCP",
                        "link": arquivo or link, "anuncio": link, "resumo": desc[:280],
                        "adicionado_em": HOJE.isoformat(), "fonte": "api:pncp"}
                item.update(classificar(titulo, f"{desc} {municipio}", [uf] if uf in UFS_VALIDAS else None, link, desc[:280]))
                item.update({"tipo": tipo, "prazo": prazo or item.get("prazo")})
                if "startup" not in item["proponentes"]:
                    item["proponentes"].append("startup")  # CPSI/ETEC são contratos com empresas
                novos.append(item)
                print(f"  ok [{tipo}]: {titulo[:70]} → prazo {prazo}")
            if len(itens) < 50:
                break
    print("PNCP →", len(novos), "novos")
    return novos


def coletar_noticias(busca, conhecidos):
    return coletar_busca(busca, conhecidos, web=False)


def item_ruim(i):
    """Itens antigos que não passam nos filtros atuais (menus, resultados, links de compartilhamento)."""
    link = i.get("link") or ""
    if i.get("fonte") == "exemplo" or "news.google.com" in link or "google.com/search" in link:
        return True
    if not link_de_edital_valido(link) or eh_ruido(i.get("titulo", "")):
        return True
    # Itens de fontes de órgãos que saíram da lista FONTES_HTML.
    if i.get("fonte", "").startswith("html:") and i["fonte"][5:] not in {f["orgao"] for f in FONTES_HTML}:
        return True
    # Itens da versão antiga do robô (sem o campo "anuncio") não tiveram o edital verificado.
    if "anuncio" not in i:
        return True
    # O link precisa ser o edital, não uma notícia (PDF sempre passa).
    if not link.lower().endswith(".pdf") and (URL_NOTICIA.search(link) or
                                               (i.get("anuncio") == link and parece_noticia(link, i.get("titulo", "")))):
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
    for i in itens:  # corrige o tipo de itens antigos marcados como CPSI só por citarem a LC 182
        if i.get("tipo") == "cpsi" and i.get("fonte") != "api:pncp":
            t = normalizar(f"{i.get('titulo', '')} {i.get('resumo', '')}")
            i["tipo"] = next((k for k, kws in TIPO_KW if tem(t, kws)), "fomento")
    conhecidos = {i["id"] for i in itens} | {gerar_id(i["titulo"]) for i in itens}

    novos = []
    if "--so-limpar" not in sys.argv:
        for fonte in FONTES_HTML:
            novos += coletar_html(fonte, conhecidos)
        for busca in BUSCAS:
            novos += coletar_busca(busca, conhecidos, web=False)
        for busca in BUSCAS_WEB:
            novos += coletar_busca(busca, conhecidos, web=True)
        novos += coletar_ue(conhecidos)
        novos += coletar_pncp(conhecidos)
        for busca, idioma in BUSCAS_EXTERIOR:
            novos += coletar_busca(busca, conhecidos, idioma=idioma)
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
