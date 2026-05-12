# Epic 9 — Kickoff Prompt (paste into a fresh Claude Code session)

> **Use**: open Claude Code in `/Users/marcosdidier/testeRevelatio/` in a new conversation. Paste the block under "## The prompt" verbatim as the first message. The rest of this file is context for *you* (the human) — not part of the paste.

---

## The prompt

```
Continue Project Revelatio. Read SESSION_RESUME.md and 09_kickoff_prompt.md
first — they have the complete status and Epic 9 specification.

Where we are: Epics 0–8.5 are done. The relatório PT-BR is at
08_deliverables/relatorio.md (+ relatorio.pdf at the same path, ready to
bundle). The reference Python pipeline at 06_reference_script/ is the
*caminho principal* of the recommendation per ADR D-006 (2026-05-12),
empirically validated at 100% accuracy on a 3-PDF baseline plus an OOD
holdout (F09_brief_shape) with 0 hallucinations and $0.00934 per dossier
($93 / R$ 457 for the full 10k backlog, ~110× cheaper than the manual
baseline of R$ 50,500). M365 + Power Automate is positioned as the
*caminho alternativo* for firms preferring no-code maintenance. **The
engine is publicly deployed at https://revelatio-demo.streamlit.app
(Epic 8.5 / D-007) with Google Sheets write-back — Act 3 of the video
should demo the live URL, not localhost.**

What I'm starting today: Epic 9 — Vídeo PT-BR ≤ 5 minutos. The brief
prescribes five act-questions verbatim (00_brief/spec_decoded.md §7):

  1. Qual solução foi escolhida
  2. Por que ela foi escolhida
  3. Como funcionaria na prática (demo ao vivo)
  4. Como a equipe utilizaria essa solução
  5. O que seria necessário para implementar o fluxo corretamente

Format livre (Loom recomendado pelo brief). Output target: a single
≤ 5-min PT-BR video + the supporting script.md, shot_list.md and
recording_notes.md inside 09_video/.

Pacing for today: structured planning first, then recording. We'll nail
the PT-BR script section by section with explicit timing budgets, then
choose the recording tool, then I record. Act 3 (the live demo) must fit
inside ≤ 2 minutes — it's the longest single act and the one where
runtime overshoots are most likely.

Anchor every quantitative claim in the script to a specific artifact —
same discipline as Epics 7 and 8. The relatório PDF
(08_deliverables/relatorio.md / relatorio.pdf) is the canonical source
of messaging; the video paraphrases, doesn't re-derive.

Start by: entering plan mode, reading 08_deliverables/relatorio.md
(source of messaging), 00_brief/spec_decoded.md §7 (verbatim brief
requirements), 06_reference_script/README.md (how the demo runs), and
proposing the video's act-by-act script outline — timing budget per act,
key claim per act anchored to a relatório section, demo cue sheet for
Act 3. Don't start writing PT-BR script prose until I approve the
outline.

The three pre-recording decisions were already answered on 2026-05-12
(see 09_kickoff_prompt.md "Decisions locked in"):
- Recording tool: Loom (browser-hosted, brief-recommended)
- Demo PDF: BOTH — brief PDF first, then F09_brief_shape OOD second
- Narration tone: scripted, read from 09_video/script.md

Start by entering plan mode, reading 08_deliverables/relatorio.md
(source of messaging) and proposing the script outline — timing budget
per act, key claim per act anchored to a relatório section, and the
two-PDF demo cue sheet for Act 3. Don't start writing PT-BR script
prose until I approve the outline.
```

---

## Context for the human (you)

### What's done (don't redo)

| Epic | Deliverable | Where |
|---|---|---|
| 0 | Setup + docs discipline | repo root |
| 1 | Ground truth + scoring rubric | `01_field_map/` |
| 2 | 8 tool dossiers + comparison matrix | `02_tool_universe/` |
| 3 | External research sprint | `03_external_research/` |
| 4 | Synthetic PDFs + golds (8 fixtures + F09 OOD holdout) | `05_synthetic_data/` |
| 5.2–5.9 | Tool hands-on tests + SCOREBOARD synthesis | `04_experiments/` |
| 6 | Reference Python pipeline + Streamlit demo UI | `06_reference_script/` |
| 7 | Architecture / LGPD / ROI stakeholder docs | `07_architecture/` |
| 8 | Relatório PT-BR (markdown + PDF) | `08_deliverables/` |
| **8.5** | **Streamlit Cloud deploy + Google Sheets write-back** | **`https://revelatio-demo.streamlit.app` + `06_reference_script/app.py` + `sheets_writer.py` + `DEPLOY.md`** |

### Act → artifact mapping (the messaging backbone)

| Video act | Source artifact for facts |
|---|---|
| Act 1 — Qual solução | `08_deliverables/relatorio.md` Sumário Executivo + §4 |
| Act 2 — Por que (com âncoras quantitativas) | Relatório §1 (tabela das 9 ferramentas) + §3 (falhas) + §4 (justificativa) + `04_experiments/SCOREBOARD.md` §1 |
| Act 3 — Como funcionaria na prática (DEMO) | **`https://revelatio-demo.streamlit.app` (URL viva, Epic 8.5 / D-007)** + um PDF de teste (sugestão: `05_synthetic_data/pdfs/F09_brief_shape.pdf` para mostrar OOD) + a planilha Google compartilhada como *closer* visual |
| Act 4 — Como a equipe utilizaria | Relatório §5 (caminho principal + alternativo + HITL + rubrica) + `07_architecture/diagrams.md` §4 (HITL lifecycle) |
| Act 5 — O que seria necessário para produção | Relatório §6 (gaps) + §7 (plano 3 fases) + `07_architecture/lgpd.md` §11 (10 gaps de produção) + `06_reference_script/notes.md` "Production hardening checklist" |

### Demo flow for Act 3 (the load-bearing part of the video)

Cue sheet ≤ 2 minutos com **dois PDFs** (decisão 2026-05-12: brief primeiro para familiaridade, F09 OOD em seguida para argumento de generalização). Acelerar tempo de espera de extração em pós-produção no Loom:

1. **0:00–0:08** — Abrir `https://revelatio-demo.streamlit.app` no navegador. Título "Revelatio — Extração de Dossiês"; barra superior do Streamlit Cloud confirma que é app hospedado.
2. **0:08–0:18** — Arrastar `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` (o PDF do brief) → "▶ Extrair 1 dossiê(s)". Frase de transição: *"primeiro o PDF que vocês conhecem"*.
3. **0:18–1:00** — Enquanto roda (~11 s), narrar a arquitetura em duas camadas: página 1 determinística (Azure DI Layout) + página 2 (Claude Sonnet 4.6) + *cross-validation* de nome entre páginas. **Acelerar este trecho em 4×–6× na edição do Loom**.
4. **1:00–1:10** — Mostrar resultado com cabeçalhos PT-BR (Nome do cliente, CPF, Comprovante — titular, ...); destacar 32 campos + "Revisar" = FALSE. Frase: *"100% no PDF do brief, zero alucinações"*.
5. **1:10–1:20** — *Refresh* da página (ou nova aba) e arrastar `05_synthetic_data/pdfs/F09_brief_shape.pdf`. Frase: *"agora um PDF que o sistema nunca viu — mesma estrutura, dados de cliente completamente novos"*. ▶ Extrair.
6. **1:20–1:35** — Acelerar a espera no Loom. Mostrar resultado F09: 32 campos preenchidos, "Revisar" = FALSE. Frase: *"também 100%, também zero alucinações — o sistema generaliza"*.
7. **1:35–1:50** — Clicar "📤 Enviar para Planilha Google". Mostrar mensagem de sucesso + link "Abrir planilha". Clicar no link.
8. **1:50–2:00** — Planilha aberta em nova aba: mostrar **as duas linhas** (brief + F09) com `Extraído em (UTC)` distinto. Frase de fechamento do Act 3: *"o painel pode clicar nessa planilha depois do vídeo e confirmar"*.

A planilha Google é o *closer* visual mais forte: artefato fora do Streamlit, "spreadsheet" é o substantivo que o brief usa (*"em planilha Excel"*), e é o que a banca pode clicar depois do vídeo para confirmar que rodou. Se rolar tempo (improvável com dois PDFs), encaixar audit log: expander "Detalhes operacionais" → latência, custo (~$0,0093), `cross_val_consistent = TRUE`. Opcional.

### Diferenciais to weave in (brief §5 — explicit bonus criteria)

Os diferenciais já estão refletidos nas escolhas arquiteturais — o vídeo os reforça ao falar dos atos:

| Diferencial | Onde aparece naturalmente no vídeo |
|---|---|
| Ferramenta não listada no brief | Act 1 + Act 2 (Azure DI Layout como peça estrutural) |
| Fluxo alternativo de automação | Act 4 (caminho M365 mostrado como alternativa real) |
| Script básico | Act 3 inteiro (o que está rodando na tela) |
| Preocupação com escala e organização operacional | Act 4 (fila HITL) + Act 5 (plano em fases) |
| Solução pensada para uso real | Act 5 (gaps LGPD + hardening checklist) |

### Decisions locked in (answered 2026-05-12 — Epic 9 fresh session should NOT re-ask)

1. **Ferramenta de gravação: Loom.** Browser-native + hosted link + brief-recommended. Use o *speed up* embutido para acelerar trechos de espera de extração no Act 3.
2. **PDF usado na demo do Act 3: AMBOS** — primeiro `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` (familiaridade para a banca), depois `05_synthetic_data/pdfs/F09_brief_shape.pdf` (argumento de generalização: estrutura idêntica, dados novos, também 100%). Cue sheet detalhado na seção anterior cabe nos 2 min porque acelera as esperas em pós-produção.
3. **Tom da narração: scripted**, lido de `09_video/script.md`. 2–3 ensaios antes do take final; gravar lendo de monitor secundário ou teleprompter no celular para manter contato visual com a câmera. Evita estouro de 5 min e hesitações em pontos técnicos (LGPD Art. 7º V, números PTAX).

### Pacing guidance

Same as Epics 7 and 8: depth + insights welcome during the script-writing phase (analytical pause), short bullet-form messages during the recording phase (hands-on execution). Don't fabricate causal narratives if any number in the script surprises — re-check against the relatório or `06_reference_script/notes.md` first.

The auto-memory's 5 feedback rules still apply in the new session (they load automatically).

### Estimated time

~2–3 horas total — ~1 h para script + cue sheet, ~30 min para ensaiar, ~1 h para gravar (várias takes) + edição básica para cortar o tempo de espera no Act 3.

### Final gates before Epic 9 ships (run before considering Epic 9 done)

```bash
# 1. Video length ≤ 5:00
# (visual check — Loom shows runtime in the dashboard; QuickTime in the title bar)

# 2. All 5 acts present in script.md
grep -cE '^## Act [1-5]' 09_video/script.md   # must equal 5

# 3. Brief checklist closed for §7 (vídeo)
grep -n "^- \[ \] .*Epic 9" 00_brief/spec_decoded.md   # must be empty

# 4. Bundle items ready: relatorio.pdf + script + video file/link
ls 08_deliverables/relatorio.pdf 09_video/script.md
```

After Epic 9 ships, Epic 10 (QA + bundle + submit) is all that remains. Deadline 2026-05-13 17:00 BRT.
