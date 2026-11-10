Radar de Editais de Inovação
Site que reúne editais de fomento, CPSI, encomendas tecnológicas (ETEC), prêmios, aceleração e desafios de inovação aberta, com filtros por região, público (CPF, CNPJ, parcerias) e segmento (busca ampla ou específica). Atualiza sozinho toda segunda-feira.
Custo: R$ 0. Nenhuma ferramenta pede cartão de crédito.
Arquivos
index.html: o site.
editais.json: a base de oportunidades (começa com exemplos fictícios, que saem na primeira coleta real).
coletar.py: o robô que busca e classifica os editais.
.github/workflows/coletar.yml: agenda o robô toda segunda às 6h.
Como publicar só pelo celular
Use o navegador do celular (Chrome ou Safari) em github.com. Se algum botão não aparecer, ative "Versão para computador" no menu do navegador.

Como a coleta funciona
Para cada fonte oficial (FONTES_HTML em coletar.py), o robô lê os anúncios da página, ignora menus e notícias de resultado/evento, entra em cada anúncio e salva o link da página ou PDF do edital. No site, "Abrir edital" leva ao edital e "Ver anúncio" leva à notícia de origem.
Também faz buscas no Bing: notícias (BUSCAS) e resultados da web (BUSCAS_WEB), incluindo buscas focadas no Rio de Janeiro. Para cobrir outro estado, copie as linhas do RJ trocando o nome do estado e dos órgãos.
Ao filtrar por um estado, as oportunidades nacionais (que valem em qualquer estado) aparecem junto. Dá para desligar isso nos filtros.
Para só reaplicar os filtros de qualidade na base atual, sem coletar: python coletar.py --so-limpar
