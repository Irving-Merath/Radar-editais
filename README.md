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

https://irving-merath.github.io/Radar-editais/

Como a coleta funciona
Para cada fonte oficial (FONTES_HTML em coletar.py), o robô lê os anúncios da página, ignora menus e notícias de resultado/evento, entra em cada anúncio e salva o link do PDF ou da página do edital (nunca a notícia; se não achar o edital, o anúncio é descartado). Um anúncio que lança vários editais gera um item por edital, com o nome oficial como título. No site, "Abrir edital" leva ao edital e "Ver anúncio" leva à notícia de origem.
O robô lê as primeiras páginas do PDF do edital para achar prazo, valor e público. Edital com prazo de inscrição já vencido fica marcado como encerrado.
Também busca notícias no Bing (BUSCAS), incluindo buscas focadas no Rio de Janeiro. A notícia só entra se tiver link para o edital oficial.
Ao filtrar por um estado, as oportunidades nacionais (que valem em qualquer estado) aparecem junto. Dá para desligar isso nos filtros.
Fontes atuais: FAPERJ, AgeRio, Centelha RJ e InovAtiva; FAPESP PIPE (SP), FACEPE (PE), FAPES (ES), FAPERGS (RS); CNPq (nacional) e Confap (chamadas internacionais com a União Europeia e outros países).
Limites conhecidos: as FAPs de SC, CE, DF e PR têm certificado de segurança incompleto e não são lidas. Finep, FAPEMIG, Prosas e Sebrae Startups montam a lista de editais com JavaScript, e o BNDES recusa conexões do GitHub, por isso esses órgãos só entram pelas notícias. A busca web do Bing (BUSCAS_WEB) ignora a pergunta e o DuckDuckGo bloqueia robôs, então hoje essas buscas não trazem resultados.
Para só reaplicar os filtros de qualidade na base atual, sem coletar: python coletar.py --so-limpar
O log de cada coleta (aba Actions) mostra, por fonte, quantos links foram lidos e por que foram descartados.
