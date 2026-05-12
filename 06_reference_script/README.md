# Revelatio — Reference Extraction Pipeline

Production-shaped Python pipeline that extracts structured data from Banco X debtor-dossier PDFs into a CSV ready for Excel. Two interfaces: **CLI** (for batch operation) and **Streamlit UI** (for demo / one-off drag-drop use).

Empirically validated at **100% accuracy** on a 3-PDF baseline corpus **plus** an out-of-distribution holdout (`F09_brief_shape.pdf`, brief-faithful layout, fresh client data) — also 100%. **0 hallucinations** across all 4 PDFs, **~$0.0093 per dossier**. See `notes.md` for full results, the OOD validation section, prompt-rule history, and production-hardening checklist.

---

## Prerequisites

1. **Python venv** at project root (`.venv/`) — already provisioned.
2. **Java** (for the Tabula scoring side-tool, not the main pipeline) — `java -version` should work.
3. **`.env` file at project root** with three values (template at `.env.example`):
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   AZURE_DI_ENDPOINT=https://<region>.api.cognitive.microsoft.com/
   AZURE_DI_KEY=<32-hex-string>
   ```

---

## Quick start — Streamlit demo UI

Best for: one-off use, video recording, showing stakeholders how it would feel in production.

```bash
.venv/bin/python -m streamlit run 06_reference_script/app.py
```

Streamlit opens a browser tab at `http://localhost:8501`. Drag one or more PDFs onto the uploader → click **▶ Extrair** → review the table on screen → click **⬇ Baixar dossiers.csv** to download.

The "Detalhes operacionais" expander at the bottom shows the audit log (latencies, token counts, cost per dossier, cross-validation mismatches) and lets you download `audit.csv` separately.

Stop the server with `Ctrl+C` in the terminal.

---

## Quick start — CLI (batch mode)

Best for: processing the actual 10k-dossier backlog.

```bash
# Single PDF
.venv/bin/python 06_reference_script/extract_dossier.py path/to.pdf --out output_dir/

# Batch (all PDFs in a directory)
.venv/bin/python 06_reference_script/extract_dossier.py --batch input_dir/ --out output_dir/
```

Outputs two files in `--out`:
- `dossiers.csv` — one row per PDF, business columns + `needs_review` flag.
- `audit.csv` — one row per PDF, operational data (latencies, tokens, cost, mismatches, errors).

Paralegals open `dossiers.csv` in Excel and filter on `needs_review = TRUE` to focus manual review only on flagged rows.

---

## Score output against gold (for development)

If the PDFs have a matching gold JSON in `01_field_map/` or `05_synthetic_data/gold/`, this validates the pipeline's accuracy:

```bash
.venv/bin/python 06_reference_script/score_pipeline_output.py 06_reference_script/test_corpus/dossiers.csv
```

---

## File map

| File | Purpose |
|---|---|
| `extract_dossier.py` | CLI orchestrator (single + batch modes) |
| `azure_di_client.py` | Azure DI Layout API wrapper |
| `page1_parser.py` | Deterministic page-1 table parsing (no LLM) |
| `claude_extractor.py` | Page-2 extraction via Claude Sonnet 4.6 with Option-B cross-validation |
| `app.py` | Streamlit demo UI |
| `score_pipeline_output.py` | CSV → gold-schema adapter + scorer |
| `notes.md` | Design rationale + empirical results + production hardening checklist |
| `test_corpus/` | Sample outputs (`dossiers.csv`, `audit.csv`) from the 3-PDF validation run |

---

## Troubleshooting

**`KeyError: 'AZURE_DI_ENDPOINT'`** → `.env` is missing or malformed. Copy `.env.example` to `.env` at project root and fill in real values.

**`anthropic.AuthenticationError`** → `ANTHROPIC_API_KEY` in `.env` is wrong, expired, or has no credit. Check `https://console.anthropic.com/settings/keys`.

**`azure.core.exceptions.ClientAuthenticationError`** → `AZURE_DI_KEY` is wrong, or the endpoint doesn't match the resource's region. Verify both in Azure Portal → `di-revelatio-test` → "Keys and Endpoint".

**Streamlit shows "Connection error"** → the script process crashed. Check the terminal where you ran `streamlit run` for the Python traceback.

**Tabula scoring fails** → that's a separate tool in `04_experiments/07_tabula/`, not part of this pipeline. The pipeline does not require Tabula.

---

## What this is NOT

This is a **PoC engine**, not a production deployment. The `notes.md` file lists 8 production-hardening items (retry logic, concurrency, prompt caching, schema versioning, PII masking, auth, idempotency, cost caps) that must be addressed before real Banco X deployment. The Streamlit UI specifically is a **demo skin** — for production, the engine wraps inside n8n (recommended for non-M365 firms) or a custom web app built by the firm's IT (recommended for firms with internal engineering).
