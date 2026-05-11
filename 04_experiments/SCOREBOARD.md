# Project Revelatio — Tool Evaluation Scoreboard

**Source-of-truth synthesis for relatório §4 (avaliação de ferramentas) and demo video §2 (alternativas avaliadas).**

Date: 2026-05-10. Methodology: each hands-on tool was given the same brief example PDF (`00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf`) and the same extraction task (32 fields across page 1 client info + page 2 comprovantes). Scoring rules in `01_field_map/scoring_rubric.md`. Power Automate also tested against the 8-fixture synthetic corpus (F01–F08).

---

## 1. Headline scoreboard (brief example PDF)

| # | Tool | Class | Page 1 | Page 2 | Overall | Hallucinations | Latency | Cost class | Hands-on? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Power Automate + AI Builder** (Custom Extraction model) | M365 workflow + trained OCR | 100% (visual) | ⚠️ layout-sensitive¹ | 92.8%² | 0 | ~5–10s/doc | M365 trial / $30/user/mo | ✅ end-to-end flow |
| 2 | **ChatGPT 5.5 Thinking** | Frontier LLM chat | 100% | 100% | **100%** | 0 | 11.8s | Plus $20/mo or API ≈ $50–100/10k | ✅ |
| 3 | **Claude Opus 4.7** | Frontier LLM chat | 100% | 100% | **100%** | 0 | 10.46s | Plus $20/mo or API ≈ $50–100/10k | ✅ |
| 4 | **NotebookLM** (Gemini default) | Source-grounded LLM | 100% | 100% | **100%** | 0 | 22.23s | Free / bundled | ✅ |
| 5 | **Azure DI Layout** (prebuilt) | Commercial OCR + structure | 100% (2 tables, 16 cells) | structured text, no kv³ | n/a⁴ | 0 | ~5s | $1.50/1k pages (~$30/10k) | ✅ |
| 6 | **Tabula** (tabula-py 2.10) | OSS deterministic | 100% (16 cells) | **0%** (no OCR) | n/a⁵ | 0 | 0.71–1.79s | $0 | ✅ |
| 7 | Microsoft Copilot | M365 LLM wrapper | (OpenAI family — see #2) | — | — | — | — | M365 / Copilot Pro | ⏭️ skipped — proxied by ChatGPT |
| 8 | Make / Integromat | iPaaS workflow | spec only | spec only | — | — | — | $9–$29/mo + per-op | dossier only |
| 9 | n8n | OSS workflow | spec only | spec only | — | — | — | free self-hosted | dossier only |

**Footnotes**:
1. AI Builder on brief PDF page 2 returned **footer text and pagination markers as field values** (e.g., "Documento ficticio para teste técnico" extracted as `proof_reference`). This is the production-blocking failure mode discovered in Epic 5.2. **Cause**: AI Builder is template-matching against the training-distribution layout; brief PDF page 2 is out-of-distribution.
2. 92.8% is the **synthetic corpus** average (F01, F02, F05, F06 — covering ~132 evaluable cells with 0 hallucinations). Brief PDF page 1 alone was ~100%; page 2 dragged the dossier-level score down.
3. Azure DI Layout returns text + tables + paragraphs + selection marks for page 2 cleanly (`Titular: Maria Almeida Costa`, etc.), but does NOT auto-structure page-2 paragraph data into key-value JSON. Needs LLM-on-top or Custom Neural for that.
4. Azure DI scored as a **component**, not an end-to-end extractor. Its role is OCR + structure. End-to-end accuracy belongs to whatever LLM/parser is layered above.
5. Same — Tabula scored as a **component** (page-1 extractor). Not a complete solution.

---

## 2. Qualitative comparison

| Tool | Training required? | Layout-tolerant? | OSS/Commercial | Production-ready? | Audit trail? |
|---|---|---|---|---|---|
| PA + AI Builder | **Yes** — ≥5 labeled docs | **No** (template-matching) | Commercial (M365) | Yes, with cross-validation | Yes (Power Automate run history) |
| ChatGPT 5.5 / Claude / NotebookLM | No | **Yes** (vision-language) | Commercial | Via API only — chat UI not scalable | Partial (API logs) |
| Azure DI Layout | No (prebuilt) | **Yes** | Commercial | Yes (as a component) | Yes (Azure Monitor) |
| Azure DI **Custom Neural** | **Yes** — 5+ docs, ~30 min train | **Yes** | Commercial | Yes — strategic recommendation | Yes |
| Tabula | No | Partial (heuristic) | OSS | Page 1 only | No (run-locally CLI) |
| Make | No | n/a (workflow) | Commercial | Yes (workflow layer) | Yes |
| n8n | No | n/a (workflow) | OSS | Yes (workflow layer) | Yes |

---

## 3. Role in the recommended architecture

The relatório recommends a **hybrid stack with two-layer routing**, not a single tool. Each evaluated tool maps to a named role (or is explicitly excluded):

| Role | Recommended tool | Why | Empirical evidence |
|---|---|---|---|
| **Primary workflow (M365 firms)** | Power Automate | Native M365 integration, audit trail, no-code maintainable by paralegals | End-to-end flow built in Epic 5.2 |
| **Page-1 deterministic extractor (M365 path)** | AI Builder Custom Extraction | Validated on synthetic corpus, low cost, no LLM dependency | 100% page-1 visual on synth + brief |
| **Page-1 deterministic extractor (non-M365 path)** | Tabula or pdfplumber | Zero cost, 0.7s latency, deterministic | 16/16 cells correct on brief, F01, F07 |
| **Page-2 OCR + structure (both paths)** | Azure DI Layout | Layout-tolerant where AI Builder failed; not source of PA bug | Page-2 paragraphs detected correctly on brief PDF |
| **Page-2 field mapping (both paths)** | Claude API or GPT API | 100% on brief PDF; cross-validated across 3 frontier LLMs | LLM round-robin (Epic 5.3–5.5) |
| **Page-2 layout-tolerant extractor (production strategic)** | Azure DI Custom Neural | Trainable on real Banco X dossiers, beats template models on layout drift | Spec-only — requires 30+ real dossiers |
| **Cross-validator (production)** | Per-page CPF/name consistency rules | Catches "wrong page-2 in wrong dossier" + AI Builder OOD failures | Documented in Epic 5.2 finding #5 |
| **Workflow orchestrator (non-M365 firms)** | n8n self-hosted | OSS, no vendor lock-in, can call Azure DI + Claude API | Dossier `02_tool_universe/05_n8n.md` |
| **HITL queue** | SharePoint list (M365) or any DB + form (non-M365) | Reviewer-friendly, audit-able | Documented design, not built |

### Explicitly excluded with one-line reasons

| Tool | Why excluded |
|---|---|
| Microsoft Copilot | OpenAI-family proxy — ChatGPT result already captures behavior, no marginal info |
| Make | More expensive than n8n for non-M365 firms; less native than Power Automate for M365 firms — middle ground with no use case |
| Standalone Tabula | Cannot handle page-2 image content; 50% of dossier invisible |
| Standalone ChatGPT/Claude/NotebookLM chat UI | Not scalable to 10k dossiers via UI; via API they become the page-2 mapper above |
| Tesseract (raw OCR) | No structure recognition — Azure DI Layout strictly dominates at comparable cost |

---

## 4. Cost projection (10,000 dossiers)

| Architecture | One-time | Per-dossier | Total 10k | Maintenance |
|---|---|---|---|---|
| **M365 path** (PA + AI Builder + Azure DI fallback + Claude API for page-2 mapping on OOD layouts) | $0 (M365 trial / existing license) | ~$0.008 | ~$80 | Paralegal-maintainable PA flow + ~30 real Banco X dossiers for AI Builder retraining |
| **Non-M365 path** (n8n + Tabula + Azure DI Layout + Claude API) | ~2–3 days eng setup | ~$0.008 | ~$80 | Developer-maintainable Python + n8n flow |
| **Cheapest viable** (n8n + Tabula + Claude API direct for page-2 image) | ~1 day eng | ~$0.005 | ~$50 | Higher hallucination risk without OCR-first step |
| **Highest-confidence** (M365 + Azure DI Custom Neural + dual-LLM cross-validation) | ~1 week (labeling 30 dossiers + training) | ~$0.015 | ~$150 | Re-train every 6 mo as Banco X templates evolve |

All four are well under the budget headroom for a firm processing 10k dossiers/year (compare to ~R$ 20k–60k/year in paralegal time at conservative 10 min/dossier).

---

## 5. Methodology caveats (own honestly in relatório §3)

1. **n=1 for brief PDF**. All scoring against `gold_truth.json` for one real-shape document. Production deployment requires validation on a real Banco X sample of 30–100 dossiers.
2. **Synthetic corpus shares field LABELS but not VISUAL LAYOUT with brief example**. This is the source of AI Builder's page-2 failure — and a deliberate finding, not a bug. The synthetic corpus validated the deterministic page-1 pipeline; the brief PDF then exposed the page-2 layout drift problem.
3. **No Custom Neural training tested**. Requires labeling time + 5+ real-shape docs, out of scope for the evaluation window. Strategic recommendation rests on Microsoft's published benchmarks for layout-tolerant trained models + the architectural argument.
4. **LLM scores at n=1 are not statistical**. 3-way 100% convergence is a strong cross-validation signal on a clean PDF but doesn't probe edge cases (low-quality scans, partial obscurations). The synthetic corpus F04/F07/F08 would probe these — out of scope for the round-robin in this window.
5. **Latency measured end-to-end including upload + chat UI rendering** for LLMs, not pure inference. Production via API will be faster (~2–4s).
6. **No multilingual or PII redaction tests run**. Brief PDF is fictitious; real Banco X dossiers contain LGPD-regulated PII that must be handled per Epic 7 architecture (in-tenant processing, no third-party logging).

---

## 6. The one-paragraph summary for the relatório

> *Avaliamos 9 ferramentas representando 4 categorias arquiteturais: workflows comerciais (Power Automate, Make), workflows OSS (n8n), LLMs frontier (ChatGPT, Claude, NotebookLM, Copilot) e OCR/extração estruturada (Azure Document Intelligence, Tabula). Todas as três LLMs frontier obtiveram 100% de acurácia com zero alucinações no PDF de exemplo. Power Automate + AI Builder obteve 92,8% médio no corpus sintético sem alucinações, mas exibiu falha layout-sensitive na página 2 do PDF de exemplo (campos extraídos de rodapés). Azure DI Layout reconheceu corretamente a estrutura de ambas as páginas sem treinamento. Tabula extraiu 100% da página 1 a custo zero, mas falhou totalmente na página 2 (não possui OCR). A arquitetura recomendada é, portanto, **híbrida e em duas camadas** — extração determinística na página 1, OCR+LLM na página 2, com regras de cross-validation e fila HITL para confiabilidade em produção — não uma ferramenta única.*

---

## 7. Artifacts index

| Tool | Notes | Raw output | Scorecard |
|---|---|---|---|
| Power Automate | `02_power_automate/notes.md` | `02_power_automate/raw_output/debtor_extraction.xlsx` | `02_power_automate/scorecard.json` |
| ChatGPT | inline (resume) | `03_chatgpt/output.json` | `03_chatgpt/output_scorecard.json` |
| Claude | inline (resume) | `04_claude/output.json` | `04_claude/output_scorecard.json` |
| NotebookLM | inline (resume) | `05_notebooklm/output.json` | `05_notebooklm/output_scorecard.json` |
| Azure DI | `06_azure_di/notes.md` | `06_azure_di/output.json` | n/a (component, not end-to-end) |
| Tabula | `07_tabula/notes.md` | `07_tabula/{brief,F01,F07}_page*_table*.csv` | n/a (component, not end-to-end) |
