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

const $=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const norm=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
const hoje=new Date();hoje.setHours(0,0,0,0);
function dias(p){if(!p)return null;const d=new Date(p+"T00:00:00");return Math.round((d-hoje)/864e5);}
function fmtData(p){const d=new Date(p+"T00:00:00");return d.toLocaleDateString("pt-BR",{day:"numeric",month:"short",year:d.getFullYear()!==hoje.getFullYear()?"numeric":undefined}).replace(".","");}
function novo(i){const d=dias(i.adicionado_em);return d!==null&&d>=-7;}

function chips(el,mapa,campo){el.innerHTML=Object.entries(mapa).map(([k,v])=>`<button type="button" class="chip" data-campo="${campo}" data-val="${k}" aria-pressed="false">${esc(v)}</button>`).join("");}
chips($("quick"),ONDE,"onde");chips($("f-onde"),ONDE,"onde");chips($("f-prop"),PROPS,"prop");chips($("f-tipo"),TIPOS,"tipo");chips($("f-tec"),TEC,"seg");chips($("f-area"),AREA,"seg");
$("uf").innerHTML=`<option value="">Qualquer estado</option>`+UFS.map(u=>`<option>${u}</option>`).join("");

document.addEventListener("click",e=>{
  const c=e.target.closest(".chip[data-campo]");
  if(c){const arr=S[c.dataset.campo],v=c.dataset.val,i=arr.indexOf(v);i>=0?arr.splice(i,1):arr.push(v);atualizar();return;}
  const m=e.target.closest("[data-modo]");if(m){S.modo=m.dataset.modo;atualizar();return;}
  if(e.target.closest("#limpar-vazio")){limpar();}
});
$("q").addEventListener("input",e=>{S.q=e.target.value;atualizar();});
$("uf").addEventListener("change",e=>{S.uf=e.target.value;if(S.uf&&!S.onde.includes("regional"))S.onde.push("regional");atualizar();});
$("abertos").addEventListener("change",e=>{S.abertos=e.target.checked;atualizar();});
$("ordem").addEventListener("change",e=>{S.ordem=e.target.value;atualizar();});
const dlg=$("dlg");
$("abrir").addEventListener("click",()=>dlg.showModal());
$("fechar").addEventListener("click",()=>dlg.close());
$("ver").addEventListener("click",()=>dlg.close());
dlg.addEventListener("click",e=>{if(e.target===dlg)dlg.close();});
function limpar(){const q=S.q;S=JSON.parse(JSON.stringify(PADRAO));S.q=q;atualizar();}
$("limpar").addEventListener("click",limpar);

function passa(i){
  if(S.q){const t=norm(i.titulo+" "+i.orgao+" "+i.resumo);if(!norm(S.q).split(/\s+/).every(w=>t.includes(w)))return false;}
  const d=dias(i.prazo);
  if(S.abertos&&d!==null&&d<0)return false;
  if(S.onde.length&&!S.onde.some(o=>o==="regional"?(i.abrangencia==="regional"&&(!S.uf||(i.ufs||[]).includes(S.uf))):i.abrangencia===o))return false;
  const p=i.proponentes||[];
  if(S.prop.length&&!S.prop.some(x=>x==="cnpj"?p.some(y=>["mei","startup","osc"].includes(y)):p.includes(x)))return false;
  if(S.tipo.length&&!S.tipo.includes(i.tipo))return false;
  const sg=i.segmentos||[];
  if(S.seg.length){if(S.modo==="especifica"?!S.seg.every(x=>sg.includes(x)):!S.seg.some(x=>sg.includes(x)))return false;}
  return true;
}
function ordenar(a,b){
  if(S.ordem==="recentes")return (b.adicionado_em||"").localeCompare(a.adicionado_em||"");
  const da=dias(a.prazo),db=dias(b.prazo);const k=d=>d===null?1e6:(d<0?2e6-d:d);return k(da)-k(db);
}
function lista(arr,mapa){return arr.map(x=>mapa[x]).filter(Boolean);}
function juntar(arr,ult){return arr.length<2?arr.join(""):arr.slice(0,-1).join(", ")+" "+ult+" "+arr[arr.length-1];}

function card(i){
  const d=dias(i.prazo);let n,u,cls="";
  if(d===null){n="Aberto";u="sem prazo";cls="off";}
  else if(d<0){n="Encerrado";u=fmtData(i.prazo);cls="off";}
  else if(d===0){n="Hoje";u="último dia";cls="urg";}
  else{n=d;u=(d===1?"dia":"dias")+"<br>até "+fmtData(i.prazo);if(d<=7)cls="urg";}
  const txt=typeof n==="string";
  const onde=i.abrangencia==="regional"?((i.ufs||[]).join(", ")||"Regional"):(i.abrangencia==="internacional"?"Internacional":"Nacional");
  const pub=lista(i.proponentes||[],PROP_CURTO);
  const segs=(i.segmentos||[]).map(s=>SEGS[s]?`<li class="${S.seg.includes(s)?"hit":""}">${esc(SEGS[s])}</li>`:"").join("");
  const via=(i.fonte||"").startsWith("noticia")?`<span class="tag ex">via notícia</span>`:"";
  return `<article class="item">
  <div class="prazo ${cls}"><span class="n${txt?" txt":""}">${esc(n)}</span><span class="u">${u}</span></div>
  <div>
    <p class="org">${esc(i.orgao)}${novo(i)?'<span class="tag novo">Novo</span>':""}${i.fonte==="exemplo"?'<span class="tag ex">exemplo</span>':""}${via}</p>
    <h2>${esc(i.titulo)}</h2>
    ${i.resumo?`<p class="desc">${esc(i.resumo)}</p>`:""}
    <p class="fatos"><span>${esc(TIPOS[i.tipo]||"Oportunidade")}</span><span>${esc(onde)}</span><span>${pub.length?esc(pub.join(", ")):"Público a confirmar"}</span></p>
    ${segs?`<ul class="segs" aria-label="Segmentos">${segs}</ul>`:""}
    <div class="acoes"><span class="valor">${esc(i.valor||"")}</span><a href="${esc(i.link)}" target="_blank" rel="noopener">Abrir edital</a></div>
  </div></article>`;
}

function atualizar(){
  salvar();
  document.querySelectorAll(".chip[data-campo]").forEach(c=>c.setAttribute("aria-pressed",S[c.dataset.campo].includes(c.dataset.val)));
  document.querySelectorAll("[data-modo]").forEach(b=>b.setAttribute("aria-pressed",S.modo===b.dataset.modo));
  $("uf").value=S.uf;$("abertos").checked=S.abertos;$("ordem").value=S.ordem;if($("q").value!==S.q)$("q").value=S.q;
  const nomes=S.seg.map(s=>SEGS[s]);
  $("modoTexto").textContent=S.modo==="ampla"
    ?(nomes.length>1?`Mostra oportunidades de ${juntar(nomes,"ou")}.`:"Mostra oportunidades de qualquer segmento marcado.")
    :(nomes.length>1?`Mostra só oportunidades que combinam ${juntar(nomes,"e")}.`:"Mostra só oportunidades que combinam todos os segmentos marcados.");
  const res=dados.filter(passa).sort(ordenar);
  const nf=S.onde.length+S.prop.length+S.tipo.length+S.seg.length+(S.uf?1:0)+(S.abertos?0:1);
  $("nf").hidden=!nf;$("nf").textContent=nf;
  $("ver").textContent=res.length===1?"Ver 1 oportunidade":`Ver ${res.length} oportunidades`;
  let sm=(res.length===1?"1 oportunidade":res.length+" oportunidades")+(S.abertos?" com inscrições abertas":"");
  if(nomes.length>1)sm+=S.modo==="especifica"?`, combinando ${juntar(nomes,"e")}`:`, em ${juntar(nomes,"ou")}`;
  else if(nomes.length===1)sm+=`, em ${nomes[0]}`;
  $("summary").textContent=sm+".";
  $("aviso").hidden=!dados.some(i=>i.fonte==="exemplo");
  const novos=dados.filter(novo).length;
  $("meta").textContent=(atualizado?`Atualizado em ${fmtData(atualizado)}. `:"")+(novos?`${novos} novos nos últimos 7 dias.`:"");
  $("lista").innerHTML=res.length?res.map(card).join(""):`<div class="vazio"><p>Nenhuma oportunidade com esses filtros.${S.modo==="especifica"&&S.seg.length>1?" Experimente a busca ampla nos segmentos.":""}</p><button class="btn ghost" id="limpar-vazio" type="button">Limpar filtros</button></div>`;
}

// Carrega a base de editais atualizada pela coleta semanal.
$("lista").innerHTML='<p class="vazio">Carregando oportunidades…</p>';
fetch("editais.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw new Error(r.status);return r.json();})
  .then(j=>{carregar(j);atualizar();})
  .catch(()=>{$("lista").innerHTML='<p class="vazio">Não foi possível carregar o arquivo editais.json.</p>';});
})();
