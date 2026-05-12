# Session Resume — Project Revelatio

> **Read this first** when starting a fresh Claude Code conversation in this directory.

## What this project is
Take-home challenge: **Implementador de IA & Automações** for a Brazilian law firm. Automate extraction of ~10k debtor-PDF dossiers (Banco X) into Excel. Deadline **2026-05-13 17:00 BRT**. PT-BR deliverables, EN internal artifacts.

## Status snapshot (as of 2026-05-11, late morning — Epic 7 completed at ~11:50 BRT)

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
| **6 — Reference Python script (+ Streamlit UI)** | ✅ **done — 100% on 3-PDF baseline + OOD holdout F09, 0 hallucinations, ~$93/10k (post-2026-05-12 literal-extraction prompt)** |
| **7 — Architecture / LGPD / ROI** | ✅ **done — 4 docs in `07_architecture/`, all WebFetch-verified, R$50k → R$436 ROI locked in** |
| 8 — Relatório PT-BR | ⏳ pending (~4-6h) — **see `08_kickoff_prompt.md` for fresh-session kickoff** |
| 9 — Video ≤ 5 min PT-BR | ⏳ pending (~2-3h) |
| 10 — QA & submission | ⏳ pending |

**Time remaining**: ~2 days (deadline 2026-05-13 17:00 BRT). Comfortable pace — all empirical work + architecture/ROI/LGPD writing done. Reserve 1 full day for Epics 8 + 9 + 10.

## Where we left off — exact next step

**Epic 8 — Relatório PT-BR.** All empirical evaluation + stakeholder docs are done (Epics 0–7 committed). Epic 8 produces the take-home deliverable: a PT-BR relatório consolidating everything for the law firm's hiring panel.

**Recommended approach**: open a fresh Claude Code session and use the standalone kickoff prompt at **`08_kickoff_prompt.md`**. It is self-contained — gives a fresh session the brief's prescribed 7-section structure, section-to-artifact mappings, the diferenciais to weave in, and the open questions to ask via AskUserQuestion before drafting.

### Epic 7 — What was delivered (2026-05-11)

All four documents in `07_architecture/`, committed as `1d8d791`:

1. **`07_architecture/diagrams.md`** (239 lines) — 4 Mermaid blocks (M365 path, non-M365 path, cross-validation flow, HITL lifecycle) + decision rubric + anchors index.
2. **`07_architecture/roi.md`** (179 lines) — $93.37 / R$ 457 at 10k dossiers vs. R$ 50,500 manual baseline at midpoint labor rate. ~110× cost ratio at midpoint, >10× even at 20% HITL. (Updated 2026-05-12 from $88.60 / R$ 434 / 116× after the literal-extraction prompt fix added ~123 input tokens per call.)
3. **`07_architecture/lgpd.md`** (302 lines) — 12-section article-by-article posture (Art. 6, 7, 18, 20, 33–36, 46–49) + 10-item production gaps checklist. Anthropic + Azure DI policy URLs WebFetch-verified.
4. **`07_architecture/manual_timing.md`** (58 lines) — empirical paralegal baseline: 6 min 44 sec on one PDF using copy-paste-page-1 + manual-page-2 two-tab workflow. n=1, honestly disclosed. The two-page asymmetry mirrors the architecture's two-layer routing.

**Key Epic 7 findings to carry into Epic 8**:

- **Headline ROI math (post-2026-05-12)**: $0.00934/dossier × 10k = $93.37 = **R$ 457** (PTAX venda 4.8999, 2026-05-08) vs. **R$ 50,500** manual baseline at midpoint labor rate. Cost ratio ~110×. Robust to 20% HITL rate assumption (still >10×).
- **Decision rubric** (3 binary inputs: M365? dev capacity? ≥30 training dossiers?) → recommended path. Lives in `07_architecture/diagrams.md` §5; relatório §5 should paraphrase or cite, not duplicate.
- **LGPD Art. 20 framing**: system is *data-preparation*, not *automated decision-making*. HITL gate is non-negotiable for this framing to hold. Documented in `07_architecture/lgpd.md` §10.
- **US tenant region** is an evaluation-time workaround, not a production decision. Honestly flagged as the #1 production gap in `lgpd.md` §11.
- **PTAX FX rate** for any future currency conversion: USD 1.00 ≈ BRL 4.8999 (2026-05-08, fetched from BCB Olinda API).

## Key findings already captured (do NOT redo)

From Epic 5.2 (`04_experiments/02_power_automate/notes.md`):

1. **Page-1 extraction is robust** (~96% AI Builder accuracy report; 100% visual on synthetic test).
2. **Page-2 extraction is layout-sensitive** — works on training-distribution layouts, fails on visually-different ones (the brief example PDF page 2 produced footer text and pagination markers as field values).
3. **Anti-hallucination behavior confirmed** — F02 missing-email and F03 missing-phone correctly returned EMPTY, not invented values. **0 hallucinations across 132 cells** on the synthetic test set.
4. **`Data de contratação` locale-misparse bug** — `12/02/2024` (BR = Feb 12) extracted as `2024-12-02` (Dec 2). Bug originates in Power Automate → Excel boundary, not AI Builder. Production-blocking for BR deployment unless tenant region is BR or date pre-formatted.
5. **Single-field gating insufficient** — CPF confidence 0.99 routed example PDF to Verdadeiro despite 4 page-2 fields being garbage. Production needs per-page or cross-validation gating.
6. **Methodological gap to own honestly in relatório §3**: our `generate_pdfs.py` synthetic corpus shares field LABELS but not VISUAL LAYOUT with the brief example. Real production deployment requires real Banco X dossiers as training data (~30-100 docs).

## Strategic angles already locked in

- **Python reference engine (`06_reference_script/`) + Azure DI Layout + Claude Sonnet 4.6** = **primary recommendation** (D-006, 2026-05-12). Empirically validated at 100% on 3-PDF baseline + OOD holdout, $0,00934/dossier. Production orchestration via n8n recommended but not built in PoC (CLI used).
- **Power Automate + AI Builder** = alternative recommendation for M365-resident firms preferring no-code maintenance by paralegal (D-005, reclassified by D-006). PA flow built end-to-end on page-1 (Epic 5.2); page-2 fallback (Azure DI + Claude) specified architecturally but not added inside PA in the PoC.
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
| `01_field_map/gold_truth.json` | Brief example PDF gold (used for scoring) |
| `01_field_map/scoring_rubric.md` | Grading rules (encoded in scoring scripts) |
| **`04_experiments/SCOREBOARD.md`** | **Source-of-truth synthesis for relatório §4 — every tool mapped to a role or excluded with reason** |
| `04_experiments/shared_llm_prompt.md` | The PT-BR prompt for ChatGPT/Claude/NotebookLM round-robin |
| `04_experiments/score_json_against_gold.py` | Generic scorer (LLM JSON output → scorecard) |
| `04_experiments/02_power_automate/notes.md` | Full Power Automate walkthrough (read for relatório draft) |
| `04_experiments/02_power_automate/scorecard.json` | PA test results (92.8% avg synthetic, 0 hallucinations) |
| `04_experiments/03_chatgpt/output_scorecard.json` | ChatGPT 5.5 Thinking: 100% on brief |
| `04_experiments/04_claude/output_scorecard.json` | Claude Opus 4.7: 100% on brief |
| `04_experiments/05_notebooklm/output_scorecard.json` | NotebookLM (Gemini): 100% on brief |
| `04_experiments/06_azure_di/notes.md` | Azure DI Layout findings — page-2 layout-tolerant |
| `04_experiments/07_tabula/notes.md` | Tabula OSS findings — 100% page-1 zero cost, 0% page-2 |
| **`06_reference_script/notes.md`** | **Reference pipeline empirical results (100% on 3-PDF + OOD F09 / 0 hallucinations / $93-per-10k) + 8-item production hardening checklist + history of the 2026-05-12 literal-extraction prompt fix** |
| `06_reference_script/README.md` | How to run CLI + Streamlit |
| `06_reference_script/test_corpus/dossiers.csv` | Validation run output (3 PDFs) |
| `06_reference_script/test_corpus/audit.csv` | Validation run audit log |
| `05_synthetic_data/pdfs/` | 8 synthetic PDFs (F01–F08) |
| `05_synthetic_data/gold/` | Matching gold JSONs |
| **`07_architecture/diagrams.md`** | **M365 + non-M365 paths, cross-val, HITL lifecycle, decision rubric** |
| **`07_architecture/roi.md`** | **$88.60 / R$ 434 vs. R$ 50,500 manual; sensitivity table; PTAX-anchored** |
| **`07_architecture/lgpd.md`** | **12-section article-by-article posture; Anthropic + Azure DI URLs verified** |
| `07_architecture/manual_timing.md` | n=1 paralegal baseline (6 min 44 sec, two-tab workflow) |
| **`08_kickoff_prompt.md`** | **Standalone Epic 8 fresh-session kickoff — paste the prompt block, get a clean start** |
| `00_brief/spec_decoded.md` | Brief checklist — relatório must satisfy all 7 prescribed sections + 5 diferenciais |

## Tenant info (for Power Automate / SharePoint references)

- M365 tenant: `revelatiotest2026.onmicrosoft.com` (US region — chosen to bypass CNPJ requirement)
- SharePoint site: `https://revelatiotest2026.sharepoint.com/sites/revelatiotest`
- Trial expires: **2026-06-08** (calendar reminder set to cancel)
- AI Builder model: trained 2026-05-09, published, "Dossie_Revelatio" collection
- Power Automate flow: "Revelatio Debtor Extraction" — built end-to-end, working

## How to resume in a new conversation (Epic 8 kickoff)

1. Open Claude Code in `/Users/marcosdidier/testeRevelatio/`.
2. Open `08_kickoff_prompt.md` — copy the block under **"## The prompt"** and paste it as the first message in the new session.
3. The kickoff block is self-contained: it references SESSION_RESUME.md + `08_kickoff_prompt.md` for full context, lists the brief's 7 prescribed sections, and instructs the new Claude to enter plan mode and ask the user 3 open questions before drafting.
4. Auto-memory will load 5 feedback rules automatically — still relevant for Epic 8:
   - Explain artifacts before writing them (especially relevant for PT-BR translation choices)
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

Five commits on `main` (no remote — local-only):

- `63f0ed3` — Initial commit: Epics 0–5 (brief decoded, scoring rubric, tool universe, synthetic corpus, Power Automate end-to-end, LLM round-robin)
- `936b029` — Epic 5.7–5.9: Azure DI Layout + Tabula empirical tests + SCOREBOARD synthesis
- `8f887ca` — Epic 6: reference pipeline + Streamlit demo UI
- `7be8039` — docs: README for reference script + Epic 7 kickoff prompt in resume
- `1d8d791` — Epic 7: Architecture / LGPD / ROI stakeholder docs + n=1 manual baseline

## What to NOT redo

- Don't re-build the Power Automate flow — working, captured in notes
- Don't re-train the AI Builder model — published, captured
- Don't rewrite backlog/decisions — just update as we go
- Don't re-do tool dossiers or comparison matrix — complete
- Don't re-generate synthetic PDFs — committed in `05_synthetic_data/pdfs/`
- Don't re-run F02/F03/F04/F08 through Power Automate — scorecard computed
- **Don't re-run the LLM round-robin** — outputs and scorecards saved at `04_experiments/03_chatgpt|04_claude|05_notebooklm/`
- **Don't re-provision Azure DI** — `di-revelatio-test` is live in East US, key in `.env`
- **Don't re-test the reference pipeline** — empirically validated at 100% on brief + F02 + F07 (baseline) and 100% on F09_brief_shape (OOD holdout, brief-faithful structure with fresh client data). Outputs at `06_reference_script/test_corpus/` and `05_synthetic_data/pdfs/F09_brief_shape.pdf`. Re-running incurs ~$0.04 of API.
- **Don't re-write `04_experiments/SCOREBOARD.md`** — source-of-truth, edit only if a new tool is added
- **Don't re-draft the Epic 7 architecture / ROI / LGPD docs** — committed at `1d8d791`. Edit only if a fact changes (e.g., PTAX moves materially, an Anthropic policy URL changes wording). Epic 8 *pulls from* these docs into PT-BR; it does not re-derive them.
- **Don't re-fetch the Anthropic / Azure DI / PTAX URLs** for Epic 8 prose — already verified 2026-05-11 and quoted with date stamps in `07_architecture/lgpd.md` §7 and `roi.md` §1. Re-fetch only if Epic 8 needs a *new* citation not already in those docs.
- **Don't re-measure the paralegal baseline** — 6 min 44 sec on the brief PDF is captured in `07_architecture/manual_timing.md`. n=1 is honestly disclosed; expanding to 3 PDFs is a *nice-to-have*, not a re-do.
