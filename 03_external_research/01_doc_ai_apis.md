# External Research — Document AI APIs

> Cloud document understanding services. Each provides OCR + layout + custom-extraction-model-per-document-type at API-as-a-service scale. The category that includes the engine behind our chosen primary (AI Builder = Azure Document Intelligence under the hood, per `decisions.md` D-005).

> **Verdict ahead of detail**: Azure Document Intelligence advances to Epic 5.7 hands-on (cross-validation pair with Power Automate 5.2). AWS Textract and Google Document AI are documented for completeness and as alternatives if firm later moves off Microsoft.

## 1. Azure Document Intelligence (formerly Form Recognizer)

| Aspect | Detail |
|---|---|
| Vendor | Microsoft Azure |
| Models offered | Layout, Read, GeneralDocument, prebuilt (invoice, receipt, ID, business card, contract, US/IN/UK tax forms, healthcare insurance card), Custom Extraction (template + neural), Custom Classification |
| Custom model training UI | Document Intelligence Studio — point-click; ~5 sample docs needed for neural custom |
| Pricing | Custom extraction: ~$50 per 1k pages (S0 tier). Prebuilt: $10–25 per 1k pages depending on model |
| **Per-PDF cost (2 pages)** | **~$0.05 custom · ~$0.02 prebuilt** |
| **10k batch cost** | **~$500 custom · ~$200 prebuilt** |
| Brazil region | ✅ **Brazil South** (São Paulo) — full Document Intelligence availability |
| LGPD posture | 4/5 — BR region + DPA + zero-retention via "isolated processing" tier |
| Output | Structured JSON with bounding boxes + confidence scores per field |
| Why we hands-on test it | (a) **Cross-validates Power Automate 5.2** — same engine, different SKU. (b) Independent unlisted-tool differential per brief. (c) BR region available. (d) Confidence scores per-field map cleanly to our HITL design. |

## 2. AWS Textract

| Aspect | Detail |
|---|---|
| Vendor | Amazon Web Services |
| Models offered | Detect Document Text, Analyze Document (forms + tables), Analyze Expense (receipts/invoices), Analyze ID, Analyze Lending (mortgage docs), Queries (LLM-style "extract field X" without training) |
| Custom model training | Limited — relies on prebuilt + Queries mode; for true custom forms use AWS Comprehend Custom or Bedrock |
| Pricing | Detect Text: $1.50 per 1k pages. Analyze Document: $50 per 1k pages. Queries: $15 per 1k pages |
| **Per-PDF cost (2 pages)** | **~$0.10 Analyze · ~$0.03 Queries** |
| **10k batch cost** | **~$1000 Analyze · ~$300 Queries** |
| Brazil region | ✅ **South America (São Paulo) sa-east-1** — Textract available |
| LGPD posture | 4/5 — BR region + DPA |
| Output | JSON with blocks, key-value pairs, tables; can reach into Lambda for pipelines |
| Why we don't hands-on test | Functionally similar to Azure DI; testing both would be redundant. We pick Azure DI because (a) it's the engine behind our chosen primary (cross-validation), and (b) Azure DI's neural custom-extraction outscores Textract Queries on highly-templated documents per published benchmarks. |

## 3. Google Document AI

| Aspect | Detail |
|---|---|
| Vendor | Google Cloud |
| Models offered | Form Parser, OCR, Specialized parsers (invoice, receipt, contract, paystub, bank statement, etc.), Custom Document Extractor (CDE), Custom Document Classifier, Workbench for HITL |
| Custom model training | Workbench — strong UI for labeling + training + reviewing |
| Pricing | Form Parser: $30 per 1k pages. CDE: $30–65 per 1k pages depending on volume. Specialized parsers: $5–10 per 1k pages |
| **Per-PDF cost (2 pages)** | **~$0.06 CDE · ~$0.01 specialized** |
| **10k batch cost** | **~$600 CDE · ~$100 specialized** |
| Brazil region | ⚠️ **southamerica-east1 (São Paulo)** — partial Document AI availability; verify CDE specifically before commit |
| LGPD posture | 3–4/5 — BR region available for some processors; verify per-processor before commit |
| Output | JSON with entities, page anchors, confidence; integrated with BigQuery + Vertex AI |
| Why we don't hands-on test | Excellent product but redundant with Azure DI for our purposes; we focus the hands-on budget on the engine that cross-validates the chosen primary. Documented here as the right alternative if firm is on GCP rather than Azure/M365. |

## Side-by-side summary

| Capability | Azure DI | AWS Textract | Google Doc AI |
|---|---|---|---|
| BR region full availability | ✅ Brazil South | ✅ sa-east-1 | ⚠️ partial (southamerica-east1) |
| Strong custom-extraction training UI | ✅ Studio | ⚠️ via Comprehend | ✅ Workbench |
| Confidence scores per field | ✅ | ✅ | ✅ |
| Cost class (10k batch, custom) | 💲💲 (~$500) | 💲💲💲 (~$1000) | 💲💲 (~$600) |
| Selected for hands-on (Epic 5.7) | ✅ | ❌ | ❌ |
| Why others not selected | Picked the engine that cross-validates Power Automate (same vendor) | Redundant + higher cost | Redundant + partial BR coverage |

## Sources / verification notes

Pricing pulled from each vendor's public pricing pages. Treat as **order of magnitude** — verify exact pricing tier with sales for production commit. Hands-on Epic 5.7 will produce the actual measured cost-per-PDF that replaces the estimate column above.

## Position in the comparison matrix
- **Azure Document Intelligence** is documented as the unlisted-tool differential AND the cross-validation pair for Power Automate (5.2 ↔ 5.7). See `02_tool_universe/comparison_matrix.md`.
- AWS Textract + Google Document AI are documented here as alternatives but not benchmarked.
