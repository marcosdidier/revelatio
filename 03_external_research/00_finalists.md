# External Research — Finalists for Epic 5 Hands-On

> **Why this exists:** Epic 3 surfaced **20+ tools** beyond the brief's list. Not all need a hands-on test. This file documents which external tools advance to Epic 5 and why — so the relatório can show the funnel from "researched many" to "tested few" with explicit reasoning, instead of just announcing winners.

## The funnel

| Stage | Count | Source |
|---|---|---|
| Tools researched (across the 4 categories) | **24** | `01_doc_ai_apis.md` (3) + `02_llm_vision.md` (3) + `03_specialized_saas.md` (9) + `04_oss.md` (8 incl. pdfplumber) + LlamaParse cross-listed |
| Surviving to Epic 5 hands-on | **2** | This file |
| In addition to: brief-listed tools we hands-on (Power Automate, ChatGPT, Claude, Tabula, n8n, NotebookLM) | 6 | Epic 5 |
| **Total Epic 5 hands-on count** | **≥ 6 (probably 7 with the OSS option)** | |

## Finalist 1 — Azure Document Intelligence

**Selected for**: Epic 5.7 hands-on as **(a) the unlisted-tool differential** and **(b) the cross-validation pair for Power Automate (5.2)**.

### Why this and not the alternatives in its category
| Alternative | Why not selected |
|---|---|
| AWS Textract | Functionally similar to Azure DI; testing both is redundant. Picked the one that cross-validates the chosen primary (same engine = AI Builder). |
| Google Document AI | Same redundancy + partial BR-region coverage at the time of this writing. |

### Why this and not LLM APIs / SaaS / OSS
- **LLM APIs (Claude, GPT-5, Gemini)**: Claude API IS hands-on tested in 5.4 — that covers the LLM-API category. Adding more would be redundant.
- **Specialized SaaS (Reducto, Extend, Nanonets, etc.)**: none beats Azure DI's specific position as our cross-validation engine. Nanonets gets a name-check in the relatório as an SMB alternative.
- **OSS (Docling, Marker)**: covered by Finalist 2.

### Expected outcome
- ≥ 90% field accuracy on the example PDF (matching Power Automate 5.2 within ±5 points)
- Cost ~$0.05 per PDF custom (~$500 for 10k batch)
- BR South region confirmed
- If 5.2 and 5.7 scores diverge by >5 points → investigate (likely AI Builder applies post-processing the raw API doesn't)

## Finalist 2 — Docling (or Marker, decided at run-time)

**Selected for**: Epic 5.9 *optional* hands-on as the **fully-local LGPD-strict alternative**.

### Why this and not the alternatives in its category
| Alternative | Why not selected |
|---|---|
| Marker | Closely tied — pick at run-time based on which produces better output on `exemplo_pdf_cliente_devedor_ficticio.pdf`. The 5.9 task allows "Docling OR Marker" |
| Unstructured.io | Lower output polish for our use case |
| LlamaParse | Cloud API, defeats the "local" purpose |
| Surya / PaddleOCR / Tesseract | OCR primitives without layout extraction; would need to be paired with another tool for full pipeline. Less self-contained as a hands-on demo. |

### Why we even include an OSS hands-on
- **The relatório needs a credible LGPD-strict path.** A firm that rejects all cloud Doc AI deserves a real recommendation, not just "go OSS." We test one to make it real.
- **The video benefits.** Showing extraction running on the operator's laptop with no network is a strong visual against the cloud-only narrative.
- **Insurance.** If both Power Automate (5.2) and Azure DI (5.7) underperform on a synthetic adversarial PDF for unknown reasons, Docling is the on-prem failover we can recommend.

### Expected outcome
- 70–85% field accuracy (lower than cloud Document AI; that's expected)
- Latency ~2–5 sec per PDF on M-series Mac CPU
- Zero per-page cost; one-time install effort
- Confirms the "always-an-OSS-path" claim in the relatório

## What about ChatGPT, Claude, Gemini API direct?

The brief-listed product (ChatGPT) is hands-on tested in 5.3 — that covers the OpenAI category at a layer the firm would actually use. Claude API is hands-on tested in 5.4 — covers Anthropic. Gemini is documented in `02_llm_vision.md` as an equivalent alternative; no separate hands-on planned because it adds redundancy without changing the architecture.

## What about specialized SaaS?

Documented in `03_specialized_saas.md` (9 tools). **Nanonets** and **Extend** explicitly named in the relatório §6 as SMB alternatives the firm can evaluate later if Microsoft stack is rejected. No hands-on planned in Epic 5 — would dilute focus without informing the architecture decision.

## What this file enables in the relatório

When the relatório §1 lists "Ferramentas testadas" the hirer sees:
- 6 brief-listed tools tested hands-on (Power Automate, ChatGPT, Claude, Tabula, n8n, NotebookLM)
- 1 unlisted Document AI tested hands-on (Azure DI, with cross-validation rationale)
- 1 unlisted OSS tested hands-on (Docling/Marker)
- **20+ tools researched and explicitly excluded with named rationale** (this file + the four category files)

That is a defensible "we ran a real research sprint" narrative, not a token survey.
