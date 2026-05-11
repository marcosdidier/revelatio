# External Research — Specialized Document Extraction SaaS

> Vertical document-extraction products with point-click UIs, often easier for non-technical teams to operate than raw APIs. Many overlap with the Document AI APIs (Epic 3.1) but with thicker UX and pre-built workflows for specific document types.

> **Verdict ahead of detail**: none of these advance to Epic 5 hands-on — Power Automate (chosen primary) and Azure DI (cross-validator) cover the extraction layer. These are documented as alternatives a non-engineering legal-ops team might prefer if Microsoft stack is unavailable.

## 1. Reducto

What: Premium document extraction API + UI. Strong on accuracy benchmarks; markets aggressively to engineers building agents. Recently expanded prebuilt schemas. Founded ~2024.
- Strengths: highest published benchmarks on table extraction, dense forms; nice JSON schema enforcement
- BR-language: PT supported via OCR; verify quality on Brazilian-Portuguese receipts
- Pricing: per-page tiered, ~$0.05–0.10 per page on standard tiers
- Legal-team UI: developer-first; not designed for non-technical operation
- **Verdict**: ⚠️ overkill for fixed-template debtor PDFs; better for agent/RAG pipelines

## 2. Extend

What: Document extraction platform with point-click custom-model training and a strong reviewer UI. Targets ops teams. Founded ~2023.
- Strengths: review queue, audit log, side-by-side correction UI
- BR-language: PT supported
- Pricing: contact sales; reportedly ~$0.05/page mid-tier
- Legal-team UI: ✅ designed for non-technical reviewers
- **Verdict**: ⚠️ good fit if firm rejects Microsoft and wants a managed product over self-hosting

## 3. Nanonets

What: Established (2017) document AI; popular SMB tier; good number of Brazilian customers. Prebuilt + custom models. WhatsApp/email/SharePoint triggers natively.
- Strengths: easy onboarding, nice prebuilt invoice/receipt models, Zapier+Make+n8n connectors
- BR-language: PT supported, has Portuguese OCR tuning
- Pricing: $499/mo Pro tier (~10k pages) — sweet for our 10k batch use case
- Legal-team UI: ✅ explicitly designed for ops users
- **Verdict**: ⚠️ strong dark-horse for non-M365 firms, especially SMB-sized law firms

## 4. Mindee

What: French startup; strong API; popular open-source predecessor (`docTR`) gives them OSS street cred. Prebuilt receipt/invoice/ID models with confidence scores.
- Strengths: clean API, free OSS extractor for prototyping (docTR), GDPR-native (helps LGPD posture)
- BR-language: PT supported via docTR's multilingual OCR
- Pricing: $250/mo for 1k pages → 10k batch ~$2500 (premium)
- Legal-team UI: developer-first product; ops UI exists but secondary
- **Verdict**: ⚠️ stronger as a developer's API than as an ops UI; consider if firm has eng capacity

## 5. Rossum

What: Czech startup; explicit focus on **invoice/receipt/financial-doc extraction with HITL UI**. Used by Pepsi, GoPro, Veolia. Strong reviewer ergonomics.
- Strengths: best-in-class HITL reviewer UI; financial-doc specialization; SAP/SF/QuickBooks connectors
- BR-language: PT supported
- Pricing: enterprise; contact sales (typically $30k+/yr)
- Legal-team UI: ✅✅ exemplary; ops users like it
- **Verdict**: ⚠️ over-built and over-priced for a single-doc-type debtor pipeline; ROI hits at multi-doc-type AP/finance ops

## 6. Klippa

What: Dutch SaaS; strong on receipt/expense capture; APIs + mobile SDKs.
- Strengths: receipt capture optimized; mobile SDKs (less relevant here)
- BR-language: PT supported
- Pricing: per-document tiers; ~$0.10/page
- **Verdict**: ❌ targeted at expense management, not bulk legal extraction

## 7. Affinda

What: Australian; resume parser → expanded into document AI broadly.
- Strengths: well-documented API; reasonable pricing
- BR-language: PT supported
- Pricing: per-credit, ~$0.05/page
- **Verdict**: ❌ niche origin (resume) limits brand fit for legal context

## 8. Parseur

What: Email + document extraction with template UI (point-click). Strong for repetitive emails / invoices.
- Strengths: very easy custom templates; email-trigger native
- BR-language: PT supported
- Pricing: tiered by docs/mo; $99/mo for 1k docs = ~$1000/10k batch
- **Verdict**: ⚠️ good for non-eng teams; better suited to recurring email-based docs than the bank-PDF dump scenario

## 9. Docparser

What: Legacy player (since ~2016); template-based document parsing.
- Strengths: stable, low risk, clear pricing
- BR-language: PT supported
- Pricing: $39–249/mo by volume
- **Verdict**: ⚠️ functional but feels dated next to AI-Builder/Reducto/Extend

## Side-by-side summary

| Tool | Strength | BR-PT | Cost class (10k batch) | Legal-team UX | Verdict |
|---|---|---|---|---|---|
| Reducto | Accuracy on dense forms | ✅ | 💲💲 | dev-first | ⚠️ |
| Extend | Reviewer UI for ops teams | ✅ | 💲💲 | ops-friendly | ⚠️ alt for non-M365 |
| **Nanonets** | SMB sweet spot | ✅ | 💲 (~$500) | ✅ ops-friendly | ⚠️ **strong alt for non-M365 SMB** |
| Mindee | OSS roots, GDPR | ✅ | 💲💲💲 | dev-first | ⚠️ |
| Rossum | Best HITL UI | ✅ | 💲💲💲💲 enterprise | ✅✅ | ⚠️ over-built |
| Klippa | Mobile receipts | ✅ | 💲💲 | ops | ❌ wrong domain |
| Affinda | Doc AI generalist | ✅ | 💲💲 | mixed | ❌ |
| Parseur | Template builder | ✅ | 💲💲 | ✅ ops | ⚠️ |
| Docparser | Stable veteran | ✅ | 💲 | dated | ⚠️ |

## Why none advance to Epic 5 hands-on

The chosen primary (Power Automate via D-005) covers extraction; Azure DI covers cross-validation; Claude API covers the LLM alternative. Adding a specialized SaaS hands-on would dilute focus without changing the recommendation. **However**, in the relatório §6 we explicitly mention **Nanonets** and **Extend** as named non-M365 SMB alternatives the firm can evaluate later, so the hirer sees we explored beyond the obvious.
