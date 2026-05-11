# Dossier — Make (formerly Integromat)

> Brief-listed tool · **Not testing hands-on** — see "Why not testing" below. Functionally redundant with n8n (Epic 5.5).

## What it is
Cloud workflow automation platform (Zapier-class) with 1500+ integrations and a visual no-code editor. Has built-in modules for OpenAI / Anthropic / OCR / Google Sheets / etc.

## Where it fits in our pipeline
- **Extractor**: no — it doesn't extract; it *calls* extractors via integration modules.
- **Orchestrator**: ✅ yes — could be the workflow that watches a Drive folder, calls an LLM/Doc-AI module per PDF, writes rows to Sheets, alerts via Slack on errors.
- **Why we're testing n8n instead**: n8n covers the same orchestrator role hands-on (5.5), is **self-hostable** (huge LGPD win), and is open-source. A single hands-on orchestrator test is enough to defend either choice; we don't need both.

## Why not testing hands-on
1. **Functional redundancy**: any workflow we build in Make we could build identically in n8n in ~the same time.
2. **LGPD posture**: Make is cloud-only — every PDF flows through Make's servers. n8n self-hosted keeps PDFs on the firm's network. For debtor data, that's the more defensible choice.
3. **Brief alignment**: the brief says "Make / n8n" together, treating them as alternatives. We pick one for hands-on (n8n), reason about the other (this dossier).

## LGPD / data-residency
- Cloud-only; servers in EU and US (no Brazil region currently).
- Has SOC 2 Type II; offers DPA for GDPR; can be configured to comply with LGPD with the right safeguards (e.g., redact CPF before sending to external modules).
- For a law firm processing 10k debtor PDFs: feasible but adds a vendor and a data-flow leg outside Brazil. n8n self-hosted avoids this entirely.

## Cost class
- Free tier: 1k operations/mo (10k PDFs × ~5 ops each = 50k ops → not on free tier)
- Core tier: $9/mo for 10k ops
- Pro: $16/mo for 10k ops with more features
- For 50k ops/batch: ~$30–50/mo
- 💲

## Fit verdict
**⚠️ Conditional** — viable orchestrator IF the firm prefers a managed product over self-hosting and is comfortable with EU/US data flows for tokenized payloads. Otherwise n8n self-hosted is the better pick. Recommended position in the relatório: *"Make seria uma alternativa equivalente ao n8n em capabilities, com vantagem de gestão menor e desvantagem de não permitir self-host (LGPD)."*

## What would change our verdict
- Make adds a Brazil region → posture improves
- Firm has zero-ops capacity and prefers vendor-managed
