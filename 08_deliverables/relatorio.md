# Relatório — Implementador de IA & Automações

**Projeto Revelatio · Avaliação de ferramentas e recomendação de arquitetura para extração de dossiês do Banco X**

Data: 2026-05-12

---

## Sumário executivo

Avaliamos nove ferramentas em quatro categorias arquiteturais — workflows comerciais, workflows OSS, LLMs *frontier* e OCR/extração estruturada — buscando uma solução para extrair ~10.000 PDFs de clientes devedores do Banco X em planilha Excel. **Construímos um pipeline de referência em Python** (`06_reference_script/`) que implementa a arquitetura recomendada e medimos **100% de acurácia, zero alucinações e US$ 0,00934 por dossiê** em validação contra quatro PDFs — três do corpus de base (PDF do brief + F02 + F07) e um *holdout* fora da distribuição que geramos especialmente para este teste (`F09_brief_shape`, mesma estrutura visual do PDF do brief, com dados de cliente completamente novos). **Expusemos esse motor publicamente em `https://revelatio-demo.streamlit.app`**, com gravação automática em planilha Google compartilhada como destino opcional, para que o painel avaliador possa exercitá-lo diretamente. **Recomendamos esse pipeline como caminho principal**, em arquitetura híbrida de duas camadas com regras de *cross-validation* e fila HITL; o Power Automate com AI Builder, que avaliamos *hands-on* e que obteve 92,8% médio em corpus sintético com zero alucinações, fica como **caminho alternativo** para escritórios já residentes em Microsoft 365 que prefiram manutenção *no-code* por paralegal. O custo total estimado para processar o *backlog* de 10.000 dossiês é de **R$ 457** (PTAX 4,8999, 2026-05-08) contra **R$ 50.500** do trabalho manual no ponto médio salarial — razão de **~110×** e *payback* no primeiro dia de operação. As conclusões abaixo derivam de testes empíricos cujos artefatos estão referenciados em cada afirmação quantitativa.

---

## §1 — Ferramentas testadas

Avaliamos nove ferramentas, das quais seis em testes *hands-on* e três em análise documental comparativa (orquestradores e proxies de LLM, avaliados a partir de documentação oficial em `02_tool_universe/`). A tabela abaixo consolida os resultados sobre o PDF de exemplo do brief; o Power Automate foi adicionalmente avaliado contra o corpus sintético de oito *fixtures* (F01–F08), e o pipeline de referência em Python foi adicionalmente validado contra o *holdout* OOD `F09_brief_shape` (descrito em §2). A fonte dos números é `04_experiments/SCOREBOARD.md` §1.

| # | Ferramenta | Classe | Página 1 | Página 2 | Alucinações | Modalidade |
|---|---|---|---|---|---|---|
| 1 | Power Automate + AI Builder | Workflow comercial M365 + OCR treinado | 100% | layout-sensível¹ | 0 | ✅ *hands-on* ponta a ponta |
| 2 | ChatGPT 5.5 Thinking | LLM *frontier* | 100% | 100% | 0 | ✅ *hands-on* |
| 3 | Claude Opus 4.7 | LLM *frontier* | 100% | 100% | 0 | ✅ *hands-on* |
| 4 | NotebookLM (Gemini) | LLM ancorado em fontes | 100% | 100% | 0 | ✅ *hands-on* |
| 5 | Azure Document Intelligence Layout | OCR comercial estruturado | 100% (16 células) | estrutura detectada² | 0 | ✅ *hands-on* |
| 6 | Tabula (tabula-py 2.10) | OSS determinístico | 100% (16 células) | 0%³ | 0 | ✅ *hands-on* |
| 7 | Microsoft Copilot | LLM em invólucro M365 | proxy de #2⁴ | — | — | ⏭️ análise documental |
| 8 | Make (Integromat) | iPaaS comercial (orquestrador) | — | — | — | 📋 análise documental |
| 9 | n8n | Workflow OSS (orquestrador) | — | — | — | 📋 análise documental |

Notas: ¹ falha de fora-da-distribuição detalhada em §3. ² Azure DI Layout retorna texto + tabelas + parágrafos da página 2 corretamente, mas não estrutura automaticamente os parágrafos em JSON chave-valor; serve como componente para uma camada LLM acima. ³ Tabula não possui OCR, e a página 2 dos dossiês é conteúdo imagem. ⁴ Copilot é proxy da família OpenAI; o resultado do ChatGPT captura o comportamento sem informação marginal.

Identificamos também — durante a sondagem de mercado em pesquisa externa — o **Azure Document Intelligence**, ferramenta não citada no brief original e que se mostrou determinante para a camada 2 da arquitetura final. Detalhamos seu papel arquitetural em §4.

---

## §2 — O que funcionou em cada uma

**Pipeline de referência em Python (a solução que construímos).** Implementamos a arquitetura híbrida recomendada em `06_reference_script/` (Azure DI Layout + Claude Sonnet 4.6 com *cross-validation* e trilha de auditoria). Medimos **100% de acurácia, zero alucinações e US$ 0,00934 por dossiê** em quatro PDFs: o do brief, F02 (missing-email), F07 (skewed page 2) e o *holdout* OOD `F09_brief_shape` — estrutura visualmente fiel ao brief, com dados de cliente completamente novos (Salvador/BA, financiamento de veículo). O *holdout* é metodologicamente importante: teste cego do *prompt* contra a estrutura real-shape do brief. Durante o desenvolvimento corrigimos uma falha de interpretação semântica no *prompt* (extração de valores compostos) com uma regra explícita de **extração literal**; o *holdout* F09 foi rodado já sob o *prompt* corrigido, sem ajustes posteriores. Detalhes e *history note* em `06_reference_script/notes.md`.

**LLMs *frontier* (ChatGPT, Claude, NotebookLM).** As três ferramentas extraíram corretamente os 32 campos do PDF de exemplo (página 1 + página 2), com zero alucinações em validação contra `01_field_map/gold_truth.json`. As latências medidas foram 11,8 s (ChatGPT), 10,46 s (Claude) e 22,23 s (NotebookLM); todas para *upload* + chat UI, incluindo renderização — via API, esperamos 2–4 s. A convergência de três LLMs independentes no mesmo PDF é um sinal forte de *cross-validation* para casos limpos.

**Power Automate + AI Builder.** O fluxo *Revelatio Debtor Extraction* obteve **92,8% médio no corpus sintético** (132 células avaliadas em F01, F02, F05, F06) com **zero alucinações**: em F02 (e-mail ausente) e F03 (telefone ausente), o AI Builder devolveu campos vazios em vez de inventar valores. A trilha de auditoria nativa do Power Automate atende ao Art. 6º X da LGPD (responsabilização) sem código adicional. Detalhes em `04_experiments/02_power_automate/notes.md`.

**Componentes determinísticos e OCR.** O Azure DI Layout reconheceu a estrutura de ambas as páginas (16 células de tabela na página 1, parágrafos identificados na página 2 do PDF de exemplo) sem qualquer treinamento prévio — comportamento *layout-tolerant* exatamente no ponto em que o AI Builder falha (`04_experiments/06_azure_di/notes.md`). O Tabula extraiu 100% da página 1 a custo zero, latência de 0,71–1,79 s por dossiê (`04_experiments/07_tabula/notes.md`).

---

## §3 — O que não funcionou

Antes de listar falhas específicas, é honesto declarar a principal limitação metodológica: **nosso corpus sintético compartilha rótulos de campo com os dossiês reais do Banco X, mas a única validação contra layout fiel ao PDF do brief foi a do *holdout* F09 que geramos nós mesmos** — não temos acesso a dossiês reais do Banco X. O F09 reduz materialmente o risco de surpresa em produção (estrutura visualmente idêntica ao brief, dados novos, 100% de acerto), mas não substitui validação sobre o conjunto real (ver `04_experiments/SCOREBOARD.md` §5 finding #2).

**Falha 1 — AI Builder *layout-sensitive* na página 2.** No PDF do brief, quatro campos da página 2 retornaram texto de rodapé como valor (por exemplo, *"Documento ficticio para teste técnico"* como `proof_reference`). O AI Builder pratica *template matching* sobre a distribuição de treino; a página 2 do exemplo está fora dela. Mitigação: somar uma camada *layout-tolerant* (Azure DI + LLM) — incorporada por padrão no caminho principal Python, ainda a adicionar como *connector* HTTP no caminho M365. Diagnóstico em `04_experiments/02_power_automate/notes.md` Fase 1.5.

**Falha 2 — Tabula não possui OCR.** 100% na página 1, **0% na página 2** (conteúdo imagem). Exclui-o como solução *standalone*, mantém-no como componente atraente na camada 1.

**Falha 3 — Erro de *parse* de data na fronteira Power Automate → Excel.** `12/02/2024` (12 de fevereiro BR) gravado como `2024-12-02` (2 de dezembro). Bug operacional do *connector* Excel, não do AI Builder. *Production-blocking* para deploy BR sem ajuste regional do *tenant*.

Cada falha é uma restrição de projeto: a primeira justifica a camada 2 (já inclusa no caminho principal); a segunda justifica Tabula como componente; a terceira justifica a fila HITL como rede de proteção.

---

## §4 — Qual ferramenta faz mais sentido para o caso

Recomendamos uma **arquitetura híbrida em duas camadas** — não uma ferramenta única. A página 1 é estruturada e tem camada de texto extraível; a página 2 é imagem com layout variável. Tratar as duas com o mesmo motor é a origem das falhas em §3. A implementação que **construímos e validamos empiricamente** é o pipeline em `06_reference_script/` — esse é o caminho principal. O caminho M365 com Power Automate é alternativa legítima, com a ressalva de que a camada 2 ainda precisa ser adicionada ao fluxo PA antes do *cutover*.

| Papel | Ferramenta recomendada | Justificativa empírica |
|---|---|---|
| Motor de extração e *cross-validation* (camada 1 + camada 2 + gate) | **Pipeline Python em `06_reference_script/`** | 100% em 4 PDFs (corpus de base + *holdout* OOD), 0 alucinações, US$ 0,00934/dossiê |
| OCR + estrutura da página 2 (ambos caminhos) | **Azure DI Layout** | *Layout-tolerant* onde AI Builder falha; reconheceu parágrafos do PDF de exemplo sem treino |
| Mapeamento campo-a-campo na página 2 | Claude API (Sonnet 4.6) | 100% no PDF de exemplo + *holdout* OOD; *prompt* Opção-B com extração literal |
| *Cross-validator* | Regra de consistência de nome entre páginas (Titular do comprovante de endereço e Pagador do comprovante bancário devem corresponder ao nome da página 1) | Sem essa camada, página 1 correta permite página 2 *garbage* (Fase 1.5 finding #5). O nome do cliente é o único *anchor* compartilhado entre as duas páginas dos dossiês — o *cross-validator* opera exclusivamente sobre ele |
| Extrator página 1 do caminho M365 (alternativo) | AI Builder Custom Extraction | 92,8% sintético com 0 alucinações no corpus F01–F06 |
| Orquestrador do caminho principal (a escolher) | n8n auto-hospedado, *cron* + pasta monitorada, ou *trigger* HTTP de aplicação web | Qualquer opção viável; n8n foi avaliado em análise documental (`02_tool_universe/05_n8n.md`) mas não construído no PoC. O motor foi orquestrado via CLI em `extract_dossier.py` |
| Orquestrador caminho M365 alternativo | Power Automate | Trilha de auditoria nativa, manutenção por paralegal |

A introdução do Azure DI Layout — ferramenta não listada no brief — é estrutural à recomendação: é o único componente testado que combina *layout-tolerance* com custo previsível (US$ 1,50 por 1.000 páginas, ~US$ 30 para o backlog inteiro). Sem ele, nenhum dos dois caminhos tem rota honesta para sair da falha *layout-sensitive* descrita em §3.

A síntese consolidada está em `04_experiments/SCOREBOARD.md` §3 e §6; os diagramas formais da arquitetura estão em `07_architecture/diagrams.md`.

---

## §5 — Como essa ferramenta seria utilizada no fluxo da equipe

A arquitetura existe em duas implementações paralelas, escolhidas conforme o perfil tecnológico do escritório. O ciclo HITL é compartilhado.

**Caminho principal — motor Python de referência (construído, validado e publicamente acessível).** O componente central é o pipeline em `06_reference_script/`, que implementa as duas camadas com *cross-validation* de nome entre páginas e trilha de auditoria, validado nos 4 PDFs descritos em §2. O motor é exposto via **interface web hospedada em `https://revelatio-demo.streamlit.app`** (Streamlit Community Cloud) que aceita upload de PDFs e oferece gravação automática em planilha Google compartilhada com o painel como destino opcional — código em `06_reference_script/app.py` + `06_reference_script/sheets_writer.py`, runbook de deploy em `DEPLOY.md` na raiz do repositório. O `extract_dossier.py` permanece como entrada CLI alternativa para uso *headless*. Para *batch* em produção sobre o backlog de 10k dossiês, a camada de orquestração fica a critério do escritório — opções viáveis incluem **n8n auto-hospedado** (escolha natural pelo perfil OSS + auditável, e a única dessas opções que avaliamos em análise documental), *cron* com pasta monitorada, ou *trigger* HTTP de uma aplicação web já existente; não construímos nenhuma delas no PoC. Referências: `02_tool_universe/05_n8n.md` e Diagrama 2 de `07_architecture/diagrams.md`.

**Caminho alternativo — M365 com Power Automate (escritórios já residentes em Microsoft 365).** Fluxo disparado pela chegada do PDF no SharePoint: AI Builder na página 1, Azure DI Layout + Claude API sobre a página 2 em casos de baixa confiança, *cross-validation* de nome entre páginas (Titular e Pagador da página 2 batem com o cliente da página 1), gravação em `dossiers.xlsx` (ou fila HITL). A camada da página 1 está construída e validada em Epic 5.2 (92,8% sintético, 0 alucinações); a camada da página 2 é especificada arquiteturalmente, deve ser adicionada como *connector* HTTP ao fluxo PA antes do *cutover* de produção. Vantagem operacional: manutenção *no-code* por paralegal. *Reference*: Diagrama 1 em `07_architecture/diagrams.md`.

**Ciclo HITL e *cross-validation*.** Quando uma linha falha na *cross-validation* (o Titular do comprovante de endereço ou o Pagador do comprovante bancário, por exemplo, não correspondem ao nome do cliente da página 1), o sistema marca `needs_review = TRUE` e roteia a linha para uma fila. A paralegal abre a linha — apenas os campos sinalizados precisam de revisão, com os demais já pré-preenchidos — e aprova, corrige ou rejeita. Cada ação gera registro em `audit.csv` com carimbo de tempo e identificador da revisora. Esse desenho está em `07_architecture/diagrams.md` §4.

**Rubrica de escolha do caminho.** Três entradas binárias (tem licenças M365? tem capacidade de desenvolvimento? tem ≥30 dossiês reais para treino?) determinam o caminho recomendado. Detalhe em `07_architecture/diagrams.md` §5. Escritórios sem M365 e sem capacidade técnica interna precisam de parceiro externo de implementação — o relatório é explícito quanto a isso, não há versão honesta da arquitetura que se opere sozinha nesse cenário.

---

## §6 — Possíveis limitações ou cuidados da solução

**LGPD — enquadramento e base legal.** A base legal primária é o **Art. 7º, V** (execução de contrato e procedimentos preliminares de cobrança); a base secundária é o **Art. 7º, IX** (legítimo interesse). O sistema é deliberadamente desenhado como **preparação de dados**, não decisão automatizada — toda decisão consequente (estratégia de cobrança, execução fiscal, oferta de acordo) é tomada por advogado a jusante da planilha. Esse enquadramento mantém o projeto fora da obrigação de revisão sob o **Art. 20**, condicionado à existência efetiva da camada HITL (`07_architecture/lgpd.md` §10). Os termos de uso da Anthropic (`anthropic.com/legal/commercial-terms` §B) e a documentação de privacidade do Azure Document Intelligence (verificados em 2026-05-11) confirmam que o conteúdo enviado via API não é usado para treinamento.

**Limitações metodológicas.** Três restrições: (i) o *holdout* F09 valida estrutura visualmente fiel ao brief, mas **ainda não testamos contra dossiês reais do Banco X**; (ii) n=1 sobre o PDF do brief; (iii) o Azure DI Custom Neural **não foi treinado** (requer 30+ dossiês reais). Consolidação em `04_experiments/SCOREBOARD.md` §5.


---

## §7 — Possível plano inicial de implementação

Propomos um plano em três fases, ancorado nos números empíricos das seções anteriores.

**Fase 1 — Provisionamento e *baseline* de dados (semanas 1–2).** Migração para Brasil Sul (M365 e Azure DI, se aplicável); assinatura do DPA da Anthropic; primeira versão do RIPD pelo DPO; coleta dos 30 dossiês reais para treino futuro do Custom Neural ou AI Builder. *Setup* do caminho principal: 2–3 dias de engenharia para escolher e integrar uma camada de orquestração (n8n, *cron* + pasta monitorada ou *trigger* HTTP) sobre o motor já validado, e configurar UI HITL com SSO. *Setup* do caminho alternativo M365: 1–2 dias para adicionar a *branch* de *fallback* da página 2 (Azure DI + Claude) ao fluxo Power Automate existente.

**Fase 2 — Piloto sobre o backlog (semanas 3–4).** Processamento dos 10.000 dossiês com a fila HITL ativa e a regra de *cross-validation* armada. Custo previsto de API: **R$ 457** (US$ 93,37 ao PTAX 4,8999, *venda* de 2026-05-08, fonte BCB Olinda). Tempo de relógio estimado em 3–6 horas com concorrência de 5–10 chamadas simultâneas, conforme item #2 do *checklist* em `06_reference_script/notes.md`. Comparativo da extração manual sobre o mesmo volume: **R$ 50.500** (10.000 × 6 min 44 s × R$ 45/h no ponto médio), com base na medição empírica n=1 em `07_architecture/manual_timing.md`. *Payback*: dia um. Razão **~110×**.

**Fase 3 — Endurecimento de produção (semanas 5–8).** Implementação do checklist de oito itens em `06_reference_script/notes.md` — *retry* com *backoff*, limitação de taxa, idempotência por *hash*, monitoramento de custo com alerta de teto, SSO no UI HITL, redação de CPFs em `audit.csv`, chamada explícita de `Delete Analyze Result` no Azure DI, *runbook* de incidentes. Treino do Custom Neural quando os 30 dossiês reais da Fase 1 estiverem rotulados; expectativa de redução marginal do custo de Claude na página 2.

A tabela abaixo, condensada de `07_architecture/roi.md` §5, mostra que a recomendação permanece robusta sob variação plausível de volume e taxa HITL.

| Volume anual | 5% HITL | 10% HITL | 20% HITL | Manual no ponto médio |
|---|---|---|---|---|
| 1.000 | R$ 118 | R$ 193 | R$ 343 | R$ 5.050 |
| 10.000 | **R$ 1.184** | **R$ 1.934** | **R$ 3.434** | **R$ 50.500** |
| 100.000 | R$ 11.843 | R$ 19.343 | R$ 34.343 | R$ 505.000 |

Em qualquer linha, a razão automatizado/manual permanece acima de 10×, o que torna a conclusão de viabilidade econômica insensível a estimativas pessimistas. **O script Python que executa a Fase 2 já existe e está disponível no *bundle* em `06_reference_script/`**, com README de execução, *test corpus* validado e o gerador do *holdout* OOD (`05_synthetic_data/generate_brief_shaped_ood.py`) reprodutível.

---

*Documentos de apoio (anexos do bundle):* `06_reference_script/` (script Python + audit log + *history note* da extração literal); `05_synthetic_data/` (gerador, PDFs e *gold* do *holdout* F09); `04_experiments/SCOREBOARD.md` (síntese empírica); `07_architecture/` (diagrams, roi, lgpd, manual_timing); `decisions.md` (ADR D-006).
