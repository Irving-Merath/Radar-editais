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
Crie uma conta gratuita em github.com.
Toque em + > New repository. Nome: radar-editais. Marque Public e Add a README file. Toque em Create repository.
No repositório, toque em Add file > Upload files e envie index.html, editais.json e coletar.py (baixados do chat). Toque em Commit changes.
Toque em Add file > Create new file. No nome, digite exatamente .github/workflows/coletar.yml (as barras criam as pastas). Cole o conteúdo do arquivo coletar.yml e toque em Commit changes.
Vá em Settings > Pages. Em Source, escolha Deploy from a branch, branch main, pasta /(root) e salve. Em 1 a 2 minutos o site estará em https://SEU-USUARIO.github.io/radar-editais.
Vá em Actions > Coleta semanal de editais > Run workflow para fazer a primeira coleta agora. Depois ela roda sozinha toda segunda.
Para corrigir um edital à mão: abra editais.json, toque no lápis, edite e salve.
Como o robô funciona
Lê as páginas de editais da lista FONTES_HTML e as buscas da lista BUSCAS (Google Notícias, últimos 7 dias).
Classifica por palavras-chave: tipo, segmentos, público, estado, prazo e valor.
Ignora o que já existe, apaga editais encerrados há mais de 90 dias e salva tudo em editais.json.
Itens vindos de notícia aparecem com a marca "via notícia": é preciso conferir o edital oficial.
Para adicionar fontes, inclua uma linha em FONTES_HTML com órgão, endereço da página de editais e estado.
Observação: o GitHub pausa tarefas agendadas de repositórios sem atividade por 60 dias. Como o robô faz um commit a cada coleta com novidades, isso normalmente não acontece. Se pausar, basta reativar em Actions.

Plano para escalar gastando pouco
Fase 1, validar (R$ 0). Mantenha GitHub Pages e Actions. Aumente a lista de fontes: fundações de amparo à pesquisa de todos os estados, Sebrae, Embrapii, BNDES, fundações privadas e programas corporativos. Para CPSI e encomendas tecnológicas, a fonte mais completa é o Portal Nacional de Contratações Públicas (PNCP), que tem API pública e gratuita. Crie um canal no Telegram e um canal no WhatsApp e poste as novidades da semana: é o meio mais barato de ganhar usuários. Um Google Forms permite que usuários sugiram editais. Meça uso com Cloudflare Web Analytics ou GoatCounter (gratuitos).
Fase 2, qualidade (perto de R$ 0). Troque a classificação por palavras-chave por um modelo de linguagem com plano gratuito (por exemplo, a API do Gemini pelo Google AI Studio ou a Groq, que hoje não exigem cartão; confira as condições atuais). Ele lê o PDF do edital e extrai prazo, valor, público e segmentos com muito mais precisão. Quando quiser contas de usuário e alertas por e-mail personalizados, use Supabase (banco e login, plano gratuito) e Brevo ou Resend para e-mails (planos gratuitos). Um domínio .com.br no registro.br custa cerca de R$ 40 por ano.
Fase 3, sustentar. Possíveis fontes de receita: alertas personalizados pagos (WhatsApp ou e-mail no dia em que sai um edital do seu perfil), plano para incubadoras, aceleradoras e prefeituras acompanharem oportunidades dos seus empreendedores, patrocínio de fundações e órgãos que querem mais inscritos qualificados, e indicação de consultores para escrever propostas. Valide com 20 a 30 usuários reais antes de construir qualquer parte paga.
Regra de ouro: só pague por uma ferramenta quando o limite gratuito estiver de fato atrapalhando os usuários.



