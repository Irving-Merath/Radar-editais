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
