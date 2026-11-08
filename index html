<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Radar de Editais de Inovação</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#EEF3F0;--surface:#FFFFFF;--ink:#13261F;--muted:#55665F;--line:#D3DDD8;--green:#0E5A45;--on-green:#FFFFFF;--green-soft:#D6EBE2;--sun:#F2B705;--sun-ink:#3D2E00;--danger:#B3412E;--display:"Bricolage Grotesque",ui-rounded,"Segoe UI",system-ui,sans-serif;--text:"Instrument Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0C1512;--surface:#13201B;--ink:#E4EEE9;--muted:#93A79F;--line:#24352E;--green:#5CCB9F;--on-green:#062019;--green-soft:#183A2E;--sun:#F5C842;--sun-ink:#2A2000;--danger:#F08A73;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0C1512;--surface:#13201B;--ink:#E4EEE9;--muted:#93A79F;--line:#24352E;--green:#5CCB9F;--on-green:#062019;--green-soft:#183A2E;--sun:#F5C842;--sun-ink:#2A2000;--danger:#F08A73;color-scheme:dark}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
*,*::before,*::after{box-sizing:inherit}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--text);font-size:16px;line-height:1.5;-webkit-text-size-adjust:100%}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
.wrap{max-width:760px;margin:0 auto;padding:0 16px}
header.top{padding:28px 0 12px}
h1{font-family:var(--display);font-weight:800;font-size:clamp(2rem,8vw,3rem);line-height:1;letter-spacing:-.02em;margin:0 0 10px}
.sub{margin:0 0 6px;color:var(--muted);max-width:56ch}
.meta{margin:0;font-size:.875rem;color:var(--muted)}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);padding:10px 0}
.bar .row{display:flex;gap:8px}
input[type=search],select{font:inherit;color:var(--ink);background:var(--surface);border:1.5px solid var(--line);border-radius:12px;padding:11px 14px;min-width:0}
input[type=search]{flex:1}
input:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible{outline:3px solid var(--sun);outline-offset:2px}
.btn{font:inherit;font-weight:600;border:0;border-radius:12px;padding:11px 16px;cursor:pointer;background:var(--green);color:var(--on-green);display:inline-flex;align-items:center;gap:8px;white-space:nowrap;text-decoration:none}
.btn.ghost{background:transparent;color:var(--green);border:1.5px solid var(--line)}
.count{background:var(--sun);color:var(--sun-ink);border-radius:999px;font-size:.75rem;min-width:20px;height:20px;display:inline-grid;place-items:center;padding:0 6px}
.quick{display:flex;gap:8px;overflow-x:auto;padding:2px 0 4px;scrollbar-width:none}
.quick::-webkit-scrollbar{display:none}
.chip{font:inherit;font-size:.9rem;border:1.5px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:7px 14px;cursor:pointer;white-space:nowrap}
.chip[aria-pressed="true"]{background:var(--green);border-color:var(--green);color:var(--on-green)}
.summary{margin:8px 0 0;font-size:.9rem;color:var(--muted)}
.note{margin:14px 0 0;padding:12px 14px;border-left:4px solid var(--sun);background:var(--surface);border-radius:4px 12px 12px 4px;font-size:.9rem}
main{padding:8px 0 48px}
.item{display:grid;grid-template-columns:76px 1fr;gap:14px;padding:20px 0;border-bottom:1px solid var(--line)}
.prazo{text-align:center;padding-top:2px}
.prazo .n{display:block;font-family:var(--display);font-weight:800;font-size:2.6rem;line-height:.9;color:var(--green);letter-spacing:-.03em}
.prazo .n.txt{font-size:1.15rem;line-height:1.1}
.prazo .u{display:block;font-size:.8rem;color:var(--muted);margin-top:4px}
.prazo.urg .n{color:var(--danger)}
.prazo.off .n{color:var(--muted)}
.org{margin:0;font-size:.85rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.tag{font-size:.72rem;font-weight:600;border-radius:6px;padding:1px 7px}
.tag.novo{background:var(--sun);color:var(--sun-ink)}
.tag.ex{border:1px dashed var(--muted);color:var(--muted)}
.item h2{font-family:var(--display);font-weight:700;font-size:1.2rem;line-height:1.2;margin:4px 0 6px;letter-spacing:-.01em}
.desc{margin:0 0 10px;color:var(--ink);opacity:.88;font-size:.95rem;max-width:62ch}
.fatos{margin:0 0 8px;display:flex;flex-wrap:wrap;gap:6px}
.fatos span{font-size:.8rem;background:var(--green-soft);color:var(--ink);border-radius:6px;padding:2px 8px}
.segs{margin:0 0 12px;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:6px}
.segs li{font-size:.78rem;border:1px solid var(--line);border-radius:999px;padding:1px 9px;color:var(--muted)}
.segs li.hit{border-color:var(--green);color:var(--green);font-weight:600}
.acoes{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.valor{font-weight:600;font-size:.95rem}
.acoes a{color:var(--green);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.vazio{padding:40px 0;text-align:center;color:var(--muted)}
.vazio button{margin-top:12px}
dialog{border:0;padding:0;width:100%;max-width:760px;max-height:88vh;margin:auto auto 0;border-radius:20px 20px 0 0;background:var(--surface);color:var(--ink)}
dialog::backdrop{background:rgba(5,20,15,.5)}
@media (min-width:700px){dialog{margin:auto;border-radius:20px}}
.sheet{display:flex;flex-direction:column;max-height:88vh}
.sheet-head{display:flex;justify-content:space-between;align-items:center;padding:16px 18px 8px}
.sheet-head h2{font-family:var(--display);margin:0;font-size:1.4rem}
.x{font:inherit;font-size:1.6rem;line-height:1;background:none;border:0;color:var(--muted);cursor:pointer;padding:4px 8px}
.sheet-body{overflow-y:auto;padding:0 18px 12px}
fieldset{border:0;margin:0;padding:14px 0;border-top:1px solid var(--line)}
legend{font-family:var(--display);font-weight:700;font-size:1.05rem;padding:0;margin-bottom:8px}
.hint{font-size:.85rem;color:var(--muted);margin:0 0 10px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.grp{font-size:.85rem;color:var(--muted);margin:12px 0 6px}
.seg-mode{display:grid;grid-template-columns:1fr 1fr;background:var(--bg);border-radius:12px;padding:4px;gap:4px;margin-bottom:8px}
.seg-mode button{font:inherit;font-size:.9rem;font-weight:600;border:0;border-radius:9px;padding:9px 6px;background:transparent;color:var(--muted);cursor:pointer}
.seg-mode button[aria-pressed="true"]{background:var(--surface);color:var(--ink);box-shadow:0 1px 3px rgba(0,0,0,.12)}
.line{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:6px 0}
.line label{font-size:.95rem}
.line select{padding:8px 10px}
input[type=checkbox]{width:22px;height:22px;accent-color:var(--green)}
.sheet-foot{display:flex;gap:10px;padding:12px 18px calc(12px + env(safe-area-inset-bottom,0px));border-top:1px solid var(--line)}
.sheet-foot .btn{flex:1;justify-content:center}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1>Radar de Editais</h1>
    <p class="sub">Fomento não reembolsável, CPSI, encomendas tecnológicas e desafios de inovação para CPF, MEI, startups e negócios de impacto.</p>
    <p class="meta" id="meta"></p>
  </header>

  <div class="bar">
    <div class="row">
      <input type="search" id="q" placeholder="Buscar por tema, órgão ou palavra" aria-label="Buscar oportunidades">
      <button class="btn" id="abrir" type="button" aria-haspopup="dialog">Filtros <span class="count" id="nf" hidden>0</span></button>
    </div>
  </div>

  <div class="quick" id="quick" aria-label="Onde a oportunidade vale"></div>
  <p class="summary" id="summary" aria-live="polite"></p>
  <p class="note" id="aviso" hidden>Os itens marcados como <strong>exemplo</strong> são fictícios e servem para demonstrar os filtros. Os editais reais entram após a primeira coleta automática.</p>

  <main id="lista"></main>
</div>

<dialog id="dlg" aria-labelledby="dlgt">
  <div class="sheet">
    <div class="sheet-head"><h2 id="dlgt">Filtros</h2><button class="x" type="button" id="fechar" aria-label="Fechar filtros">×</button></div>
    <div class="sheet-body">
      <fieldset>
        <legend>Onde vale</legend>
        <div class="chips" id="f-onde"></div>
        <div class="line"><label for="uf">Estado das oportunidades regionais</label><select id="uf"></select></div>
      </fieldset>
      <fieldset>
        <legend>Quem pode participar</legend>
        <p class="hint">“CNPJ” inclui MEI, startups, empresas e organizações.</p>
        <div class="chips" id="f-prop"></div>
      </fieldset>
      <fieldset>
        <legend>Tipo de oportunidade</legend>
        <div class="chips" id="f-tipo"></div>
      </fieldset>
      <fieldset>
        <legend>Segmentos</legend>
        <div class="seg-mode" role="group" aria-label="Modo de busca por segmento">
          <button type="button" data-modo="ampla">Busca ampla</button>
          <button type="button" data-modo="especifica">Busca específica</button>
        </div>
        <p class="hint" id="modoTexto"></p>
        <p class="grp">Tecnologias</p>
        <div class="chips" id="f-tec"></div>
        <p class="grp">Áreas de aplicação</p>
        <div class="chips" id="f-area"></div>
      </fieldset>
      <fieldset>
        <legend>Prazo e ordem</legend>
        <div class="line"><label for="abertos">Mostrar só inscrições abertas</label><input type="checkbox" id="abertos"></div>
        <div class="line"><label for="ordem">Ordenar por</label>
          <select id="ordem"><option value="prazo">Prazo mais próximo</option><option value="recentes">Adicionados recentemente</option></select></div>
      </fieldset>
    </div>
    <div class="sheet-foot">
      <button class="btn ghost" type="button" id="limpar">Limpar filtros</button>
      <button class="btn" type="button" id="ver">Ver resultados</button>
    </div>
  </div>
</dialog>

<script type="application/json" id="seed">{"atualizado_em":"2026-11-08","editais":[
{"id":"ex01","titulo":"Apoio a startups de base tecnológica no estado do Rio de Janeiro","orgao":"FAPERJ","tipo":"fomento","abrangencia":"regional","ufs":["RJ"],"proponentes":["startup","mei"],"segmentos":["ia","bigdata","iot","saude","educacao"],"valor":"até R$ 200 mil","prazo":"2026-12-15","link":"https://www.faperj.br","resumo":"Subvenção não reembolsável para desenvolver produto ou serviço inovador, para empresas com sede no RJ.","adicionado_em":"2026-11-05","fonte":"exemplo"},
{"id":"ex02","titulo":"Subvenção para soluções de inteligência artificial na saúde pública","orgao":"Finep","tipo":"fomento","abrangencia":"nacional","ufs":[],"proponentes":["startup"],"segmentos":["ia","saude","bigdata"],"valor":"R$ 500 mil a R$ 2 milhões","prazo":"2027-01-30","link":"http://www.finep.gov.br","resumo":"Recursos não reembolsáveis para empresas que desenvolvam IA aplicada a diagnóstico, triagem e gestão do SUS.","adicionado_em":"2026-11-03","fonte":"exemplo"},
{"id":"ex03","titulo":"Aceleração de negócios de impacto da economia circular","orgao":"AgeRio","tipo":"aceleracao","abrangencia":"regional","ufs":["RJ"],"proponentes":["mei","osc","startup"],"segmentos":["residuos","clima","social"],"valor":"Mentorias e capital semente","prazo":"2026-11-28","link":"https://www.agerio.com.br","resumo":"Programa de 4 meses para negócios que reduzem, reaproveitam ou reciclam resíduos em comunidades fluminenses.","adicionado_em":"2026-11-06","fonte":"exemplo"},
{"id":"ex04","titulo":"CPSI: monitoramento de enchentes com sensores e visão computacional","orgao":"Prefeitura municipal (RJ)","tipo":"cpsi","abrangencia":"regional","ufs":["RJ"],"proponentes":["startup","parceria"],"segmentos":["iot","visao","clima","cidades"],"valor":"até R$ 1,6 milhão","prazo":"2026-11-20","link":"https://www.gov.br/compras/pt-br","resumo":"Contrato Público para Solução Inovadora: teste de solução que detecte alagamentos em tempo real e alerte a Defesa Civil.","adicionado_em":"2026-11-07","fonte":"exemplo"},
{"id":"ex05","titulo":"CPSI: otimização de rotas da coleta de resíduos com dados","orgao":"Governo do estado de São Paulo","tipo":"cpsi","abrangencia":"regional","ufs":["SP"],"proponentes":["startup"],"segmentos":["bigdata","ia","residuos","logistica"],"valor":"até R$ 1,6 milhão","prazo":"2026-12-04","link":"https://www.gov.br/compras/pt-br","resumo":"Busca solução que reduza quilometragem e custo da coleta usando dados de GPS, volume e demanda.","adicionado_em":"2026-10-28","fonte":"exemplo"},
{"id":"ex06","titulo":"Grants for climate tech in the Global South","orgao":"Fundação internacional","tipo":"fomento","abrangencia":"internacional","ufs":[],"proponentes":["osc","startup","parceria"],"segmentos":["clima","energia","iot"],"valor":"até US$ 100 mil","prazo":"2027-02-15","link":"https://www.globalinnovation.fund","resumo":"Doação para pilotos de energia limpa e adaptação climática liderados por organizações locais.","adicionado_em":"2026-11-04","fonte":"exemplo"},
{"id":"ex07","titulo":"Projetos culturais que usam tecnologia para ampliar acesso","orgao":"Fundação cultural nacional","tipo":"fomento","abrangencia":"nacional","ufs":[],"proponentes":["cpf","mei","osc"],"segmentos":["cultura","educacao"],"valor":"até R$ 50 mil","prazo":"2026-12-10","link":"https://www.gov.br/cultura","resumo":"Aceita pessoa física. Apoia acervos digitais, acessibilidade e formação de público.","adicionado_em":"2026-10-20","fonte":"exemplo"},
{"id":"ex08","titulo":"Desafio de inovação aberta: POC de visão computacional em centros de distribuição","orgao":"Programa de inovação de empresa de varejo","tipo":"poc","abrangencia":"nacional","ufs":[],"proponentes":["startup"],"segmentos":["visao","logistica","ia"],"valor":"POC remunerada","prazo":"2026-11-25","link":"https://www.google.com/search?q=desafio+inova%C3%A7%C3%A3o+aberta+POC+startups","resumo":"Prova de conceito de 90 dias para contagem automática de estoque e conferência de cargas.","adicionado_em":"2026-11-02","fonte":"exemplo"},
{"id":"ex09","titulo":"Capacitação e bolsa para microempreendedores inovadores","orgao":"Sebrae","tipo":"aceleracao","abrangencia":"nacional","ufs":[],"proponentes":["mei","cpf"],"segmentos":["educacao","financas"],"valor":"Bolsa mensal","prazo":"2026-12-20","link":"https://sebrae.com.br","resumo":"Trilha de formação em gestão e validação de produto para quem está começando.","adicionado_em":"2026-11-02","fonte":"exemplo"},
{"id":"ex10","titulo":"Bolsas para pesquisador empreendedor em IoT no agro","orgao":"CNPq","tipo":"fomento","abrangencia":"nacional","ufs":[],"proponentes":["cpf","parceria"],"segmentos":["iot","agro","bigdata"],"valor":"Bolsa + custeio","prazo":"2027-01-15","link":"https://www.gov.br/cnpq","resumo":"Para pesquisadores que queiram levar tecnologia ao mercado em parceria com empresas.","adicionado_em":"2026-10-15","fonte":"exemplo"},
{"id":"ex11","titulo":"Encomenda tecnológica: triagem de exames de imagem com IA","orgao":"Hospital público federal","tipo":"etec","abrangencia":"nacional","ufs":[],"proponentes":["startup","parceria"],"segmentos":["ia","visao","saude"],"valor":"até R$ 3 milhões","prazo":"2027-01-10","link":"https://www.gov.br/mcti","resumo":"ETEC para desenvolver solução ainda inexistente no mercado, com risco tecnológico compartilhado.","adicionado_em":"2026-11-08","fonte":"exemplo"},
{"id":"ex12","titulo":"Primeiros passos: ideia inovadora para empresa","orgao":"FAPEMIG","tipo":"fomento","abrangencia":"regional","ufs":["MG"],"proponentes":["cpf","startup"],"segmentos":["ia","agro","energia"],"valor":"até R$ 80 mil","prazo":"2026-12-01","link":"https://fapemig.br","resumo":"Aceita CPF na inscrição; a empresa precisa ser aberta só se a proposta for aprovada.","adicionado_em":"2026-10-30","fonte":"exemplo"},
{"id":"ex13","titulo":"Prêmio para soluções de educação e inclusão digital","orgao":"Fundação educacional","tipo":"premio","abrangencia":"nacional","ufs":[],"proponentes":["cpf","osc"],"segmentos":["educacao","social"],"valor":"R$ 30 mil","prazo":"2026-11-15","link":"https://www.google.com/search?q=pr%C3%AAmio+educa%C3%A7%C3%A3o+inclus%C3%A3o+digital","resumo":"Reconhece iniciativas que levam conectividade e letramento digital a escolas públicas.","adicionado_em":"2026-10-22","fonte":"exemplo"},
{"id":"ex14","titulo":"Gestão comunitária de resíduos sólidos","orgao":"Fundação estadual (BA)","tipo":"fomento","abrangencia":"regional","ufs":["BA"],"proponentes":["osc","parceria"],"segmentos":["residuos","social","clima"],"valor":"até R$ 120 mil","prazo":"2026-10-30","link":"https://www.google.com/search?q=edital+res%C3%ADduos+s%C3%B3lidos+Bahia","resumo":"Projetos de coleta seletiva conduzidos por associações e cooperativas.","adicionado_em":"2026-10-01","fonte":"exemplo"},
{"id":"ex15","titulo":"Open call for health data startups (Europe and Latin America)","orgao":"Aceleradora europeia","tipo":"aceleracao","abrangencia":"internacional","ufs":[],"proponentes":["startup","parceria"],"segmentos":["saude","bigdata","ia"],"valor":"€ 50 mil + aceleração","prazo":"2026-12-31","link":"https://www.google.com/search?q=open+call+health+data+startups","resumo":"Programa remoto com investimento inicial para startups de dados em saúde.","adicionado_em":"2026-11-01","fonte":"exemplo"},
{"id":"ex16","titulo":"CPSI: plataforma de gestão escolar com análise de dados","orgao":"Secretaria de Educação (PE)","tipo":"cpsi","abrangencia":"regional","ufs":["PE"],"proponentes":["startup","mei"],"segmentos":["educacao","bigdata"],"valor":"até R$ 1,6 milhão","prazo":"2026-12-08","link":"https://www.gov.br/compras/pt-br","resumo":"Teste de solução para prever evasão escolar e apoiar a gestão das redes de ensino.","adicionado_em":"2026-11-06","fonte":"exemplo"}
]}
</script>
<script>
(function(){
const ONDE={regional:"Meu estado",nacional:"Brasil todo",internacional:"Mundo"};
const PROPS={cpf:"Pessoa física (CPF)",cnpj:"CNPJ (qualquer)",mei:"MEI",startup:"Startup ou empresa",osc:"OSC ou negócio de impacto",parceria:"Parcerias e consórcios"};
const PROP_CURTO={cpf:"CPF",mei:"MEI",startup:"Startup/empresa",osc:"OSC/impacto",parceria:"Parceria"};
const TIPOS={fomento:"Fomento não reembolsável",cpsi:"CPSI",etec:"Encomenda tecnológica",poc:"POC e inovação aberta",aceleracao:"Aceleração",premio:"Prêmio"};
const TEC={bigdata:"Big data",ia:"IA e machine learning",visao:"Visão computacional",iot:"IoT"};
const AREA={saude:"Saúde",educacao:"Educação",cultura:"Cultura",residuos:"Gestão de resíduos",logistica:"Logística",agro:"Agro e alimentos",energia:"Energia",clima:"Clima e meio ambiente",cidades:"Cidades e governo",financas:"Finanças e inclusão",social:"Impacto social"};
const SEGS=Object.assign({},TEC,AREA);
const UFS=["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];
const KEY="radar-editais-v1";
const PADRAO={q:"",onde:[],uf:"",prop:[],tipo:[],seg:[],modo:"ampla",abertos:true,ordem:"prazo"};
let S=Object.assign({},PADRAO);
try{const s=JSON.parse(localStorage.getItem(KEY)||"null");if(s)S=Object.assign({},PADRAO,s);}catch(e){}
function salvar(){try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}}

let dados=[],atualizado="";
function carregar(obj){const arr=Array.isArray(obj)?obj:(obj.editais||[]);dados=arr;atualizado=(!Array.isArray(obj)&&obj.atualizado_em)||arr.reduce((m,i)=>i.adicionado_em>m?i.adicionado_em:m,"");}
carregar(JSON.parse(document.getElementById("seed").textContent));

const $=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c
