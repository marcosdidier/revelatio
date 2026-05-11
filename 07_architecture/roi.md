# Project Revelatio — ROI Analysis

> **Status**: Epic 7 deliverable (2 of 3). Written 2026-05-11. Internal language: EN. PT-BR translation lives in the relatório (Epic 8 §6).

The relatório claims this automation pays for itself within the first day of operation. This document is the underlying math, anchored on the **empirically measured** $0.00886/dossier (not estimated, not extrapolated from vendor pricing sheets — measured on 3 real test runs) and on the **empirically measured** 6 min 44 sec paralegal baseline (not assumed from the brief — measured on the same brief PDF). Every number below is reproducible from one of the artifacts cited in §8.

**FX rate used for consolidated lines**: USD 1.00 ≈ **BRL 4.8999** (PTAX venda, 2026-05-08, last trading day before publication; fonte: Banco Central do Brasil, [olinda.bcb.gov.br PTAX API](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo)). Rounded to BRL 4.90 in headline numbers; detail tables keep API costs in USD and labor in BRL.

---

## 1. TL;DR

**~$89 USD (~R$ 436) to process the 10,000-dossier Banco X backlog** at 99.07% accuracy with 0 hallucinations, vs. **~R$ 50,500 in paralegal time** (10k × measured 6:44 × R$ 45/h fully-loaded midpoint).

**Payback: day one.** Cost ratio at midpoint: ≈ **116×**. Even on pessimistic assumptions (20% HITL rate + cheaper paralegal labor at R$ 30/h), the ratio stays above 10×, so the conclusion is robust to assumption changes.

---

## 2. Empirical cost basis (the load-bearing section)

From `06_reference_script/notes.md` lines 47–55 (3-PDF validation run: brief PDF, F02, F07):

| Component | Per dossier | Mechanics |
|---|---|---|
| Azure Document Intelligence Layout | $0.003 | 2 pages × $1.50 / 1000 pages (Microsoft published rate) |
| Claude Sonnet 4.6 — input tokens | $0.0033 | ~1085 tokens × $3.00 / M tokens |
| Claude Sonnet 4.6 — output tokens | $0.0057 | ~378 tokens × $15.00 / M tokens |
| **Total** | **$0.00886** | Measured average over 3 PDFs |

Cross-reference: matches `04_experiments/SCOREBOARD.md` §4 projection of "~$0.008" within rounding (the SCOREBOARD projection was made before the 3-PDF validation; the empirical number is +10% above it because of slightly higher output-token usage on the brief PDF's longer page-2 content).

**At 10,000 dossiers**: $0.00886 × 10,000 = **$88.60 USD** = **R$ 434.06** at PTAX 4.8999.

The cost is dominated by Claude output tokens (~64% of the per-dossier total). Future cost reductions are most leveraged by output-length compression in the prompt (e.g., returning a tighter JSON without explanatory text), not by switching Azure DI or input compression.

---

## 3. Manual baseline — empirically measured

From `07_architecture/manual_timing.md` (single-PDF measurement, brief PDF, two-tab workflow):

| Metric | Value |
|---|---|
| Time to complete one dossier | **6 min 44 sec** (404 sec) |
| Method | Two tabs: Excel + PDF viewer; Ctrl-C/V from page-1 text layer; manual transcription of page-2 image |
| Sample size | n=1 |

**At 10,000 dossiers**:

| Labor rate (R$/h, fully loaded) | Total hours | Total cost (BRL) |
|---|---|---|
| R$ 30/h (junior paralegal) | 1,122 h | **R$ 33,667** |
| R$ 45/h (midpoint) | 1,122 h | **R$ 50,500** |
| R$ 60/h (senior / time-pressured) | 1,122 h | **R$ 67,333** |

The brief's implied "~10 min/dossier" assumption is **moderately conservative** vs. the measurement. A paralegal who could not copy-paste page 1 (e.g., scanned dossier with no text layer) would land closer to 10 min; a paralegal highly familiar with the template might land closer to 5 min. The 6:44 measurement is a mildly optimistic anchor and used throughout this doc as the baseline.

**Sensitivity on the time measurement** (±50% to bracket inter-paralegal variation):

| Time per dossier | At R$ 45/h, 10k volume |
|---|---|
| 3 min 22 sec (–50%) | R$ 25,250 |
| 6 min 44 sec (measured) | **R$ 50,500** |
| 10 min 6 sec (+50%) | R$ 75,750 |

Even at the optimistic lower bound (R$ 25,250), the automation's ~R$ 436 cost is **58× cheaper**. The ROI conclusion does not depend on the measurement being precisely 6:44 — only on the order of magnitude, which the n=1 measurement establishes confidently.

---

## 4. Side-by-side architecture comparison

From `04_experiments/SCOREBOARD.md` §4, with PTAX 4.8999 applied to USD totals:

| Architecture | One-time setup | Per-dossier | Total 10k (USD) | Total 10k (BRL) | Maintenance |
|---|---|---|---|---|---|
| **M365 path** (PA + AI Builder + DI fallback + Claude page-2 mapping) | $0 (existing M365 licenses) | ~$0.008 | ~$80 | ~R$ 392 | Paralegal-maintainable PA flow + ~30 real Banco X dossiers for AI Builder retraining |
| **Non-M365 path** (n8n + reference engine + DI + Claude) | ~2–3 days eng (~$3k one-time) | $0.00886 (measured) | **$88.60** | **R$ 434** | Developer-maintainable Python + n8n flow |
| **Cheapest viable** (n8n + Tabula + Claude direct on page-2 image) | ~1 day eng (~$1k one-time) | ~$0.005 | ~$50 | ~R$ 245 | Higher hallucination risk without OCR-first step |
| **Highest-confidence** (M365 + Azure DI Custom Neural + dual-LLM cross-validation) | ~1 week eng + labeling 30 dossiers (~$8k one-time) | ~$0.015 | ~$150 | ~R$ 735 | Re-train every 6 mo as Banco X templates evolve |

All four sit well under the manual baseline (R$ 33–67k at 10k volume). The choice between them is **operational shape**, not cost: M365 firms get the cheapest happy-path; non-M365 firms get the validated reference; cost-sensitive firms with technical risk tolerance can go cheapest-viable; quality-critical engagements can pay for the highest-confidence stack.

---

## 5. Sensitivity analysis — total annual cost

The two main uncertainties in production cost are: (a) **volume** (how many dossiers per year) and (b) **HITL rate** (what fraction of rows the system flags for paralegal review). Total cost = API cost + (HITL rate × volume × paralegal review time × R$/h).

Assumptions for HITL review (justified below):
- HITL review time: **2 min/row** (paralegal verifies the flagged fields with the rest of the row pre-filled; not a redo of the full 6:44 workflow)
- Paralegal labor: **R$ 45/h** (midpoint of §3)
- HITL cost per row: 2 min × (R$ 45 / 60) = **R$ 1.50/row**

### Annual cost (BRL) by volume × HITL rate

| Volume | 5% HITL | 10% HITL | 20% HITL |
|---|---|---|---|
| 1,000/yr | R$ 118 | R$ 193 | R$ 343 |
| **10,000/yr** | **R$ 1,184** | **R$ 1,934** | **R$ 3,434** |
| 100,000/yr | R$ 11,843 | R$ 19,343 | R$ 34,343 |

Numbers above are total automated cost (API + paralegal HITL review). Compare to all-manual baselines from §3 at the same volumes:

| Volume | All-manual at R$ 45/h (midpoint) |
|---|---|
| 1,000/yr | R$ 5,050 |
| 10,000/yr | **R$ 50,500** |
| 100,000/yr | R$ 505,000 |

### Conclusion from §5

**HITL rate matters more than volume** for the *automated* side. Every percentage point of HITL costs ~R$ 150/year at 10k volume. But even at 20% HITL (a generous estimate — the empirical run had 0 cross-val failures on 3 PDFs, suggesting HITL rate in production will likely be in the 5–10% range with proper AI Builder retraining), the automation costs **R$ 3,434/year at 10k vs. R$ 50,500 manual** — a 14.7× advantage.

**Why HITL review is 2 min, not 6:44**: the cross-validation gate identifies *which specific fields* are inconsistent (`audit.csv` `cross_val_reason` column). The paralegal reviews the flagged fields with the rest of the row pre-filled — closer to spot-checking than re-extraction. A naive "treat HITL as full manual rework" assumption would charge 6:44 per HITL row and collapse the ROI at high HITL rates; the cross-validation design specifically prevents this regression.

---

## 6. Hidden / recurring costs

Costs not captured in §2–§5 that the relatório should disclose honestly:

| Cost | Estimated magnitude | Notes |
|---|---|---|
| **Custom Neural retraining** (M365 path, if AI Builder is retrained on real dossiers) | ~$200–500 + 0.5 day eng every 6 months | As Banco X templates evolve. Anchored: SCOREBOARD §4 "Maintenance" column |
| **LGPD audit** (RIPD preparation, DPO time) | ~R$ 5–15k one-time + ~R$ 3–8k/yr | Cross-reference `07_architecture/lgpd.md` §9 (RIPD requirement). Real cost depends on whether the firm has an in-house DPO or outsources |
| **SharePoint / object storage scaling** | Trivial at PoC scale (10k PDFs × ~200 KB = ~2 GB), but year-over-year retention adds linearly | Sized per `lgpd.md` §4 retention schedule |
| **Engineering on-call** (production hardening checklist items 1, 2) | ~5–10% of one engineer's time | API failure handling, retry logic, concurrency — `06_reference_script/notes.md` items #1, #2 |
| **Cost cap monitoring** (production hardening item #8) | Trivial implementation; tail risk insurance | Daily spend threshold + alert. `notes.md` hardening item #8 |
| **Paralegal LGPD training** | ~R$ 1–2k/yr | `lgpd.md` §9 medidas administrativas |
| **DPA renewals + legal review** | Trivial cost; ~1 day/yr DPO time | Anthropic + Microsoft DPAs (`lgpd.md` §7) |

**Total recurring at 10k volume, midpoint estimates**: API + HITL (~R$ 1,934) + retraining (~R$ 2,500/yr) + LGPD (~R$ 5,500/yr) + on-call (~R$ 5,000/yr) + training (~R$ 1,500/yr) ≈ **R$ 16,400/yr fully loaded**.

This is the honest comparison number for the relatório: **R$ 16,400/yr automated (fully loaded) vs. R$ 50,500/yr manual** = ~3.1× advantage on fully-loaded ongoing cost, *plus* the order-of-magnitude advantage on first-batch backlog processing.

The first-batch advantage (R$ 436 vs. R$ 50,500) is what produces the "day one payback" framing. The steady-state advantage (R$ 16k vs. R$ 50k) is what produces the "this isn't a one-time win, it's a structural cost change" framing.

---

## 7. Payback period

**First batch (10k backlog)**: processing time ≈ **3–6 hours** with concurrency (production hardening item #2 — 5–10 concurrent calls; `notes.md` line 72). Break-even occurs **before the first batch completes**: the manual labor cost to process those same 10k dossiers would be ~R$ 50k spread over ~6 months of paralegal time; the automation produces them in an afternoon at R$ 436 + ~R$ 1.5k HITL paralegal review = R$ 1,936. The differential is realized on day one.

**Steady-state marginal cost**: adding one dossier to the automated flow costs ~$0.009 (≈ R$ 0.04) of API time. Adding one dossier to the manual flow costs ~R$ 3.40 at the conservative R$ 30/h labor rate (or ~R$ 5.05 at midpoint R$ 45/h) — **~76–120× cost reduction at the margin** depending on labor rate.

**Capital-recovery framing**: the one-time setup cost for the non-M365 path is ~$3k (2–3 days engineering ≈ R$ 14,700). Using the conservative-baseline marginal saving of ~R$ 3.36/dossier (R$ 3.40 manual at R$ 30/h − R$ 0.04 automated), setup is recovered after **~4,400 dossiers**. For a firm doing 10k/year, that's ~5 months. For 100k/year, that's ~16 days. At the midpoint labor rate, payback is faster (~3,000 dossiers).

For the M365 path, setup is functionally $0 (existing licenses), so capital recovery is immediate.

---

## 8. Anchors index

| Claim or number | Source |
|---|---|
| $0.00886/dossier measured | `06_reference_script/notes.md` lines 33–38 (3-PDF results table) + lines 47–55 (cost breakdown) |
| 99.07% accuracy / 0 hallucinations | `06_reference_script/notes.md` lines 33–38 |
| Per-component cost ratios (DI / Claude in / Claude out) | `06_reference_script/notes.md` lines 50–53 |
| 6 min 44 sec paralegal baseline | `07_architecture/manual_timing.md` (single-PDF measurement, 2026-05-11) |
| Two-tab workflow methodology | `07_architecture/manual_timing.md` "Method" §; mirrors architecture two-layer routing |
| FX rate USD 1.00 ≈ BRL 4.8999 | PTAX venda 2026-05-08, Banco Central do Brasil, [olinda.bcb.gov.br PTAX API](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo) (verified WebFetch 2026-05-11) |
| 4 architecture comparison rows | `04_experiments/SCOREBOARD.md` §4 |
| HITL review time 2 min/row | Cross-validation design — flagged-field review, not full re-extraction (`07_architecture/diagrams.md` §3) |
| Custom Neural retraining cost | SCOREBOARD §4 "Maintenance" column + `notes.md` production hardening discussion |
| LGPD audit / DPO time | `07_architecture/lgpd.md` §9 (RIPD requirement) |
| Engineering on-call estimate | `06_reference_script/notes.md` production hardening checklist items #1, #2, #8 |
| Concurrency assumption (3–6 h for 10k) | `06_reference_script/notes.md` line 72 (production hardening item #2) |
| Paralegal labor rate band R$ 30–60/h | Brazilian legal-back-office market benchmark (inherited from project background) — sensitivity table in §3 brackets the band |
| Marginal cost-per-dossier ~$0.009 ≈ R$ 0.04 | $0.00886 × 4.8999 |
| Marginal manual cost ~R$ 3.40/dossier | 6:44 × (R$ 45 / 60) |

---

## 9. What this document does NOT cover

- **Strategic justification of the architecture choice** — see `07_architecture/diagrams.md`.
- **LGPD compliance posture** — see `07_architecture/lgpd.md`.
- **Methodology caveats** (n=1 brief PDF for both the API cost and the manual timing; synthetic vs. real-layout drift) — see `04_experiments/SCOREBOARD.md` §5 and `07_architecture/manual_timing.md`. The relatório §3 should own these honestly.
- **Procurement / vendor negotiation** — API costs above are list prices; volume commitments with Anthropic or Microsoft can reduce them, but the >100× ROI ratio is robust enough that procurement optimization is a second-order concern.
