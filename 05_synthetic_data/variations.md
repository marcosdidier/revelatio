# Synthetic Data — Variations Matrix

> **Why this exists:** the brief implies 10k production PDFs with the *same* template but realistic data drift — missing fields, bad scans, alternate labels, format quirks. A recommendation that scores well on the single example PDF but cracks on production-realistic noise is a recommendation that fails day 2 of deployment. This file enumerates the **deliberate axes of variation** our synthetic corpus exercises so the Epic 5 hands-on tests aren't graded only on the easy case.
>
> **Where used:** `05_synthetic_data/fixtures.csv` lists which fixture exercises which axis; `generate_pdfs.py` produces the PDFs; `04_experiments/<tool>/score.csv` records each tool's accuracy across axes; `relatorio.md §3` ("o que não funcionou") cites specific axis-failures.

## Axes of variation in the corpus

| Axis | Why it matters | Fixture |
|---|---|---|
| 1. **Missing optional field** (email) | Common gap in cobrança data — debtor never gave email. Tools must return null, not invent. | F02 |
| 2. **Missing optional field** (phone) | Same logic, different field. | F03 |
| 3. **Page-2 image with noise/blur** | Real comprovantes are scanned at varying quality; OCR must degrade gracefully. | F04 |
| 4. **CPF without separators** (`12345678909`) | Field-mapping tools must recognize the digit pattern, not depend on dots/dashes. | F05 |
| 5. **Alternate field labels** (`Nome:` vs `Nome completo`, `Tel:` vs `Telefone`) | Robust extractors must anchor on semantic intent, not literal labels. | F06 |
| 6. **Page-2 rotated 3°** | Scanner skew is universal in document workflows. | F07 |
| 7. **Page-2 partial obscuration** (printer streak) | Partial-extraction handling — should report what it sees, flag what it can't. | F08 |
| 8. **Smoke-test "perfect" baseline** | Anchor: any tool that fails this fails everything. | F01 |

## Axes deliberately NOT covered (would be future work)

| Axis | Why deferred |
|---|---|
| Multi-debt clients (>1 contract per PDF) | Requires page-1 layout changes; relatório calls this out as Phase 2 |
| Multi-page comprovantes (3+ pages) | Realistic but our example is 2 pages; honor the brief's stated structure |
| Adversarial PDFs (deliberately corrupt structure) | Out of scope — we're testing OCR robustness, not security |
| Non-Portuguese debtors | Brazilian law firm context — PT-BR is the only realistic case |

## How each fixture is scored

Each fixture has a corresponding `gold/{fixture_id}.json` produced by the same script that generates the PDF — so the gold and the PDF are guaranteed to agree by construction. Tools are scored against the gold using `01_field_map/scoring_rubric.md`, with sub-scores reported per axis (e.g., "Tool X scored 95% on perfect, 80% on missing-field, 60% on noisy-page2").

Per-axis breakdowns are the relatório's most defensible evidence: instead of "Tool X is good," we say "Tool X handles missing fields well but degrades on bad scans — recommended only with the cloud OCR backend."
