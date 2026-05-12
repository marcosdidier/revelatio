# Backlog — Project Revelatio

> Take-home challenge: **Implementador de IA & Automações** — automating the Banco-X debtor-PDF → spreadsheet pipeline (~10,000 PDFs, currently ~10 people × several days of manual work).

| Field | Value |
|---|---|
| Owner | Marcos Didier |
| Brief sent | **2026-05-07** |
| Deadline | **2026-05-13 17:00 BRT** |
| Working dir | `/Users/marcosdidier/testeRevelatio/` |
| Source brief | `00_brief/brief_implementador_ia.pdf` |
| Source example | `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` |
| Deliverable language | **PT-BR** (relatório, video) — backlog stays EN for execution |
| Tooling co-pilot | Claude Code (Opus 4.7), back-to-back |
| Status | Active |

---

## TL;DR

We treat the test as a **production engineering brief**, not a one-shot prompt-and-pray. The pipeline routes each PDF page to the cheapest tool that solves it (Page 1 → deterministic text parser; Page 2 → OCR + Document-AI extraction with confidence-flagged human review). We benchmark **≥ 6 tools** hands-on against a manually-extracted gold truth — including the chosen primary, **Power Automate + AI Builder** (D-005), cross-validated against Azure Document Intelligence (same engine, different SKU), surface **≥ 8 tools beyond** the brief's list (the explicit differential), ship a **working Python reference script** that runs end-to-end on the example, generate **5–10 synthetic PDFs** to prove the script handles structural variation, and bundle everything into a PT-BR relatório + ≤ 5 min video. Special focus on **LGPD / data residency** (law firm + CPF + financial data = compliance non-negotiable) and **ROI math at 10k scale** — two angles most candidates won't address.

---

## Legend — Tags map back to brief's evaluation criteria

| Tag | Brief criterion |
|---|---|
| `[Pesquisa]` | Capacidade de pesquisa e teste de ferramentas |
| `[Clareza]` | Organização e clareza na solução proposta |
| `[Raciocínio]` | Raciocínio prático |
| `[Implementação]` | Capacidade de implementação |
| `[Comunicação]` | Comunicação e explicação da solução |
| `[Proatividade]` | Proatividade na busca de alternativas |
| `[Diff:UnlistedTool]` | **Diferencial**: apresentar ferramenta não listada |
| `[Diff:AltFlow]` | **Diferencial**: propor fluxo alternativo de automação |
| `[Diff:Script]` | **Diferencial**: criar script básico para auxiliar |
| `[Diff:Escala]` | **Diferencial**: preocupação com escala e organização operacional |
| `[Diff:UsoReal]` | **Diferencial**: estruturar para uso real no escritório |

---

## Coverage Map — Brief Requirement → Epic

| Brief section | Required output | Where addressed |
|---|---|---|
| Objetivo (avaliação) | Show all 6 evaluation skills | Epics 1–10, tagged inline |
| Contexto do desafio | Understand the 10k PDF pipeline | Epic 0 (decode) + Epic 7 (architecture) |
| Campos esperados (13 from page 1) | Excel column list | Epic 1 (gold truth) + Epic 6 (script) |
| Comprovantes da página 2 | Image OCR fields | Epic 1 + Epic 5 + Epic 6 |
| Ferramentas sugeridas (7) | Test ≥ 3 | Epic 2 (universe) + Epic 5 (hands-on ≥ 5) |
| Diferencial: ferramenta externa | Discover unlisted tools | **Epic 3** (sprint, ≥ 8 tools) |
| Diferencial: fluxo alternativo | Alternative automation | **Epic 7.2** |
| Diferencial: script básico | Working code | **Epic 6** |
| Diferencial: escala e operação | 10k-scale concerns | **Epic 7.4** + Epic 4 (synthetic data) |
| Entrega 1: Relatório | Per-bullet PT-BR doc | **Epic 8** |
| Entrega 2: Vídeo ≤ 5 min | PT-BR explainer | **Epic 9** |
| Formato (Drive ou .zip) + Prazo | Bundle, submit before 13/05 17h | **Epic 10** |

---

## Master Timeline — 6-Day Plan (today is 2026-05-07)

| Day | Date | Focus | Epics |
|---|---|---|---|
| Day 1 (Thu) | 2026-05-07 | Setup + ground truth + brief decode | 0, 1 |
| Day 2 (Fri) | 2026-05-08 | Tool universe + external research sprint | 2, 3 |
| Day 3 (Sat) | 2026-05-09 | Synthetic data + hands-on benchmarks (1/2) — Power Automate first | 4, 5 (5.1–5.5) |
| Day 4 (Sun) | 2026-05-10 | Hands-on benchmarks (2/2) + reference script start | 5 (5.6–5.10), 6 (6.1–6.3) |
| Day 5 (Mon) | 2026-05-11 | Finish script + architecture + LGPD + ROI | 6, 7 |
| Day 6 (Tue) | 2026-05-12 | Relatório PT-BR + video + dry-run | 8, 9, 10 (10.1–10.2) |
| Buffer | 2026-05-13 (until 17h) | Final polish + submission | 10.3 |

---

# Epic 0 — Project Setup & Documentation Discipline

**Why**: a clean, traceable workspace with explicit decisions and lessons logs is the difference between "we did stuff" and "here's the audit trail." Hirers can poke around any folder and find structure.

**0.1 — Scaffold workspace** ✅ *(done pre-execution)*
Create 10 numbered folders (`00_brief` … `09_video`) + copy source PDFs into `00_brief/`.
- Out: workspace skeleton in place
- DoD: `ls /Users/marcosdidier/testeRevelatio/` shows 10 numbered folders + 3 root files
- Tags: `[Clareza]`

**0.2 — Initialize decisions.md and lessons.md** ✅ *(done pre-execution)*
ADR-style log of locked-in choices + per-CLAUDE.md lessons stub.
- Out: `decisions.md`, `lessons.md`
- DoD: 4 ADRs (D-001…D-004) and 3 working hypotheses (WH-001…WH-003) recorded
- Tags: `[Clareza]`

**0.3 — Decode the brief into an actionable spec**
One-page PT-EN summary that translates the PDF brief into a 1:1 checklist we can grep against.
- Steps: re-read `00_brief/brief_implementador_ia.pdf` → write `00_brief/spec_decoded.md` listing every "must" / "expected" / "diferencial" with checkbox
- Out: `00_brief/spec_decoded.md`
- DoD: every bullet from the brief PDF appears as a checkbox; pages 2–5 of the brief fully covered
- Tags: `[Clareza]` `[Raciocínio]`

**0.4 — `git init` + first commit**
Optional but recommended; gives us reset points and a tidy delivery artifact.
- Steps: `cd /Users/marcosdidier/testeRevelatio && git init && git add . && git commit -m "chore: scaffold project Revelatio"`
- Out: `.git/` directory + initial commit
- DoD: `git log --oneline` shows 1 commit
- Tags: `[Clareza]` `[Implementação]`

---

# Epic 1 — Establish Ground Truth

**Why**: every tool we test must be **scored against the same baseline**. Without a manually-extracted gold file we can't tell which tool is "best" — we'd just be vibes-rating outputs. The brief's evaluation criterion "raciocínio prático" demands measurable evidence.

**1.1 — Field map: trace each Excel column to its PDF location**
Build a table mapping each of the 13+ expected fields to: page, section, format pattern (e.g., `CPF: NNN.NNN.NNN-NN`), and notes on extraction strategy.
- Steps: open the example PDF → for each field in the brief, record location + sample value from `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` → write `01_field_map/field_map.md` as a table
- Out: `01_field_map/field_map.md`
- DoD: 13 page-1 fields + ≥ 8 page-2 attachment fields documented; each row has page, anchor text, regex hint
- Tags: `[Clareza]` `[Raciocínio]`

**1.2 — Manually extract the gold-truth JSON for the example PDF**
The single source of truth every tool will be scored against.
- Out: `01_field_map/gold_truth.json` — schema `{"page1": {nome, cpf, telefone, ...}, "page2": {comprovante_endereco: {...}, comprovante_bancario: {...}}}`
- DoD: JSON parses; every field from `field_map.md` has a value; values match the example PDF exactly (Maria Almeida Costa, CPF 123.456.789-09, contrato BX-2024-0004587, etc.)
- Tags: `[Raciocínio]` `[Implementação]`

**1.3 — Define scoring rubric**
How we'll grade each tool: per-field exact / partial / miss; weighted by importance (CPF + contrato weight 2x because they're the join keys); aggregate to a 0–100 score.
- Out: `01_field_map/scoring_rubric.md` + `01_field_map/score_template.csv`
- DoD: rubric explains weights, partial-credit rules, and how OCR noise (e.g. spaces in CPF) is normalized before comparison
- Tags: `[Clareza]` `[Raciocínio]`

---

# Epic 2 — Tool Universe Map (the 7 brief-listed tools)

**Why**: the brief explicitly says we may explain why a tool *doesn't* fit — that's valid context. We give each of the 7 a fair structured dossier with a clear Fit verdict, **even ones that obviously don't fit** (NotebookLM for bulk extraction, etc.). Demonstrates `[Pesquisa]` and respects the hirer's judgment by not pretending they made a bad list.

**Per-tool dossier template** (one Markdown file per tool under `02_tool_universe/`):
- *What it is* (1 paragraph)
- *Where it fits in our pipeline* (extraction / orchestration / chat-only / none)
- *Hands-on plan* (will we test it in Epic 5? if not, why not)
- *LGPD / data-residency note*
- *Fit verdict*: ✅ Recommended · ⚠️ Conditional · ❌ Not recommended (with one-line reason)

**2.1 — ChatGPT** (`02_tool_universe/01_chatgpt.md`) — GPT-5 with vision + file upload. Hands-on test in 5.2. LGPD: Plus tier may train on data unless opted out; Team/Enterprise have zero-retention. Likely ⚠️ for direct-to-app use; ✅ as a prototyping tool. Tags: `[Pesquisa]`

**2.2 — Claude** (`02_tool_universe/02_claude.md`) — Opus 4.7 with native PDF support up to 100 pages, vision built-in. Hands-on test in 5.3. LGPD: Team/Enterprise has zero-retention; API supports zero-data-retention. Likely ✅ via API. Tags: `[Pesquisa]`

**2.3 — NotebookLM** (`02_tool_universe/03_notebooklm.md`) — Google Workspace research assistant over uploaded sources. **Wrong tool**: built for conversational research, not bulk structured extraction. Will test briefly in 5.7 to *demonstrate* the misfit (one screenshot = strong evidence). Verdict: ❌ for bulk; ✅ as a "search-the-corpus" companion for the legal team after extraction. Tags: `[Pesquisa]` `[Raciocínio]`

**2.4 — Make** (`02_tool_universe/04_make.md`) — orchestrator (Zapier-class). Has built-in OpenAI / Anthropic / OCR modules. Cloud-only — every PDF flows through Make servers. Verdict: ⚠️ — fine for non-sensitive data; LGPD friction for debtor data unless we use Make for trigger-only and keep payload local. Tags: `[Pesquisa]`

**2.5 — n8n** (`02_tool_universe/05_n8n.md`) — orchestrator like Make BUT supports **self-hosting** → entire flow on the firm's infra → strong LGPD posture. Hands-on test in 5.5: build a flow that watches a folder, calls Doc-AI per PDF, writes to a Google Sheet. Verdict: ✅ if self-hosted as the alternative no-code flow. Tags: `[Pesquisa]` `[Diff:AltFlow]`

**2.6 — Tabula** (`02_tool_universe/06_tabula.md`) — Java GUI/CLI for table extraction from text-based PDFs. **Page 1 only** — no OCR, so page 2 is invisible to it. Hands-on test in 5.4 to score page-1 coverage. Verdict: ⚠️ — useful as a free baseline for page 1; insufficient alone. Tags: `[Pesquisa]`

**2.7 — Power Automate + AI Builder** (`02_tool_universe/07_power_automate.md`) ⭐ **CHOSEN PRIMARY (D-005)** — End-to-end M365-native solution. AI Builder Document Processing extracts both pages (built on same engine as Azure DI), Power Automate orchestrates, Excel Online writes the spreadsheet, Approvals + SharePoint handle HITL. Hands-on test in **5.2**; cross-validated against Azure DI in 5.7. Verdict: ✅ Chosen primary. Tags: `[Pesquisa]` `[Implementação]` `[Diff:UsoReal]` `[Diff:Escala]`

**2.8 — Microsoft Copilot** (`02_tool_universe/08_copilot.md`) — chat-mode AI in M365 apps. Same M365 caveat. Useful for *consuming* the resulting spreadsheet (e.g., "summarize all debtors > 90 days") but not the extractor itself. Verdict: ⚠️ Not the extractor; ✅ as a downstream consumer. Tags: `[Pesquisa]` `[Raciocínio]`

**2.9 — Comparison matrix**
Single CSV/MD that summarizes all 8 dossiers across columns: extractor / orchestrator / privacy posture / cost class / hands-on score (filled later from Epic 5).
- Out: `02_tool_universe/comparison_matrix.md`
- DoD: 8 rows, every column populated, ranked
- Tags: `[Clareza]` `[Comunicação]`

---

# Epic 3 — External Tool Research Sprint  *(Brief differential: ferramenta não listada)*

**Why**: the brief explicitly calls out external tool discovery as a key differential. Most candidates will stop at the listed 7. We surface ≥ 8 unlisted tools, organize by category, and pull 1–2 finalists into the hands-on benchmark.

**3.1 — Document AI APIs** (`03_external_research/01_doc_ai_apis.md`)
Cloud document understanding services. Each entry: vendor, what it does, pricing/page, prebuilt vs custom model availability, Brazil region availability, LGPD posture.
- Tools to research: **Azure Document Intelligence** (Layout + Custom + GenAI extraction), **AWS Textract** (Forms + Tables + Queries), **Google Document AI** (Form Parser + Custom Extractor + Workbench)
- DoD: 3 vendors, side-by-side table on cost, accuracy class, BR region, LGPD
- Tags: `[Pesquisa]` `[Proatividade]` `[Diff:UnlistedTool]`

**3.2 — LLM-with-vision API options** (`03_external_research/02_llm_vision.md`)
Direct API use of multimodal models (vs the wrapped product in Epic 2).
- Tools: **Anthropic Claude API** (PDF native), **OpenAI Responses API** (GPT-5 vision), **Google Gemini API** (1M-token context, native PDF)
- DoD: comparison on PDF support, cost per 1k pages, structured-output mode (JSON schema enforcement), zero-retention options
- Tags: `[Pesquisa]` `[Proatividade]` `[Diff:UnlistedTool]`

**3.3 — Specialized SaaS extractors** (`03_external_research/03_specialized_saas.md`)
Vertical document-extraction products with HITL UIs, often easier for non-technical teams to operate.
- Tools: **Reducto**, **Extend**, **Nanonets**, **Mindee**, **Rossum**, **Klippa**, **Affinda**, **Parseur**, **Docparser**
- DoD: ≥ 6 tools profiled; for each → strengths, BR-language support (PT-BR is critical), pricing class, and a "would the legal team operate this UI" judgment
- Tags: `[Pesquisa]` `[Proatividade]` `[Diff:UnlistedTool]` `[Diff:UsoReal]`

**3.4 — Open-source / local options** (`03_external_research/04_oss.md`)
Tools that run on the firm's machine — strongest LGPD posture.
- Tools: **Docling** (IBM), **Marker** (vision-LLM PDF→MD), **Unstructured.io**, **LlamaParse** (LlamaIndex), **Surya** (multilingual OCR with PT support), **PaddleOCR**, **Tesseract** (baseline), **pdfplumber** (page-1 deterministic — already in our hypothesis)
- DoD: ≥ 5 OSS tools profiled; install effort, hardware needed, PT-BR accuracy notes, license
- Tags: `[Pesquisa]` `[Proatividade]` `[Diff:UnlistedTool]`

**3.5 — Synthesis: top 3 external candidates → into Epic 5 hands-on**
Pick the 1–2 strongest external tools to actually benchmark in Epic 5.
- Out: `03_external_research/00_finalists.md`
- DoD: justification per finalist; default selection: Azure Document Intelligence (cloud cost-effective) + Docling or Marker (OSS, LGPD-friendly fallback)
- Tags: `[Raciocínio]` `[Comunicação]`

---

# Epic 4 — Synthetic Data Generation  *(Diff: Escala)*

**Why**: a recommendation built on n=1 is not a recommendation, it's an anecdote. We generate a small corpus that mimics the example PDF's structure with controlled variations, so when we say "the script handles 10k PDFs", we have evidence — not assertions.

**4.1 — Define variation matrix**
Which axes of variation matter? Missing fields, alternate field labels, low-quality scan on page 2, multi-debt clients (>1 contract), digit-only vs formatted CPF, different bank receipt layouts.
- Out: `05_synthetic_data/variations.md` — table with 8–10 axes
- DoD: each axis has rationale tied to a real-world likelihood
- Tags: `[Raciocínio]` `[Diff:Escala]`

**4.2 — Build PDF generator script**
Python + ReportLab (page 1) + Pillow/raster for page 2 to mimic the image-as-attachment behavior. Driven by a CSV of fixture rows.
- Out: `05_synthetic_data/generate_pdfs.py`, `05_synthetic_data/fixtures.csv`
- DoD: script runs, produces deterministic output for given seed
- Tags: `[Implementação]` `[Diff:Script]` `[Diff:Escala]`

**4.3 — Generate corpus of 5–10 PDFs**
Each fixture exercises ≥ 1 axis from 4.1. Include 1 "perfect" PDF (matches example exactly) as smoke-test.
- Out: `05_synthetic_data/pdfs/{01_perfect, 02_missing_email, 03_low_res_scan, ...}.pdf` + matching `gold/*.json`
- DoD: each PDF has its own gold-truth JSON; corpus opens correctly in Preview
- Tags: `[Implementação]` `[Diff:Escala]`

---

# Epic 5 — Hands-On Tool Benchmark

**Why**: the brief asks for ≥ 3 tools tested. We do **6 hands-on** to dominate the criterion AND because the chosen primary solution (Power Automate, D-005) deserves explicit hands-on validation rather than just analytical defense. Each test produces a directory of artifacts (raw output, screenshot, scored JSON), so the relatório can cite real evidence rather than impressions.

**5.1 — Test plan & template** (`04_experiments/00_test_plan.md`)
Standard procedure: take the example PDF + 3 random synthetic PDFs from corpus → run through tool → capture raw output → score against gold.
- Out: per-tool subfolder template `04_experiments/<NN>_<tool>/{raw_output/, screenshots/, score.csv, notes.md}`
- DoD: template folder exists with README explaining what each file should contain
- Tags: `[Clareza]`

**5.2 — Run: Power Automate + AI Builder Document Processing** ⭐ **CHOSEN PRIMARY (D-005)**
End-to-end test of the production pipeline shape we'd actually deploy. Validates the chosen recommendation directly (and is cross-validated by Azure DI in 5.7 — same engine, different SKU).
- Steps:
  1. Provision M365 Business Basic 30-day trial (instant) + Power Automate Premium trial + AI Builder credits trial via admin center
  2. Provision Dataverse default environment (~5 min)
  3. AI Builder → Document Processing → Custom model. Upload 5 PDFs (the example + 4 from synthetic corpus). Tag the brief-required + page-2 fields per `01_field_map/field_map.md`. Train (~10–30 min)
  4. Build Power Automate flow: SharePoint folder trigger → AI Builder Predict → confidence routing (≥ 0.85 → Excel Online "Add row to table"; < 0.85 → Microsoft Approvals + SharePoint review list) → email/Teams summary on completion
  5. Run on the example PDF; capture flow run JSON, per-step screenshots, output Excel row
  6. Run on 4 random synthetic PDFs from Epic 4 (including 1 deliberately corrupted to verify HITL routing)
  7. Score each against gold using the rubric
- Out: `04_experiments/02_power_automate/{model_training/, flow_export.json, run_history/, output.xlsx, score.csv, screenshots/, notes.md}`
- DoD: end-to-end flow succeeds; field accuracy ≥ 90% on example PDF; HITL routing demonstrably triggers on the deliberately-corrupted synthetic; AI Builder credit consumption recorded for the cost model
- Tags: `[Pesquisa]` `[Implementação]` `[Diff:UsoReal]` `[Diff:Escala]`

**5.3 — Run: ChatGPT (Plus, GPT-5 with file upload)**
Steps: upload the example PDF → prompt to extract all 13+ fields as JSON → record output + a follow-up "now also extract page 2" → save raw response.
- Watch for: hallucinated fields, halts on multi-page, refusal due to "personal data".
- Out: `04_experiments/03_chatgpt/` populated
- DoD: scored against gold; observed cost (tokens × price) recorded; LGPD note on data-handling policy.
- Tags: `[Pesquisa]` `[Implementação]`

**5.4 — Run: Claude (Opus 4.7 via Claude.ai + via API)**
Two-shot: once via web (file upload), once via Anthropic Python SDK with `pdf` content block. Compare structured-output quality.
- Out: `04_experiments/04_claude/` with both results
- DoD: scored; API cost recorded; observation on whether tool prefers JSON-mode or natural answer
- Tags: `[Pesquisa]` `[Implementação]`

**5.5 — Run: Tabula (page-1 only, demonstrate the limit)**
Steps: open Tabula GUI → load example PDF → auto-detect tables on page 1 → export CSV → also try page 2 to confirm it returns nothing useful (the demonstration).
- Out: `04_experiments/05_tabula/` with CSV + screenshots showing page-2 emptiness
- DoD: page-1 score ≥ 80% (likely it nails the simple table); page-2 score = 0 with documented "no OCR" note
- Tags: `[Pesquisa]` `[Raciocínio]`

**5.6 — Run: n8n flow** *(Diff: AltFlow)*
Build a small n8n workflow: trigger (manual file upload) → HTTP node to Claude API or Doc AI → JSON parser → Google Sheets append. Run on the example PDF. Self-hosted via npx for local privacy demo.
- Out: `04_experiments/06_n8n/` with workflow JSON export + screenshots + sheet link
- DoD: end-to-end run produces a sheet row matching the gold
- Tags: `[Pesquisa]` `[Implementação]` `[Diff:AltFlow]`

**5.7 — Run: Azure Document Intelligence** *(Diff: UnlistedTool + cross-validation for 5.2)*
The strongest "unlisted tool" play AND a cross-validation of the Power Automate (5.2) accuracy claim — AI Builder Document Processing is built on the Azure DI engine, so testing both gives us two angles on the same extraction layer (5.2 + 5.7 should agree within ~5 points; if they don't, that's an alarm we investigate).
- Steps: provision Azure account if needed → upload example via Document Intelligence Studio → try `prebuilt-layout` then `prebuilt-document` then a custom extraction model → record raw JSON + cost
- Out: `04_experiments/07_azure_doc_intel/` with raw JSON, screenshots from Studio, cost log
- DoD: page-2 image fields extracted (especially código de barras, valor pago, autenticação); Brazil-region note on residency; score within ±5 points of 5.2's score (cross-validation check)
- Tags: `[Pesquisa]` `[Implementação]` `[Diff:UnlistedTool]`

**5.8 — Run: NotebookLM (proving the misfit)**
Steps: upload example PDF as a source → ask "extract all fields as a table" → screenshot the answer (likely conversational, not structured). One screenshot ≫ 1000 words to defend the verdict.
- Out: `04_experiments/08_notebooklm/screenshot.png` + `notes.md`
- DoD: noted that conversational LLM-grounded research ≠ bulk structured extraction; positive note that NotebookLM **could** sit downstream of the spreadsheet for legal-team Q&A on the corpus
- Tags: `[Pesquisa]` `[Raciocínio]` `[Comunicação]`

**5.9 — Optional: Run: Docling or Marker (OSS local fallback)**
Run as a "no-API-key" alternative for LGPD-strict orgs.
- Out: `04_experiments/09_docling/`
- DoD: scored; install steps documented; recorded local hardware (M-series Mac) latency
- Tags: `[Pesquisa]` `[Diff:UnlistedTool]`

**5.10 — Score consolidation & winner declaration**
Fill the comparison matrix from 2.9 with hands-on numbers; declare a winner per criterion (best accuracy, best cost, best LGPD posture, best ease-of-operation). **Verify cross-validation**: 5.2 (Power Automate) and 5.7 (Azure DI) should produce very similar scores; document any divergence.
- Out: `04_experiments/scoreboard.md` + updated `02_tool_universe/comparison_matrix.md`
- DoD: ranked list; chosen primary (Power Automate) explicitly justified with cross-validation note; alternative flow (n8n + Claude / Azure DI) explicitly recommended for non-M365 firms
- Tags: `[Clareza]` `[Comunicação]` `[Raciocínio]`

---

# Epic 6 — Reference Implementation Script  *(Diff: Script + Diff: Escala)*

**Why**: the brief lists "criar script básico" as a differential. We over-deliver: a small but real Python pipeline that is end-to-end runnable on any PDF in the corpus, with schema validation, confidence scoring, and an Excel writer. This is what we'll demo in the video.

**6.1 — Architecture sketch** (`06_reference_script/ARCHITECTURE.md`)
1-page diagram + flow narrative. Components: `loader.py` → `page1_parser.py` (pdfplumber) → `page2_parser.py` (Doc AI / Claude vision) → `schema.py` (pydantic) → `confidence.py` → `excel_writer.py` → `cli.py`.
- DoD: diagram + 1-page narrative + module table
- Tags: `[Comunicação]` `[Implementação]`

**6.2 — `page1_parser.py`** — deterministic text extraction with anchored regex per field. No LLM, no OCR. Near-zero cost per call.
- Steps: `pip install pdfplumber` → load page 1 → for each field in `field_map.md`, find anchor + regex → return dict
- DoD: returns 13/13 fields for the example PDF; unit-tested against `gold_truth.json`
- Tags: `[Implementação]` `[Raciocínio]`

**6.3 — `page2_parser.py`** — chosen Doc-AI engine (default Azure DI; pluggable to Claude vision). Outputs structured fields + per-field confidence.
- DoD: returns ≥ 8 fields from the comprovantes section; confidence floats present
- Tags: `[Implementação]`

**6.4 — `schema.py` (pydantic)** — strict types: CPF format-validated, valores as `Decimal`, dates as `date`. Failures → `ValidationError` captured per row, not a crash.
- DoD: passing the gold dict validates clean; deliberately corrupted input raises a labelled error
- Tags: `[Implementação]` `[Raciocínio]`

**6.5 — `confidence.py`** — combines parser-emitted confidence with rule-based checks (CPF checksum, CEP format, valor > 0, dias_em_atraso ≥ 0). Outputs aggregate `confidence_score` per row + per-field flags.
- DoD: one synthetic-corpus PDF deliberately produces low confidence and is flagged
- Tags: `[Implementação]` `[Raciocínio]` `[Diff:Escala]`

**6.6 — `excel_writer.py`** — `openpyxl`. Sheet 1: page-1 fields (one row per PDF). Sheet 2: comprovantes (one row per attachment). Sheet 3: review-queue (rows below confidence threshold). Conditional formatting: red highlights on flagged fields.
- DoD: opens cleanly in Excel + Google Sheets; column order matches the brief's expected fields
- Tags: `[Implementação]` `[Diff:UsoReal]`

**6.7 — `cli.py`** — `python -m revelatio extract <input.pdf>` and `python -m revelatio batch <folder/>`. Logs to `audit.log`; supports `--dry-run` and `--threshold 0.85`.
- DoD: `python -m revelatio batch 05_synthetic_data/pdfs/ -o out.xlsx` produces a valid xlsx in < 60s on M-series Mac
- Tags: `[Implementação]` `[Diff:Script]`

**6.8 — Tests on synthetic corpus**
Run the pipeline against all 5–10 synthetic PDFs; produce `06_reference_script/test_report.md` showing accuracy per axis from the variation matrix.
- DoD: ≥ 90% field-level accuracy on the "happy path" PDFs; ≥ 70% on adversarial PDFs; flagged-row rate matches expectation
- Tags: `[Implementação]` `[Diff:Escala]`

---

# Epic 7 — Architecture & Recommendation

**Why**: the relatório needs to answer "how would the team actually use this?" — not just "which tool won." Architecture, LGPD, ROI, and risks are the senior-engineer payload that turns a tool review into a deployable plan.

**7.1 — Architecture diagram** (`07_recommendation/architecture.md` + Mermaid)
Watch folder → queue (Postgres or even SQLite) → workers (run our Python pipeline OR n8n calls) → Excel/Sheets writer + audit log → review queue UI for HITL → clean spreadsheet.
- DoD: Mermaid diagram renders; arrows labelled with data shapes; dashed boundary for "leaves firm's network"
- Tags: `[Comunicação]` `[Clareza]`

**7.2 — Alternative no-code flow** *(Diff: AltFlow)* (`07_recommendation/alt_flow_n8n.md`)
For non-engineering teams to maintain. Same logical flow but in n8n. Tradeoffs section: easier handover vs less control / visibility on errors.
- DoD: 1-page diagram + when-to-prefer-which decision tree
- Tags: `[Comunicação]` `[Diff:AltFlow]`

**7.3 — LGPD / data residency analysis** (`07_recommendation/lgpd.md`) *(this is the angle most candidates won't have)*
Data inventory (CPF, e-mail, address, financial data → all sensitive under LGPD); legal basis (legitimate interest of the controller bank, or contract execution); data residency (Azure has BR South region; AWS has São Paulo; OSS option keeps data fully on-prem); retention; the "operator vs controller" question for the law firm.
- DoD: 1-page memo a non-lawyer can act on; explicit recommendations for each tool tier
- Tags: `[Raciocínio]` `[Comunicação]` `[Diff:UsoReal]`

**7.4 — Cost & ROI model** (`07_recommendation/roi.xlsx` or `roi.md` table) *(Diff: Escala)*
Three scenarios — current manual baseline (10 people × X days × cost), recommended pipeline (Doc AI per-page cost × 10k + ~5% HITL × labor cost), worst-case fallback (LLM per page × 10k). Show payback in PDFs processed.
- DoD: numbers honest (cite source for per-page pricing); break-even calc shown; sensitivity to HITL rate
- Tags: `[Raciocínio]` `[Comunicação]` `[Diff:Escala]`

**7.5 — Risk register** (`07_recommendation/risks.md`)
Top 8 risks: vendor outage, model drift on new PDF templates, OCR fails on bad scans, CPF false positive, audit failure, cost overrun, LGPD breach, key-person dependency. Each: impact, likelihood, mitigation.
- DoD: 8 risks with mitigations; mapped to who owns each
- Tags: `[Raciocínio]` `[Diff:UsoReal]`

**7.6 — Operational playbook** (`07_recommendation/playbook.md`) *(Diff: UsoReal)*
Day-after-deploy: who watches the queue, what to do when a row fails, how to add a new field, how to upgrade the model, what tells us the system is degrading.
- DoD: 1-page runbook in plain language for the legal-ops lead
- Tags: `[Diff:UsoReal]` `[Comunicação]`

---

# Epic 8 — Deliverable Assembly (PT-BR)

**Why**: the relatório is **the** thing the hirer reads. It must mirror the brief's bullet list 1:1 (so they can checklist-grade it) and be in PT-BR. We translate from our internal EN artifacts.

**8.1 — Author `relatorio.md` (PT-BR)** matching the brief's required sections **exactly**:
- Ferramentas testadas
- O que funcionou em cada uma
- O que não funcionou
- Qual ferramenta faz mais sentido para o caso
- Como essa ferramenta seria utilizada no fluxo da equipe
- Possíveis limitações ou cuidados da solução
- Possível plano inicial de implementação
- *(extras for differentials: ferramentas externas, fluxo alternativo, escala, LGPD)*
- Out: `08_deliverables/relatorio.md` + a rendered `relatorio.pdf`
- DoD: each brief bullet has its own H2; PT-BR throughout; ≤ 8 pages PDF
- Tags: `[Comunicação]` `[Clareza]`

**8.2 — `README.md` (PT-BR) for the bundle**
The first thing the hirer opens after unzipping. Map of the bundle, how to read it, "start here" pointers.
- Out: `08_deliverables/README.md`
- Tags: `[Comunicação]` `[Clareza]`

**8.3 — `materiais_adicionais/` index**
Curated list with hyperlinks: comparison matrix, scoreboard, architecture, LGPD memo, ROI, script, video link.
- Out: `08_deliverables/materiais_adicionais/INDEX.md`
- Tags: `[Clareza]`

**8.4 — Bundle as `.zip` + upload to Drive**
Final packaging. Exclude `.git/`, `__pycache__`, `node_modules`, `*.env`. Naming: `revelatio_marcos_didier_v1.zip`.
- Out: `08_deliverables/revelatio_marcos_didier_v1.zip` + Drive share link in README
- DoD: zip < 50 MB, opens cleanly, Drive link is set to "Anyone with the link – Viewer"
- Tags: `[Implementação]`

---

# Epic 9 — Video (≤ 5 min, PT-BR)

**Why**: the brief is explicit about the time limit. A tight, well-paced video is itself a `[Comunicação]` signal. Most candidates ramble — we plan it second-by-second.

**9.1 — Storyboard / script** (`09_video/script.md`)
Five-act structure for ~5 min: (1) 30 s — problem framing & ROI hook, (2) 60 s — what we found across tools (matrix on screen), (3) 90 s — recommended architecture + LGPD note, (4) 90 s — live script demo (one PDF in → one row out), (5) 30 s — implementation roadmap & close.
- DoD: timed line-by-line; under 5:00 read at moderate pace
- Tags: `[Comunicação]`

**9.2 — Slide deck** (`09_video/slides.pdf` or Google Slides link)
Minimal, ≤ 8 slides: title, problem, tools-tested matrix, recommendation, architecture, demo, ROI, close.
- DoD: rendered PDF; no slide has > 30 words
- Tags: `[Comunicação]` `[Clareza]`

**9.3 — Screen-recording rehearsal**
Loom or QuickTime. Do one untimed run to find dead air; then time it; then one final clean take.
- DoD: ≤ 5:00, no outright stumbles, demo segment shows the script writing the spreadsheet row
- Tags: `[Comunicação]`

**9.4 — Final cut + upload**
Light editing only (cut dead air, normalize audio). Upload to Loom or Drive. Link in README + relatório.
- Out: `09_video/final_video.mp4` + share link
- DoD: link plays in incognito; PT-BR audio; auto-captions on
- Tags: `[Comunicação]`

---

# Epic 10 — Quality Gate & Submission

**Why**: don't lose points on technicalities. The brief's last page lists Formato + Prazo — we triple-check.

**10.1 — Self-review against the brief checklist**
Open `00_brief/spec_decoded.md`, check every box, fix gaps.
- DoD: 100% of brief checkboxes marked; one paragraph per "Diferencial" explaining where we hit it
- Tags: `[Clareza]`

**10.2 — Evaluator-persona dry-run**
Read the bundle as if we were the hirer. Time it. Note any "wait, what?" moments. Fix them.
- Out: `08_deliverables/dry_run_notes.md` (ephemeral, deleted before submission)
- DoD: ≤ 15 min total read time for the relatório; demo video plays cleanly
- Tags: `[Clareza]` `[Comunicação]`

**10.3 — Submit before 13/05/2026 17:00 BRT**
Send the Drive link or zip via the channel the hirer specified. Confirm receipt.
- DoD: confirmation logged in `decisions.md` (D-007: submitted at HH:MM); buffer of ≥ 6 h vs deadline. (D-006 was claimed on 2026-05-12 for the strategic flip from Power Automate-primary to Python-engine-primary, so the submission ADR slot bumps to D-007.)
- Tags: `[Clareza]`

---

## Appendix A — Coverage of the Brief's 5 Differentials

| Differential | Where addressed |
|---|---|
| Apresentar uma ferramenta não listada | Epic 3 (≥ 8 unlisted tools), Epic 5.6 (Azure DI hands-on), Epic 5.8 (Docling) |
| Propor um fluxo alternativo de automação | Epic 7.2 (n8n alt flow) |
| Criar um script básico para auxiliar | Epic 6 (full Python pipeline) |
| Demonstrar preocupação com escala e organização operacional | Epic 4 (synthetic corpus), Epic 7.4 (ROI), Epic 7.6 (playbook) |
| Estruturar para uso real no escritório | Epic 7.3 (LGPD), Epic 7.5 (risks), Epic 7.6 (playbook), Epic 8 (PT-BR docs) |

## Appendix B — Submission Checklist

- [ ] Relatório PT-BR (`08_deliverables/relatorio.pdf`) covers all 7 brief bullets + 4 differential bullets
- [ ] Vídeo ≤ 5:00 PT-BR (`09_video/final_video.mp4` or Loom link)
- [ ] Script (`06_reference_script/`) runnable: `python -m revelatio batch ...`
- [ ] Materiais adicionais index (`08_deliverables/materiais_adicionais/INDEX.md`)
- [ ] README.md PT-BR at top level of bundle
- [ ] Zip OR Drive link tested in incognito
- [ ] Submitted before 2026-05-13 17:00 BRT

## Appendix C — Why this beats a typical submission

1. **Two-layer routing** insight (cheap deterministic for page 1, Doc-AI for page 2) — most candidates blast everything through ChatGPT and pay a 100x cost penalty at scale.
2. **≥ 5 hands-on tool benchmarks** vs the brief's minimum of 3.
3. **Working script** end-to-end on synthetic corpus — not just "here's what I would do."
4. **LGPD section** on a law-firm + financial-data brief — the obvious compliance angle most candidates won't address.
5. **ROI math at 10k scale** with an explicit break-even and HITL sensitivity — turns the conversation from "cool demo" to "let's deploy."
6. **PT-BR deliverables** — cultural-fit signal that an English-only submission misses.
7. **Audit trail** in `decisions.md` — the bundle reads like a real internal project, not a homework assignment.

## Appendix D — File Map (final state at submission)

```
testeRevelatio/
├── README.md                     ← (Epic 8.2, PT-BR) entry point for the hirer
├── backlog.md                    ← this file (EN, internal)
├── decisions.md                  ← ADR log (EN, internal)
├── lessons.md                    ← per CLAUDE.md (EN, internal)
├── 00_brief/                     ← original PDFs + decoded spec
├── 01_field_map/                 ← gold truth + scoring rubric
├── 02_tool_universe/             ← 8 dossiers + comparison matrix
├── 03_external_research/         ← 4 categories of unlisted tools + finalists
├── 04_experiments/               ← per-tool benchmark folders + scoreboard
├── 05_synthetic_data/            ← generator script + 5-10 PDFs + golds
├── 06_reference_script/          ← runnable Python pipeline + tests
├── 07_recommendation/            ← architecture, LGPD, ROI, risks, playbook
├── 08_deliverables/              ← relatorio (PT-BR), README, INDEX, zip
└── 09_video/                     ← script, slides, final cut + share link
```
