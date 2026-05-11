# Manual paralegal timing — empirical baseline

> **Purpose**: replace the brief's implied "~10 min/dossier" with a measured number for the `roi.md` §3 baseline. Source of truth for any "manual baseline" claim in the relatório.

## Method

The user ran a one-PDF timing experiment, working as a paralegal would on a single dossier from a fresh start. Setup:

- Two browser tabs side-by-side (Excel / sheet + PDF viewer)
- Start: stopwatch begins on opening the PDF
- Stop: stopwatch ends after the spreadsheet row is filled and one verification pass is done

## Measurement

| PDF | Time | Page-1 workflow | Page-2 workflow |
|---|---|---|---|
| `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` | **6 min 44 sec** (404 s) | Ctrl-C / Ctrl-V from the PDF text layer | Manual transcription (no text layer on the image-based page 2) |

**Date measured**: 2026-05-11.

**Sample size**: n=1. The user pivoted from the planned 3-PDF protocol to a single-PDF measurement to keep the experiment compact. F02 (missing-email) and F07 (skewed page 2) were not timed; the relatório should disclose this honestly under methodology caveats.

## Two-page asymmetry (key finding)

The single biggest observation from this run is that the manual workflow **splits exactly along the same boundary as the automated architecture**:

| Page | Manual workflow | Automated equivalent |
|---|---|---|
| Page 1 | Copy-paste (PDF has text layer; near-zero cognitive load per field) | Deterministic table parse (`page1_parser.py`); ~0s, no API cost |
| Page 2 | Manual transcription (PDF is image-only; cognitive load per field, no shortcut) | Azure DI Layout OCR + Claude/AI Builder field mapping |

This is not a coincidence — both the human and the system face the same fact about Banco X dossiers: **the comprovantes page is image content, not text**. That is the structural reason a deterministic-only approach (Tabula) hits 100% on page 1 and 0% on page 2 (`04_experiments/SCOREBOARD.md` §1 row 6). The architecture's two-layer routing exists because page 2 is genuinely harder, for the human and the machine.

**Implication for ROI**: most of the 6:44 was spent on page 2. A paralegal who could not copy-paste page 1 either (e.g., scanned dossier with no text layer at all) would land closer to 8–10 minutes — bracketing the brief's implied 10-min assumption. A faster paralegal who is highly familiar with the template might land closer to 5 minutes. **6:44 is a reasonable, mildly-optimistic anchor** for the baseline.

## What 6 min 44 sec means at 10k scale

| Time per dossier | Total hours for 10k | At R$ 30/h fully loaded | At R$ 60/h fully loaded |
|---|---|---|---|
| 6 min 44 sec (measured, page-1 copyable) | 1,122 h | **R$ 33,667** | **R$ 67,333** |
| ~10 min (brief implied, page-1 manual) | 1,667 h | R$ 50,000 | R$ 100,000 |
| 5 min (skilled paralegal) | 833 h | R$ 25,000 | R$ 50,000 |

Even at the optimistic measured time of 6:44 and the lower labor rate, the manual baseline is **R$ 33,667** vs. the automated cost of **~R$ 434** (= $88.60 × 4.8999 BRL/USD, PTAX venda 2026-05-08; see `roi.md` §1). The cost ratio is **~78:1** at the low end. At the midpoint labor rate (R$ 45/h), the ratio rises to ~116:1; see `roi.md` §1 TL;DR for the headline number. The optimistic-baseline case still leaves a >R$ 33,000 gap, so ROI is not load-bearing on the precise time measurement; it's load-bearing on the order of magnitude, which a single-PDF measurement establishes confidently.

## Stuck moments (qualitative)

(None recorded by the user for this run. If a 3-PDF expansion happens later, capture: date locale confusion on "Data de contratação", ambiguous bairro formatting, page-2 field-region misreading, etc.)

## Anchors

| Claim | Source |
|---|---|
| 6 min 44 sec measurement, two-tab method | User direct observation, 2026-05-11 |
| Page-2 is image content (no text layer) | Confirmed by manual transcription workflow + Tabula's 0% page-2 score in `04_experiments/SCOREBOARD.md` §1 row 6 |
| Automation cost $0.00886/dossier | `06_reference_script/notes.md` lines 33–38 |
| Brief's implied 10-min baseline | `00_brief/` PDF + project background context |
| FX rate USD 1.00 ≈ BRL 4.8999 | PTAX venda 2026-05-08, Banco Central do Brasil ([olinda.bcb.gov.br PTAX API](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo), verified WebFetch 2026-05-11) |
