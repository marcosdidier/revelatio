# External Research — Open-Source / Local Document Extraction

> Tools that run on the firm's own machine — strongest possible LGPD posture (data never leaves the network). Critical fallback category if firm later rejects all cloud Document AI for compliance reasons.

> **Verdict ahead of detail**: Docling (or Marker) advances to Epic 5.9 as the optional OSS hands-on. pdfplumber is already in the chosen architecture as the page-1 deterministic parser.

## 1. Docling (IBM Research, MIT-licensed)

What: PDF / DOCX / PPTX → structured JSON + Markdown converter. Released 2024 by IBM Research. Strong on tables and reading order; built around the DocLayNet model trained on 80k pages of varied document types.
- Install: `pip install docling`
- Hardware: CPU-only works; GPU helps for batch
- BR-language: ✅ multilingual model (PT included)
- License: MIT
- Output: structured JSON with bboxes, tables as cell matrices, MD export
- **Verdict**: ✅ **strongest OSS candidate for Epic 5.9 hands-on**; best documented; backed by IBM = long-term confidence

## 2. Marker

What: PDF → Markdown via small vision-LLM models (LayoutLM, MathPix-style). Optimized for academic papers but works on any layout.
- Install: `pip install marker-pdf`
- Hardware: requires GPU for reasonable speed (M-series Mac MPS works)
- BR-language: ✅ via OCR backbone
- License: GPL-3 (verify if firm tolerates GPL — usually yes for internal tools)
- Output: Markdown + image extraction
- **Verdict**: ✅ alternative to Docling; pick based on which produces better output on `exemplo_pdf_cliente_devedor_ficticio.pdf` in 5.9

## 3. Unstructured.io (open-source library)

What: Document partitioning library (the OSS half — there's also a commercial API). Splits PDFs/DOCs into structured chunks.
- Install: `pip install unstructured`
- Hardware: CPU works
- BR-language: ✅ via OCR backends (Tesseract or PaddleOCR)
- License: Apache 2 (OSS); commercial API has separate terms
- Output: List of `Element` objects (Title, NarrativeText, Table, Image)
- **Verdict**: ⚠️ solid utility library; less polished output than Docling for our use case

## 4. LlamaParse (LlamaIndex)

What: Premium parser inside LlamaIndex; vision-LLM-driven; handles complex layouts.
- Install: `pip install llama-parse` + API key (note: LlamaParse itself is **API-based**, not local — listed here for category completeness; for fully local use Marker or Docling)
- Hardware: API call (cloud)
- BR-language: ✅
- License: free tier (~7k pages/day) + paid
- Output: Markdown + JSON
- **Verdict**: ⚠️ excellent quality but defeats the "local" purpose; same compliance concerns as cloud APIs

## 5. Surya OCR

What: Multilingual OCR from VikParuchuri (same author as Marker). **Explicit Portuguese support and tuning.**
- Install: `pip install surya-ocr`
- Hardware: GPU helpful; CPU works for small batches
- BR-language: ✅ explicit PT-BR tuning
- License: GPL-3 base model + commercial license available for closed-source production
- Output: bounding boxes + text per region + reading order
- **Verdict**: ✅ best **OCR primitive** for PT-BR; pair with a layout/extraction layer (Docling, Unstructured) for full pipeline

## 6. PaddleOCR (Baidu, Apache 2)

What: Industrial-strength OCR with strong multilingual support including Portuguese.
- Install: `pip install paddleocr`
- Hardware: CPU works; GPU faster
- BR-language: ✅ PT model (`pt`)
- License: Apache 2
- Output: bboxes + text + confidence
- **Verdict**: ✅ great free alternative to Surya; well-maintained, pre-PaddleOCR's reputation in Chinese OCR translates to robust Latin-alphabet support

## 7. Tesseract (Apache 2)

What: The veteran OCR engine. 35+ years old, Google-stewarded since 2006.
- Install: `brew install tesseract` + Portuguese language pack
- Hardware: CPU only
- BR-language: ✅ via `tesseract -l por`
- License: Apache 2
- Output: text + bboxes (TSV mode)
- **Verdict**: ⚠️ excellent baseline; outclassed by Surya / PaddleOCR on accuracy but unmatched on portability

## 8. pdfplumber (already in our architecture)

What: Python library for PDF text + table extraction from text-based PDFs (no OCR).
- Install: `pip install pdfplumber`
- Hardware: CPU only
- BR-language: irrelevant (text layer pass-through; no OCR)
- License: MIT
- Output: text, tables (list of cells), bboxes
- **Verdict**: ✅✅ **already chosen** as the page-1 parser in Epic 6 reference script

## Side-by-side summary

| Tool | Local? | PT-BR | License | Where used | Verdict |
|---|---|---|---|---|---|
| **Docling** | ✅ | ✅ | MIT | Epic 5.9 hands-on candidate | ✅ |
| Marker | ✅ | ✅ | GPL-3 | Epic 5.9 alternative | ✅ |
| Unstructured | ✅ | via OCR | Apache 2 | utility lib | ⚠️ |
| LlamaParse | ❌ (cloud API) | ✅ | freemium | not local; in LLM category | ⚠️ |
| Surya | ✅ | ✅✅ tuned | GPL-3/comm | OCR primitive | ✅ |
| PaddleOCR | ✅ | ✅ | Apache 2 | OCR primitive alt | ✅ |
| Tesseract | ✅ | ✅ | Apache 2 | baseline OCR | ⚠️ baseline |
| **pdfplumber** | ✅ | n/a | MIT | **chosen page-1 parser** (Epic 6) | ✅✅ |

## When OSS-local wins

- **LGPD-strict firms** (or sectors: healthcare, finance, public sector). The "data never leaves the network" claim is binary.
- **Cost-conscious, technical-team firms.** Zero per-page cost; only hosting + dev time.
- **Air-gapped deployments** (rare in law but exists in defense/intelligence).

## When OSS-local loses

- **No engineering capacity to maintain.** Self-hosted = self-supported. Power Automate's "Microsoft fixes the bugs" matters for non-eng teams.
- **Extraction accuracy ceiling lower** for complex multi-template extraction. Cloud Document AI APIs invest billions in model quality OSS can't match.

## Position in the comparison matrix

- **pdfplumber**: ✅ chosen page-1 parser in Epic 6 reference script.
- **Docling or Marker**: optional OSS hands-on in Epic 5.9 — produces a "fully-local fallback" data point in the relatório for LGPD-strict scenarios.
- **Surya / PaddleOCR**: documented as OCR primitives for the alternative-flow architecture (`07_recommendation/alt_flow_n8n.md`) when paired with Docling for layout.
