# Session Resume — Project Revelatio

> **Read this first** when starting a fresh Claude Code conversation in this directory.

## What this project is
Take-home challenge: **Implementador de IA & Automações** for a Brazilian law firm. Automate extraction of ~10k debtor-PDF dossiers (Banco X) into Excel. Deadline **2026-05-13 17:00 BRT**. PT-BR deliverables, EN internal artifacts.

## Status snapshot (as of 2026-05-10, end-of-day)

| Epic | Status |
|---|---|
| 0 — Setup & docs discipline | ✅ done |
| 1 — Ground truth + scoring rubric | ✅ done |
| 2 — Tool universe (8 dossiers + matrix) | ✅ done |
| 3 — External research sprint | ✅ done |
| 4 — Synthetic PDFs + golds (8 fixtures, .venv at root) | ✅ done |
| **5.2 — Power Automate hands-on** | ✅ **done — avg 92.8% on synthetic test, 0 hallucinations** |
| **5.3 / 5.4 / 5.5 — LLM round-robin (ChatGPT, Claude, NotebookLM)** | ✅ **done — all 3 scored 100% on brief PDF, 0 hallucinations** |
| 5.6 — Copilot | ⏭️ skipped (OpenAI-family proxy via ChatGPT; documented by spec) |
| **5.7 — Azure DI Layout** | ✅ **done — page-2 layout-tolerant; NOT the source of PA hallucination bug** |
| **5.8 — Tabula (OSS hands-on)** | ✅ **done — 16/16 page-1 cells, 0 page-2 (no OCR); class-level finding** |
| **5.9 — Scoreboard synthesis** | ✅ **done — `04_experiments/SCOREBOARD.md` (source-of-truth for relatório §4)** |
| 5.10 — Skipped: Make + n8n full hands-on (covered via dossiers + diagrams instead) | — |
| 6 — Reference Python script | ⏳ pending (~3-4h) |
| 7 — Architecture / LGPD / ROI | ⏳ pending (~2h) |
| 8 — Relatório PT-BR | ⏳ pending (~4-6h) |
| 9 — Video ≤ 5 min PT-BR | ⏳ pending (~2-3h) |
| 10 — QA & submission | ⏳ pending |

**Time remaining**: ~2.5 days. Reserve 1 full day for Epics 8 + 9 + 10. Research budget: ~1.5 days.

## Where we left off — exact next step

**Run the 3 LLMs (5.3 ChatGPT, 5.4 Claude, 5.5 NotebookLM) on the brief example PDF using the shared prompt. Save each output JSON. Then I run the scoring script.**

### Per-tool procedure (same for all 3, ~20-30 min each)

1. Open the LLM:
   - ChatGPT → `chatgpt.com`
   - Claude → `claude.ai`
   - NotebookLM → `notebooklm.google.com` (use "Add sources" instead of paperclip)
2. Start a NEW conversation.
3. Upload PDF: `/Users/marcosdidier/testeRevelatio/00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf`
4. Paste the prompt from `04_experiments/shared_llm_prompt.md` (the full PT-BR prompt section).
5. Time the response (note latency in seconds).
6. Copy the JSON response. Save to:
   - ChatGPT → `04_experiments/03_chatgpt/output.json`
   - Claude → `04_experiments/04_claude/output.json`
   - NotebookLM → `04_experiments/05_notebooklm/output.json`
7. Note: latency, model version, cost class, whether output was clean JSON or wrapped.

### After all 3 outputs saved, run

```
.venv/bin/python 04_experiments/score_json_against_gold.py 04_experiments/03_chatgpt/output.json
.venv/bin/python 04_experiments/score_json_against_gold.py 04_experiments/04_claude/output.json
.venv/bin/python 04_experiments/score_json_against_gold.py 04_experiments/05_notebooklm/output.json
```

Each prints a verdict + writes `*_scorecard.json` next to the input.

## Key findings already captured (do NOT redo)

From Epic 5.2 (`04_experiments/02_power_automate/notes.md`):

1. **Page-1 extraction is robust** (~96% AI Builder accuracy report; 100% visual on synthetic test).
2. **Page-2 extraction is layout-sensitive** — works on training-distribution layouts, fails on visually-different ones (the brief example PDF page 2 produced footer text and pagination markers as field values).
3. **Anti-hallucination behavior confirmed** — F02 missing-email and F03 missing-phone correctly returned EMPTY, not invented values. **0 hallucinations across 132 cells** on the synthetic test set.
4. **`Data de contratação` locale-misparse bug** — `12/02/2024` (BR = Feb 12) extracted as `2024-12-02` (Dec 2). Bug originates in Power Automate → Excel boundary, not AI Builder. Production-blocking for BR deployment unless tenant region is BR or date pre-formatted.
5. **Single-field gating insufficient** — CPF confidence 0.99 routed example PDF to Verdadeiro despite 4 page-2 fields being garbage. Production needs per-page or cross-validation gating.
6. **Methodological gap to own honestly in relatório §3**: our `generate_pdfs.py` synthetic corpus shares field LABELS but not VISUAL LAYOUT with the brief example. Real production deployment requires real Banco X dossiers as training data (~30-100 docs).

## Strategic angles already locked in

- **Power Automate + AI Builder** = primary recommendation FOR M365-resident firms with real training data + cross-validation rules layered on
- **n8n self-hosted + Claude API** = alternative recommendation for non-M365 firms (Epic 6 reference Python script will demonstrate)
- **Azure DI Custom Neural** = page-2 cross-validator (Epic 5.7, layout-tolerant model)
- **Two-layer routing** insight: page 1 deterministic, page 2 OCR — empirically validated in Phase 1.5 + Phase 3
- **HITL queue + cross-validation rules** are explicit deliverables
- **LGPD posture, ROI math at 10k scale** are explicit deliverables in Epic 7

## Key files to know

| File | Purpose |
|---|---|
| `backlog.md` | Master plan, 11 epics |
| `decisions.md` | ADRs (D-001 lang, D-002 budget, D-003 synth corpus, D-004 M365, D-005 Power Automate primary) |
| `lessons.md` | Per-project learnings |
| `01_field_map/gold_truth.json` | Brief example PDF gold (used for LLM scoring) |
| `01_field_map/scoring_rubric.md` | Grading rules (encoded in scoring scripts) |
| `04_experiments/shared_llm_prompt.md` | The PT-BR prompt for ChatGPT/Claude/NotebookLM round-robin |
| `04_experiments/score_json_against_gold.py` | Generic scorer (LLM JSON output → scorecard) |
| `04_experiments/02_power_automate/score_excel_against_gold.py` | Power Automate scorer (Excel → scorecard) |
| `04_experiments/02_power_automate/scorecard.json` | PA test results (92.8% avg) |
| `04_experiments/02_power_automate/notes.md` | Full Phase 0–5 walkthrough notes (read for relatório draft) |
| `04_experiments/02_power_automate/setup/create_debtor_excel.py` | Reproducibility for Excel headers |
| `05_synthetic_data/pdfs/` | 8 synthetic PDFs (F01–F08) |
| `05_synthetic_data/gold/` | Matching gold JSONs |

## Tenant info (for Power Automate / SharePoint references)

- M365 tenant: `revelatiotest2026.onmicrosoft.com` (US region — chosen to bypass CNPJ requirement)
- SharePoint site: `https://revelatiotest2026.sharepoint.com/sites/revelatiotest`
- Trial expires: **2026-06-08** (calendar reminder set to cancel)
- AI Builder model: trained 2026-05-09, published, "Dossie_Revelatio" collection
- Power Automate flow: "Revelatio Debtor Extraction" — built end-to-end, working

## How to resume in a new conversation

1. Open Claude Code in `/Users/marcosdidier/testeRevelatio/`
2. Say: **"Continue Project Revelatio. Read SESSION_RESUME.md, then pick up at Epic 5.3-5.5 LLM round-robin — I'm ready to run [tool name] / I have output ready at [path]."**
3. Auto-memory will load 5 feedback rules automatically:
   - Explain artifacts before writing them
   - Propagate strategic choices immediately
   - Defer artifact updates until user pauses
   - Don't fabricate analytical narratives — ask for specific outputs
   - During execution, default to numbered click steps (no narrative)

## Pacing preferences (carried forward)

- Step-by-step in chat for hands-on tests
- PT-BR deliverables, EN backlog
- Pair-testing: user provides accounts, AI prepares prompts and scoring
- During execution: numbered steps, no insights
- During analysis pauses: depth + insights welcome

## Git state

- Initialized but **not committed yet** (per user choice). 50+ files staged + new files from Phase 5. Decide when to first commit.

## What to NOT redo

- Don't re-build the Power Automate flow — it's working, captured in notes
- Don't re-train the AI Builder model — published, captured
- Don't rewrite backlog/decisions — just update as we go
- Don't re-do tool dossiers or comparison matrix — complete
- Don't re-generate synthetic PDFs — committed in `05_synthetic_data/pdfs/`
- Don't re-run F02/F03/F04/F08 through Power Automate — scorecard already computed
