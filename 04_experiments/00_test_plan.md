# Epic 5 — Test Plan & Template

> **What every per-tool hands-on test produces and how the artifacts are organized.** Read this once; each per-tool folder follows this template.

## Per-tool folder structure

Each tool tested in Epic 5 lives under `04_experiments/`:

```
04_experiments/
├── 00_test_plan.md             ← this file
├── 02_power_automate/          ← Epic 5.2  (chosen primary)
├── 03_chatgpt/                 ← Epic 5.3
├── 04_claude/                  ← Epic 5.4
├── 05_tabula/                  ← Epic 5.5
├── 06_n8n/                     ← Epic 5.6
├── 07_azure_doc_intel/         ← Epic 5.7  (cross-validator for 5.2)
├── 08_notebooklm/              ← Epic 5.8  (misfit demo)
├── 09_docling/                 ← Epic 5.9  (optional OSS)
└── scoreboard.md               ← Epic 5.10 consolidated comparison
```

## Each per-tool folder contains

| File / subfolder | Purpose | Required? |
|---|---|---|
| `walkthrough.md` | Step-by-step instructions for tools with multi-step provisioning (e.g. Power Automate) | only when needed |
| `notes.md` | Free-form observations during testing — the human-readable record | ✅ |
| `raw_output/` | Tool's literal output (JSON files, exported flows, etc.) | ✅ |
| `screenshots/` | UI screenshots showing the tool in action | ✅ |
| `score.csv` | Filled-in copy of `01_field_map/score_template.csv` | ✅ |
| `output.xlsx` | The Excel file the tool produced (if applicable) | when applicable |
| `cost_log.md` | Token / credit consumption for the run | ✅ |

## Standard procedure (per tool)

1. Read the tool's dossier (`02_tool_universe/0X_<tool>.md`) for context.
2. If a `walkthrough.md` exists for this tool, follow it; otherwise:
3. Run the tool on `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` first (the canonical example).
4. Capture artifacts:
   - Raw output → `raw_output/`
   - At least 1 UI screenshot → `screenshots/`
5. Copy `01_field_map/score_template.csv` → `04_experiments/<NN>_<tool>/score.csv`. Fill `tool_value` column.
6. Apply normalization rules from `01_field_map/scoring_rubric.md`.
7. Mark each row as **exact** / **partial** / **miss** / **hallucination**.
8. Compute total score (per-field × weight, aggregated to /100). Record in `notes.md`.
9. Re-run on 4 random synthetic PDFs from `05_synthetic_data/pdfs/` for axis-coverage (skip if the tool's role doesn't warrant it, e.g. NotebookLM misfit demo).
10. Update `04_experiments/scoreboard.md` (one row per tool — Epic 5.10 consolidates).

## Cost-recording convention

For each test, record cost in $USD per PDF assuming 10k batch:
- **API tools**: input tokens + output tokens × per-1M price (cite source)
- **SaaS / managed**: per-page tier × volume
- **OSS / local**: $0 in licensing; note hardware spend + dev time
- **Power Automate**: AI Builder credit consumption × $25 per 1k credits + applicable license seats

This feeds `07_recommendation/roi.md` (Epic 7.4).

## What "score" means

Per `01_field_map/scoring_rubric.md`:
- Per-field result: exact (1.0) / partial (0.5) / miss (0) / hallucination (−0.5)
- Weights: `cpf` and `contract_number` = 2× (downstream join keys); all others = 1×
- Aggregated to a 0–100 score
- Subscores reported per page (1 vs 2) and per axis (perfect / missing / bad-scan / etc.)

## Cross-validation requirement (Epic 5.10)

Power Automate (5.2) and Azure DI (5.7) test the **same underlying engine** (AI Builder Document Processing is built on Azure Document Intelligence). Their scores should agree within ±5 points. If they don't, investigate before declaring a winner — likely cause is AI Builder applying different post-processing than the raw API.

## Notes.md template

Each tool's `notes.md` should answer in plain prose:
- Setup difficulty (1–5 scale + 1 sentence why)
- What worked
- What didn't work
- Any surprises (positive or negative)
- Hallucination instances (what the tool invented)
- Estimated cost-per-PDF for 10k-batch deployment
- LGPD posture observed (BR region available? zero-retention possible?)
- Verdict change vs the dossier's pre-test prediction (refined or contradicted?)
