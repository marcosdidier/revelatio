# Epic 6 — Reference extraction script

**Date**: 2026-05-10/12
**Pipeline**: PDF → Azure DI Layout → page-1 deterministic table parse + page-2 Claude Sonnet 4.6 with Option-B cross-validation → CSV row.

**2026-05-12 update**: prompt updated to enforce **literal field extraction** (return everything after the field label verbatim, do not segment compound values). This eliminated a parsing quirk on `proof_address_neighborhood` (the LLM had been semantically dropping the city/UF suffix from values like `Bairro: Boa Vista - Recife/PE`). After the change, the 3-PDF test corpus scores **100,0% on every PDF**, both pages, with 0 hallucinations. Average cost rose marginally to **$0,00934 / dossier** due to ~120 extra input tokens for the new rule.

## What this exists for

Reference implementation of the non-M365 production architecture. Demonstrates that the recommended hybrid stack (deterministic OCR + LLM field mapping + cross-validation) is **mechanically buildable** in a few hundred lines of Python. For real production, this engine sits behind one of: n8n workflow with file-upload trigger (recommended for non-M365 firms), Flask/Django web form (custom), or watched folder in batch mode. The Streamlit `app.py` is a **demo skin** for the video, NOT a production tool.

## Architecture

```
PDF
  → azure_di_client.analyze_pdf()           [Azure DI Layout, ~6–7s]
      → returns full layout dict (text + tables + paragraphs + spans)
  → page1_parser.parse_page1()              [deterministic, ~0s]
      → reads Campo/Informação tables auto-detected on page 1
      → normalizes dates DD/MM/YYYY → YYYY-MM-DD
      → normalizes money "R$ 18.450,00" → "18450.00"
      → normalizes "147 dias" → 147 (int)
  → claude_extractor.extract_page2()        [Claude Sonnet 4.6, ~4–5s]
      → sends page-2 text + page-1 client_name/CPF as anchors
      → LLM extracts page-2 fields AND flags cross-validation mismatches
  → merge → dossiers.csv row + audit.csv row
```

**Option-B cross-validation prompt design**: the LLM receives page-1 anchors (`client_name`, `cpf`) and is asked to flag any case where page-2 fields (`proof_address_holder`, `payer`) don't match. Mismatches surface as `needs_review=TRUE` in `dossiers.csv` and `cross_val_consistent=FALSE` with a description in `audit.csv`. This directly mitigates the production-blocking failure mode discovered in Epic 5.2: a high-confidence single-field gate (e.g., CPF) routed a dossier to "approved" even when page-2 content was garbage.

## Empirical results (3-PDF test corpus)

Tested against `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` (the PDF Power Automate hallucinated on), `F02_missing_email.pdf` (anti-hallucination test for null fields), and `F07_skewed_page2.pdf` (layout-robustness test). Results below reflect the **post-2026-05-12 prompt** with the literal-extraction rule.

| PDF | Overall | Page 1 | Page 2 | Hallucinations | Latency | Cost (USD) |
|---|---|---|---|---|---|---|
| Brief example | **100.0%** | 100% | 100% | 0 | 10.84s | $0.00938 |
| F02 missing-email | **100.0%** | 100% | 100% | 0 | 12.17s | $0.00932 |
| F07 skewed page 2 | **100.0%** | 100% | 100% | 0 | 10.76s | $0.00931 |
| **Average** | **100.0%** | **100%** | **100%** | **0** | **11.26s** | **$0.00934** |

### History note — the parsing quirk we fixed

Before the 2026-05-12 prompt update, the F02 and F07 PDFs scored 98,6% overall (97,1% page 2) due to a single non-exact cell in `proof_address_neighborhood`. The PDF renders `Bairro: Boa Vista - Recife/PE` (`05_synthetic_data/generate_pdfs.py` line 237 passes the full value to the renderer; gold matches the same value at line 368), but the LLM was returning only `"Boa Vista"` — semantically interpreting `Bairro` as "just the neighborhood name" and dropping the city/UF suffix. The fix was a single rule added to `claude_extractor.py` (Regra 2): *extract each field value literally, do not segment compound values*. This restored 100% on every cell of every test PDF and preserves anti-hallucination (we are being more literal, not less).

### Anti-hallucination preserved

F02's email field returned **empty** (`""`), not an invented plausible value. This is the same anti-hallucination property validated for Power Automate in Epic 5.2 (F02 and F03 finding) — preserved through the LLM pipeline by the explicit `"use null (NUNCA invente)"` rule in the prompt.

### OOD holdout validation — F09_brief_shape (2026-05-12)

To validate that the literal-extraction rule generalizes beyond the in-distribution test PDFs, we generated `F09_brief_shape.pdf` — a brief-faithful layout (§3+§4 prose blocks, `"(ficticio)"` CPF suffix, combined `Agencia: X | Conta: Y` page-2 line, running footer with page number) with completely new client data (Ana Beatriz Souza Carvalho, Salvador/BA, financiamento de veículo) that the pipeline had never seen. Generator: `05_synthetic_data/generate_brief_shaped_ood.py`. Gold: `05_synthetic_data/gold/F09_brief_shape.json`.

| Metric | F09 result |
|---|---|
| Overall | **100,0%** |
| Page 1 | 100% |
| Page 2 | 100% |
| Hallucinations | 0 |
| Latency | 11,54s |
| Cost | $0,00932 |

Adversarial features that behaved correctly:
- Combined `Agencia: 5678 | Conta: 00045123-7` line was correctly split into `bank_branch="5678"` and `bank_account="00045123-7"` — a real test of literal extraction on a single-line dual-field rendering.
- Bairro `Centro - Salvador/BA` extracted verbatim (the literal-extraction rule's canonical test case applied to fresh data).
- CPF table cell `567.890.123-45 (ficticio)` correctly emitted as `567.890.123-45` by the page-1 parser; the `"(ficticio)"` disclaimer suffix did not contaminate the field.
- Page-1 §3 and §4 prose blocks (not present in F01–F08 fixtures) did not produce spurious fields.
- Running footer with `Pagina N` did not leak into any field value — the same failure mode that Power Automate exhibited on the brief PDF page 2 (Epic 5.2 Phase 1.5) is fully bounded by the literal-extraction prompt + the page-2 region delimitation.

Combined with the 3-PDF baseline, this brings the pipeline's empirical result to **100% on 4 PDFs, 0 hallucinations, 1 of which is a true OOD holdout**.

## Cost projection at scale

Average **$0.00934/dossier × 10,000 = $93.37** for the full Banco X backlog (≈ R$ 457,45 at PTAX 4,8999 venda 2026-05-08).

Breakdown of the $0.00934:
- Azure DI Layout: ~$0.003 (2 pages @ $1.50/1000, unchanged)
- Claude Sonnet 4.6 input: ~$0.00362 (~1208 tokens @ $3/M — +~120 tokens vs. the pre-2026-05-12 prompt for the literal-extraction rule)
- Claude Sonnet 4.6 output: ~$0.00572 (~381 tokens @ $15/M, unchanged)

This still sits at the lower end of the SCOREBOARD §4 projection band of ~$80–$150 across architecture variants.

## Comparison to other tools

| Tool | Score | Hallucinations | Latency | Cost/10k | Notes |
|---|---|---|---|---|---|
| Power Automate + AI Builder | 92.8% (synth avg) | 0/132 cells | ~5–10s | M365 fixed | Page-2 layout-sensitive on brief PDF |
| LLM round-robin (chat UI) | 100% on brief | 0 | 10–22s | $50–100 | Not scalable via UI |
| **This script** | **100%** on 3-PDF + OOD holdout | 0 | 11.3s | **~$93** | Production-shaped |

The reference script is the only tested configuration that simultaneously: (a) handles page-2 layout drift like the LLMs, (b) operates at API scale unlike the chat UIs, (c) provides full audit trail and cross-validation unlike a plain LLM call, (d) costs less than 100 USD for the full backlog.

## Production hardening checklist

What this PoC script does NOT do, that a real production deployment must add:

1. **Retry logic**: Azure API or Anthropic API transient errors should retry with exponential backoff. Currently fails the row and continues to the next.
2. **Concurrency**: Batch mode is sequential. For 10k dossiers at ~11s each = ~30 hours single-threaded. Production should parallelize 5–10 concurrent calls (both APIs handle this easily). With concurrency, full backlog ≈ 3–6 hours.
3. **Prompt caching**: Current prompt is ~250 tokens — below the 1024-token Anthropic cache threshold. For production prompts with few-shot examples or longer schema docs, add `cache_control: ephemeral` to static parts.
4. **Schema versioning**: The CSV column order is hardcoded. If the firm adds/renames fields in their gold, both the script and any downstream Excel formulas break. Production should version the schema.
5. **PII redaction in logs**: `audit.csv` may leak CPFs if mismatches include them. For LGPD compliance (see Epic 7), mask or hash CPFs in any persisted log.
6. **Auth**: Streamlit `app.py` has no auth. Production replacement (n8n / Flask) must add the firm's SSO.
7. **Idempotency**: Re-running the script on the same PDF re-charges the APIs. Production should cache by content hash.
8. **Cost cap**: No spending limit. Production should fail-loudly above a configurable daily threshold.

## File index

| File | Purpose | Lines |
|---|---|---|
| `azure_di_client.py` | Azure DI Layout wrapper | 31 |
| `page1_parser.py` | Deterministic page-1 table parsing | 79 |
| `claude_extractor.py` | Claude Sonnet 4.6 + Option-B prompt | 95 |
| `extract_dossier.py` | CLI orchestrator (single + batch modes) | 130 |
| `app.py` | Streamlit demo UI | 110 |
| `score_pipeline_output.py` | CSV → gold-schema adapter + scorer call | 95 |

## How to run

```bash
# Single PDF
.venv/bin/python 06_reference_script/extract_dossier.py path/to.pdf --out output_dir/

# Batch (recommended for evaluation)
.venv/bin/python 06_reference_script/extract_dossier.py --batch input_dir/ --out output_dir/

# Score against gold (only works for PDFs with gold JSON in 01_field_map/ or 05_synthetic_data/gold/)
.venv/bin/python 06_reference_script/score_pipeline_output.py output_dir/dossiers.csv

# Streamlit demo UI (for video recording)
.venv/bin/python -m streamlit run 06_reference_script/app.py
```

## What `.env` must contain

```env
ANTHROPIC_API_KEY=sk-ant-...
AZURE_DI_ENDPOINT=https://<region>.api.cognitive.microsoft.com/
AZURE_DI_KEY=<32-hex-string>
```

The `.env.example` at the project root is the template. `.env` is gitignored.
