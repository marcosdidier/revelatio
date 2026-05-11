# Session Resume — Project Revelatio

> **Read this first** when starting a fresh Claude Code conversation in this directory.

## What this project is
Take-home challenge: **Implementador de IA & Automações** for a Brazilian law firm. Automate extraction of ~10k debtor-PDF dossiers (Banco X) into Excel. Deadline **2026-05-13 17:00 BRT**. PT-BR deliverables, EN internal artifacts.

## Status snapshot (as of 2026-05-11, very early morning — session ended at ~01:40 BRT after Epic 6 wrapped)

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
| **6 — Reference Python script (+ Streamlit UI)** | ✅ **done — 99.07% avg on 3-PDF test, 0 hallucinations, ~$89/10k** |
| 7 — Architecture / LGPD / ROI | ⏳ pending (~2h) |
| 8 — Relatório PT-BR | ⏳ pending (~4-6h) |
| 9 — Video ≤ 5 min PT-BR | ⏳ pending (~2-3h) |
| 10 — QA & submission | ⏳ pending |

**Time remaining**: ~2 days (deadline 2026-05-13 17:00 BRT). Comfortable pace — all empirical work done, only writing artifacts remain. Reserve 1 full day for Epics 8 + 9 + 10.

## Where we left off — exact next step

**Epic 7 — Architecture / LGPD / ROI.** All empirical evaluation is complete (Epics 0–6 done, committed). Epic 7 produces three documents that feed directly into Epic 8 (relatório) and Epic 9 (video).

### Epic 7 deliverables (~2h total)

Create directory `07_architecture/` and write three files:

1. **`07_architecture/diagrams.md`** — Mermaid diagrams of the recommended hybrid architecture. At minimum:
   - **M365 path**: SharePoint folder → Power Automate flow → AI Builder (page 1) → Azure DI Layout (page 2 fallback) → Claude API (field mapping) → cross-validation → Excel / HITL queue
   - **Non-M365 path**: file upload (n8n trigger) → reference Python script (engine) → CSV + audit log + HITL queue
   - **Cross-validation flow**: how page-1 anchors (client_name, CPF) gate page-2 acceptance, and the per-page confidence routing
   - **HITL queue lifecycle**: needs_review=TRUE → SharePoint list (M365) or DB row (non-M365) → paralegal review form → approve/correct → write-back

2. **`07_architecture/lgpd.md`** — LGPD compliance posture. Anchored to LGPD Articles 6 (princípios), 7 (bases legais), 18 (direitos do titular), 46–49 (segurança e governança). Cover:
   - **Data residency**: where PDFs and extracted data live (Azure DI region, M365 tenant region, audit log location). Note: tenant is currently US for trial reasons — production must be Brazil South or document the cross-border data flow under Art. 33–36.
   - **Retention policy**: how long extracted CSV rows persist, how long PDFs are retained, when audit logs are purged.
   - **Access control**: who reads `dossiers.csv`, who reads `audit.csv` (with potentially-PII mismatch strings), who can modify HITL queue.
   - **PII redaction**: CPFs in `audit.csv` mismatch strings need masking. Production hardening checklist item #5 from `06_reference_script/notes.md`.
   - **In-tenant processing**: prevent third-party logging. Anthropic API does not retain customer data by default (cite the policy URL); Azure DI processes in-region.
   - **Direitos do titular**: how the firm responds to access / deletion / portability requests (Art. 18).

3. **`07_architecture/roi.md`** — ROI math at 10k-dossier scale. Anchored on the **empirically validated $0.0089/dossier** (from `06_reference_script/notes.md` and `04_experiments/SCOREBOARD.md` §4). Cover:
   - **Baseline cost**: paralegal time at ~10 min/dossier × R$ 30–60/h labor cost = R$ 50k–100k for 10k dossiers (one-time backlog) or annual recurring at the steady-state intake.
   - **Automated cost**: ~$89 (Azure DI + Claude API) + engineering time (~3 days one-time setup or ~$0 marginal for M365 path).
   - **Payback period**: essentially first day of operation.
   - **Sensitivity table**: what happens if the firm processes 1k, 10k, 100k dossiers/year. What happens if the HITL queue rate is 5% vs 20% (impacts paralegal residual cost).
   - **Hidden costs**: re-training Custom Neural every 6 months as Banco X templates evolve; LGPD audit costs; SharePoint storage scaling.

### Approach to writing these

These are **stakeholder-facing documents** (the relatório author will pull paragraphs directly into §5, §6, §7). Write in EN internally; the relatório translation to PT-BR happens in Epic 8. Anchor every claim in a specific empirical artifact (SCOREBOARD row, notes.md finding, scorecard number) so a skeptical reader can verify.

Recommended order: **diagrams first** (forces the architecture to be concrete), **ROI second** (anchored on the $89 we already validated), **LGPD third** (most legal-research-heavy, can pull from `02_tool_universe/07_power_automate.md` for tenant-region details).

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
| **`06_reference_script/notes.md`** | **Reference pipeline empirical results (99.07% / 0 hallucinations / $89-per-10k) + 8-item production hardening checklist** |
| `06_reference_script/README.md` | How to run CLI + Streamlit |
| `06_reference_script/test_corpus/dossiers.csv` | Validation run output (3 PDFs) |
| `06_reference_script/test_corpus/audit.csv` | Validation run audit log |
| `05_synthetic_data/pdfs/` | 8 synthetic PDFs (F01–F08) |
| `05_synthetic_data/gold/` | Matching gold JSONs |

## Tenant info (for Power Automate / SharePoint references)

- M365 tenant: `revelatiotest2026.onmicrosoft.com` (US region — chosen to bypass CNPJ requirement)
- SharePoint site: `https://revelatiotest2026.sharepoint.com/sites/revelatiotest`
- Trial expires: **2026-06-08** (calendar reminder set to cancel)
- AI Builder model: trained 2026-05-09, published, "Dossie_Revelatio" collection
- Power Automate flow: "Revelatio Debtor Extraction" — built end-to-end, working

## How to resume in a new conversation (Epic 7 kickoff prompt)

1. Open Claude Code in `/Users/marcosdidier/testeRevelatio/`.
2. Paste the **full block below** as the first message — it's self-contained and gives a fresh Claude session everything it needs to pick up cleanly:

---

> Continue Project Revelatio. Read `SESSION_RESUME.md` first — it has the complete status, deliverables, and empirical context.
>
> **Where we are**: Epics 0–6 are done and committed (3 commits on `main`, most recent `8f887ca`). The reference Python pipeline at `06_reference_script/` is empirically validated: **99.07% average accuracy** on a 3-PDF test corpus (brief + F02 + F07), **0 hallucinations**, **$0.0089 per dossier** ($89 for the full 10k Banco X backlog). The Streamlit demo UI at `06_reference_script/app.py` has been visually validated and is ready for video recording in Epic 9.
>
> **What I'm starting today**: Epic 7 — Architecture / LGPD / ROI. Three stakeholder-facing documents in a new `07_architecture/` directory:
>
> 1. `07_architecture/diagrams.md` — Mermaid diagrams for the recommended hybrid architecture (M365 path, non-M365 path, cross-validation flow, HITL queue lifecycle)
> 2. `07_architecture/lgpd.md` — LGPD compliance posture anchored to Art. 6, 7, 18, 33–36, 46–49 (data residency, retention, access control, PII redaction in audit logs, in-tenant processing, direitos do titular)
> 3. `07_architecture/roi.md` — 10k-dossier ROI math using the empirically validated $89, against a paralegal baseline (~R$ 50k–100k for 10k dossiers at ~10 min each)
>
> See the "Where we left off" section of `SESSION_RESUME.md` for the full spec of each document.
>
> **Pacing for today**: depth + insights welcome (this is writing, not hands-on execution). Anchor every claim to a specific artifact (a SCOREBOARD row, a notes.md finding, a scorecard number) so a skeptical reader can verify. Recommended order: diagrams first → ROI second → LGPD third.
>
> **Start by**: proposing the structure of all three documents (section outlines, ~5 min) so I can approve the shape before you draft prose. Don't start writing prose until I confirm the outline.

---

3. Auto-memory will load 5 feedback rules automatically — they're still relevant for Epic 7:
   - Explain artifacts before writing them (especially relevant — Epic 7 is heavy on artifact writing)
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

Three commits on `main` (no remote — local-only):

- `63f0ed3` — Initial commit: Epics 0–5 (brief decoded, scoring rubric, tool universe, synthetic corpus, Power Automate end-to-end, LLM round-robin)
- `936b029` — Epic 5.7–5.9: Azure DI Layout + Tabula empirical tests + SCOREBOARD synthesis
- `8f887ca` — Epic 6: reference pipeline + Streamlit demo UI

## What to NOT redo

- Don't re-build the Power Automate flow — working, captured in notes
- Don't re-train the AI Builder model — published, captured
- Don't rewrite backlog/decisions — just update as we go
- Don't re-do tool dossiers or comparison matrix — complete
- Don't re-generate synthetic PDFs — committed in `05_synthetic_data/pdfs/`
- Don't re-run F02/F03/F04/F08 through Power Automate — scorecard computed
- **Don't re-run the LLM round-robin** — outputs and scorecards saved at `04_experiments/03_chatgpt|04_claude|05_notebooklm/`
- **Don't re-provision Azure DI** — `di-revelatio-test` is live in East US, key in `.env`
- **Don't re-test the reference pipeline** — empirically validated at 99.07% on brief + F02 + F07, outputs at `06_reference_script/test_corpus/`
- **Don't re-write `04_experiments/SCOREBOARD.md`** — source-of-truth, edit only if a new tool is added
