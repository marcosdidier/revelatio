# Brief Decoded — Take-Home "Implementador de IA & Automações"

> Source: `00_brief/brief_implementador_ia.pdf` (5 páginas, Recife, 07/05/2026).
> Purpose of this file: a single grep-able checklist mapping every "must" / "expected" / "diferencial" bullet from the brief to the deliverable that satisfies it. The relatório (Epic 8) will be cross-checked against this file before submission.
>
> Convention: `[ ]` open · `[~]` in progress · `[x]` done. Each box has an owner-task ID from `backlog.md`.

---

## §1 — Objetivo (evaluation criteria the hirer scores us on)

- [ ] **Capacidade de pesquisa e teste de ferramentas** — Epics 2, 3, 5 — `[Pesquisa]`
- [ ] **Organização e clareza na solução proposta** — Epics 0, 7, 8 — `[Clareza]`
- [ ] **Raciocínio prático** — Epics 1, 5, 7 — `[Raciocínio]`
- [ ] **Capacidade de implementação** — Epic 6 — `[Implementação]`
- [ ] **Comunicação e explicação da solução** — Epics 8, 9 — `[Comunicação]`
- [ ] **Proatividade na busca de alternativas** — Epic 3 — `[Proatividade]`

## §2 — Contexto do Desafio

- [x] Understand: ~10.000 PDFs de clientes devedores de banco, estrutura semelhante.
- [x] Understand: extração manual atual exige ~10 pessoas por vários dias.
- [x] Understand: solução deve consolidar dados em **planilha Excel**.
- [x] Understand: must cover **dados da primeira página + comprovantes da segunda página** (image-based).
- [ ] Decision recorded: which extraction layer per page (WH-001 in `decisions.md`).

## §3 — Campos esperados na planilha (13 obrigatórios + livre p/ comprovantes)

Page-1 fields (13 mandatory):
- [x] Nome do cliente — Task 1.2
- [x] CPF — Task 1.2
- [x] Telefone — Task 1.2
- [x] E-mail — Task 1.2
- [x] Endereço — Task 1.2
- [x] Número do contrato — Task 1.2
- [x] Produto — Task 1.2
- [x] Valor original — Task 1.2
- [x] Saldo atualizado — Task 1.2
- [x] Dias em atraso — Task 1.2
- [x] Status — Task 1.2
- [x] Última tentativa de contato — Task 1.2
- [x] Responsável interno — Task 1.2

Page-2 fields (open-ended — "informações identificadas nos comprovantes/documentos anexados"):
- [x] Comprovante de endereço (titular, endereço, bairro, CEP, referência, mês/ano, valor, código de barras) — Task 1.2
- [x] Comprovante bancário (banco, agência, conta, data, tipo, pagador, recebedor, valor pago, autenticação) — Task 1.2
- [ ] Bonus fields surfaced (data de nascimento, CEP page 1, data de contratação) — Task 1.2

## §4 — Ferramentas sugeridas (mínimo 3 testadas)

- [ ] ChatGPT — Epic 2.1 + Epic 5.2 — `[Pesquisa]`
- [ ] Claude — Epic 2.2 + Epic 5.3 — `[Pesquisa]`
- [ ] NotebookLM — Epic 2.3 + Epic 5.7 — `[Pesquisa]`
- [ ] Make — Epic 2.4 — `[Pesquisa]`
- [ ] n8n — Epic 2.5 + Epic 5.5 — `[Pesquisa]` `[Diff:AltFlow]`
- [ ] Tabula — Epic 2.6 + Epic 5.4 — `[Pesquisa]`
- [ ] Power Automate — Epic 2.7 (analytical only, see D-004) — `[Pesquisa]`
- [ ] Microsoft Copilot — Epic 2.8 (analytical only, see D-004) — `[Pesquisa]`
- [ ] Comparison matrix consolidating all 8 — Epic 2.9
- [ ] Hands-on tests of ≥ 6 tools (we exceed the "minimum 3" — including chosen primary Power Automate in 5.2 and its Azure DI cross-validator in 5.7) — Epic 5

> Brief explicitly accepts: "Caso alguma ferramenta não faça sentido para o contexto, também será válido explicar o motivo do não uso." We exploit this: NotebookLM, Make, Power Automate, Microsoft Copilot get reasoned "why-not" or "conditional-fit" verdicts.

## §5 — Diferenciais (explicit bonus criteria from the brief)

- [ ] **Apresentar uma ferramenta não listada inicialmente** — Epic 3 (≥ 8 tools) + Epic 5.6 Azure DI hands-on — `[Diff:UnlistedTool]`
- [ ] **Propor um fluxo alternativo de automação** — Epic 7.2 (n8n alt flow) — `[Diff:AltFlow]`
- [ ] **Criar um script básico para auxiliar no processo** — Epic 6 (full Python pipeline) — `[Diff:Script]`
- [ ] **Demonstrar preocupação com escala e organização operacional** — Epics 4, 7.4, 7.6 — `[Diff:Escala]`
- [ ] **Estruturar uma solução pensando em uso real no contexto do escritório** — Epics 7.3, 7.5, 7.6, 8 PT-BR — `[Diff:UsoReal]`

> Note from brief: "A busca e sugestão de ferramentas adicionais será considerada um diferencial **importante**." Bolded in the original — we treat this as the highest-leverage differential.

## §6 — Entrega 1: Relatório (PT-BR)

The relatório must contain (verbatim from brief):
- [ ] Ferramentas testadas — Epic 8.1 §1
- [ ] O que funcionou em cada uma — Epic 8.1 §2
- [ ] O que não funcionou — Epic 8.1 §3
- [ ] Qual ferramenta faz mais sentido para o caso — Epic 8.1 §4
- [ ] Como essa ferramenta seria utilizada no fluxo da equipe — Epic 8.1 §5 (uses Epic 7.6 playbook)
- [ ] Possíveis limitações ou cuidados da solução — Epic 8.1 §6 (uses Epic 7.5 risks + 7.3 LGPD)
- [ ] Possível plano inicial de implementação — Epic 8.1 §7 (uses Epic 7.1 architecture + 7.4 ROI)

## §7 — Entrega 2: Vídeo (≤ 5 min)

The video must show (verbatim from brief):
- [ ] Qual solução foi escolhida — Epic 9.1 act 1
- [ ] Por que ela foi escolhida — Epic 9.1 act 2
- [ ] Como funcionaria na prática — Epic 9.1 act 3 + 4 (live demo)
- [ ] Como a equipe utilizaria essa solução — Epic 9.1 act 4
- [ ] O que seria necessário para implementar o fluxo corretamente — Epic 9.1 act 5
- [ ] Format livre (Loom recommended) — Epic 9.4

## §8 — Formato de Entrega

- [ ] Bundle via Google Drive **OR** `.zip` — Epic 8.4
- [ ] Bundle contém: Relatório, Vídeo, Script, Materiais adicionais — Epic 8 totals
- [ ] README in PT-BR at the top of the bundle (extra polish) — Epic 8.2

## §9 — Prazo

- [x] Brief sent: **2026-05-07**
- [ ] Submitted **before 2026-05-13 17:00 BRT** — Epic 10.3
- [ ] Aim for ≥ 6h buffer (submit by 2026-05-13 11:00 BRT)

---

## Quick-grade pass before submission (Epic 10.1 will use this)

Run: `grep -c "\[ \]" 00_brief/spec_decoded.md` — must equal **0** before submitting.
Run: `grep -c "\[~\]" 00_brief/spec_decoded.md` — must equal **0** before submitting.
