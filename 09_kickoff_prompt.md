# Epic 9 — Kickoff Prompt (paste into a fresh Claude Code session)

> **Use**: open Claude Code in `/Users/marcosdidier/testeRevelatio/` in a new conversation. Paste the block under "## The prompt" verbatim as the first message. The rest of this file is context for *you* (the human) — not part of the paste.

---

## The prompt

```
Continue Project Revelatio. Read SESSION_RESUME.md and 09_kickoff_prompt.md
first — they have the complete status and Epic 9 specification.

Where we are: Epics 0–8 are done. The relatório PT-BR is at
08_deliverables/relatorio.md (+ relatorio.pdf at the same path, ready to
bundle). The reference Python pipeline at 06_reference_script/ is the
*caminho principal* of the recommendation per ADR D-006 (2026-05-12),
empirically validated at 100% accuracy on a 3-PDF baseline plus an OOD
holdout (F09_brief_shape) with 0 hallucinations and $0.00934 per dossier
($93 / R$ 457 for the full 10k backlog, ~110× cheaper than the manual
baseline of R$ 50,500). M365 + Power Automate is positioned as the
*caminho alternativo* for firms preferring no-code maintenance.

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

There are three open questions to raise via AskUserQuestion before
finalizing the outline — they're listed in 09_kickoff_prompt.md under
"Open questions for the user". Get answers, then plan.
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
| 4 | Synthetic PDFs + golds (8 fixtures) | `05_synthetic_data/` |
| 5.2–5.9 | Tool hands-on tests + SCOREBOARD synthesis | `04_experiments/` |
| 6 | Reference Python pipeline + Streamlit demo UI | `06_reference_script/` |
| 7 | Architecture / LGPD / ROI stakeholder docs | `07_architecture/` |
| 8 | Relatório PT-BR (markdown + PDF) | `08_deliverables/` |

### Act → artifact mapping (the messaging backbone)

| Video act | Source artifact for facts |
|---|---|
| Act 1 — Qual solução | `08_deliverables/relatorio.md` Sumário Executivo + §4 |
| Act 2 — Por que (com âncoras quantitativas) | Relatório §1 (tabela das 9 ferramentas) + §3 (falhas) + §4 (justificativa) + `04_experiments/SCOREBOARD.md` §1 |
| Act 3 — Como funcionaria na prática (DEMO) | `06_reference_script/app.py` (Streamlit) + `extract_dossier.py` (CLI) + um PDF de teste (sugestão: `05_synthetic_data/pdfs/F09_brief_shape.pdf` para mostrar OOD) |
| Act 4 — Como a equipe utilizaria | Relatório §5 (caminho principal + alternativo + HITL + rubrica) + `07_architecture/diagrams.md` §4 (HITL lifecycle) |
| Act 5 — O que seria necessário para produção | Relatório §6 (gaps) + §7 (plano 3 fases) + `07_architecture/lgpd.md` §11 (10 gaps de produção) + `06_reference_script/notes.md` "Production hardening checklist" |

### Demo flow for Act 3 (the load-bearing part of the video)

Sugestão de cue sheet em ≤ 2 minutos:

1. **0:00–0:10** — Tela inicial do Streamlit (`.venv/bin/python -m streamlit run 06_reference_script/app.py`). Mostrar título.
2. **0:10–0:25** — Arrastar `F09_brief_shape.pdf` (ou o PDF do brief) para o uploader. Botão "▶ Extrair".
3. **0:25–1:30** — Enquanto roda (~11 s real), narrar a arquitetura em duas camadas: página 1 determinística + página 2 OCR + LLM + *cross-validation*. Aqui vale fazer edição para cortar o tempo de espera.
4. **1:30–1:50** — Mostrar a tabela `dossiers.csv` na tela do Streamlit; destacar os 32 campos preenchidos + a coluna `needs_review = FALSE`.
5. **1:50–2:00** — Abrir o expander "Detalhes operacionais"; mostrar `audit.csv` com latência, custo (~$0,0093), `cross_val_consistent = TRUE`.

Se rolar tempo, encaixar uma demonstração rápida da fila HITL: editar uma célula do CSV para simular *mismatch*, mostrar `needs_review = TRUE`. Opcional.

### Diferenciais to weave in (brief §5 — explicit bonus criteria)

Os diferenciais já estão refletidos nas escolhas arquiteturais — o vídeo os reforça ao falar dos atos:

| Diferencial | Onde aparece naturalmente no vídeo |
|---|---|
| Ferramenta não listada no brief | Act 1 + Act 2 (Azure DI Layout como peça estrutural) |
| Fluxo alternativo de automação | Act 4 (caminho M365 mostrado como alternativa real) |
| Script básico | Act 3 inteiro (o que está rodando na tela) |
| Preocupação com escala e organização operacional | Act 4 (fila HITL) + Act 5 (plano em fases) |
| Solução pensada para uso real | Act 5 (gaps LGPD + hardening checklist) |

### Open questions for the user (Epic 9 session should ask via AskUserQuestion before finalizing the outline)

1. **Ferramenta de gravação**: Loom (no navegador, link já hosted, mais fácil de compartilhar — recomendado pelo brief), QuickTime / OBS (arquivo MP4 local, mais controle sobre edição), ou ScreenStudio / similar (Mac-native, edição de cortes embutida)?

2. **PDF usado na demo do Act 3**: o do brief (`00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` — a banca já conhece, evita dúvida sobre layout) ou o *holdout* OOD (`05_synthetic_data/pdfs/F09_brief_shape.pdf` — dados frescos, demonstra empiricamente a generalização e oferece narrativa mais forte)? Recomendação: F09, pelo argumento metodológico — mas confirme.

3. **Tom da narração**: scripted (lido em voz alta a partir do `script.md`, mais controle de tempo e clareza PT-BR) ou extempore (mais natural, porém maior risco de estourar 5 min)? Recomendação: scripted com 2–3 ensaios; gravar take final lendo de monitor secundário ou teleprompter no celular. Confirme.

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
