# Dossier — Tabula

> Brief-listed tool · Will test hands-on in **Epic 5.4** — to **demonstrate its strength on page 1 and its hard limit on page 2**.

## What it is
Open-source desktop app + CLI (Java) that extracts tables from text-based PDFs. Mature, free, ~10 years old. Outputs CSV / TSV / JSON. Two extraction modes: lattice (for ruled tables) and stream (for whitespace-aligned).

## Where it fits in our pipeline
- **Extractor for page 1**: ✅ — page 1 is exactly its sweet spot (digital text, table-shaped). Will likely extract all 16 page-1 fields nearly free, in milliseconds, with zero LLM cost.
- **Extractor for page 2**: ❌ — page 2 is rasterized image. Tabula has **no OCR**. It will return empty.
- **Orchestrator**: no.

## Hands-on plan (Epic 5.4)
1. Open Tabula GUI (or `tabula-py` Python wrapper).
2. Load `exemplo_pdf_cliente_devedor_ficticio.pdf`, lattice mode on page 1.
3. Auto-detect or hand-draw selection on the two tables → export to CSV.
4. Score against gold (page-1 portion only).
5. Repeat on page 2 → expect empty output → screenshot the empty result as evidence in the relatório.
6. Conclusion: Tabula = strong free baseline for the page-1 layer, useless for page 2 alone.

## LGPD / data-residency
- **Local-only**, runs on operator's machine. No data leaves at all.
- Strongest possible posture (tied with Docling and pdfplumber).

## Cost class
- 💲 — free OSS (MIT license). Java runtime needed.

## Fit verdict
**⚠️ Useful as a free baseline component** for the page-1 layer in a hybrid pipeline; **insufficient alone**. We do not propose Tabula as the standalone solution — we propose it as **one of two valid choices for the page-1 extractor**, alongside `pdfplumber` (which is more programmable). Both are local, both are free, both ace digital-text tables.

## Why include it at all in the relatório
- Honors the brief by addressing it
- Shows we understand the **two-layer routing** insight in concrete terms (Tabula nails layer 1, fails layer 2 — therefore architecture must route per layer)
- Demonstrates that the cheapest tool can win for the right layer
