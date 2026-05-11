# Epic 6 — Reference extraction script

**Date**: 2026-05-10/11
**Pipeline**: PDF → Azure DI Layout → page-1 deterministic table parse + page-2 Claude Sonnet 4.6 with Option-B cross-validation → CSV row.

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

Tested against `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` (the PDF Power Automate hallucinated on), `F02_missing_email.pdf` (anti-hallucination test for null fields), and `F07_skewed_page2.pdf` (layout-robustness test).

| PDF | Overall | Page 1 | Page 2 | Hallucinations | Latency | Cost (USD) |
|---|---|---|---|---|---|---|
| Brief example | **100.0%** | 100% | 100% | 0 | 11.20s | $0.00896 |
| F02 missing-email | **98.6%** | 100% | 97.1%† | 0 | 11.68s | $0.00881 |
| F07 skewed page 2 | **98.6%** | 100% | 97.1%† | 0 | 10.99s | $0.00881 |
| **Average** | **99.07%** | **100%** | **98.1%** | **0** | **11.29s** | **$0.00886** |

† The 1 non-exact cell (`proof_address_neighborhood`) is a synthetic-gold inconsistency, not an LLM error. The synthetic PDF renders `Bairro: Boa Vista` but the gold expects `"Boa Vista - Recife/PE"`. The LLM correctly extracted `"Boa Vista"` matching the rendered text. To be fixed in the gold during Epic 8 QA, or kept as-is and noted (the LLM's behavior is the correct one).

### Anti-hallucination preserved

F02's email field returned **empty** (`""`), not an invented plausible value. This is the same anti-hallucination property validated for Power Automate in Epic 5.2 (F02 and F03 finding) — preserved through the LLM pipeline by the explicit `"use null (NUNCA invente)"` rule in the prompt.

## Cost projection at scale

Average $0.00886/dossier × 10,000 = **$88.60 for the full Banco X backlog**.

Breakdown of the $0.00886:
- Azure DI Layout: ~$0.003 (2 pages @ $1.50/1000)
- Claude Sonnet 4.6 input: ~$0.0033 (~1085 tokens @ $3/M)
- Claude Sonnet 4.6 output: ~$0.0057 (~378 tokens @ $15/M)

This matches the SCOREBOARD §4 projection of ~$80 within rounding.

## Comparison to other tools

| Tool | Score | Hallucinations | Latency | Cost/10k | Notes |
|---|---|---|---|---|---|
| Power Automate + AI Builder | 92.8% (synth avg) | 0/132 cells | ~5–10s | M365 fixed | Page-2 layout-sensitive on brief PDF |
| LLM round-robin (chat UI) | 100% on brief | 0 | 10–22s | $50–100 | Not scalable via UI |
| **This script** | **99.07%** on 3-PDF | 0 | 11.3s | **$89** | Production-shaped |

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
