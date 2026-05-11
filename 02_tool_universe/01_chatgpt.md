# Dossier — ChatGPT

> Brief-listed tool · Will test hands-on in **Epic 5.2**.

## What it is
OpenAI's flagship consumer/business chatbot, currently with **GPT-5** as the default model. Supports native PDF upload and vision; can return JSON via response-format constraints (in API and via prompt in chat). Available tiers: Free, Plus, Team, Enterprise, plus the developer API.

## Where it fits in our pipeline
- **Extractor candidate**: yes, for both pages (text + image). Vision handles page 2 OCR; text extraction handles page 1.
- **Orchestrator**: no — it's a model behind a chat UI / API, not a workflow engine.
- **Downstream consumer**: yes — once the spreadsheet exists, the legal team could ask "ChatGPT, summarize all debtors over 90 days with status 'Em negociação'" via a Custom GPT pointed at the file.

## Hands-on plan (Epic 5.2)
1. Plus tier (web): upload `exemplo_pdf_cliente_devedor_ficticio.pdf` → prompt: *"Extract every field from this PDF as a JSON object matching this schema: [paste from `gold_truth.json` keys]. Return ONLY valid JSON. If a field is not present, return null — do not invent values."*
2. Run on 4 random synthetic PDFs (after Epic 4) for accuracy + latency averages.
3. Capture: raw output, screenshot, hallucination count, time-to-completion, refusals (some tiers refuse documents containing CPF/PII).

## LGPD / data-residency
- **Free / Plus**: data may be used to train models unless opted-out via Settings → Data Controls. Servers primarily US-based.
- **Team / Enterprise**: zero data retention by default; SOC 2 Type II; data not used for training. Still US-hosted.
- **API**: zero retention available; can sign DPA. Can use Azure-hosted OpenAI (GPT-5) for tenant data residency including BR-region option indirectly.
- **Verdict for 10k debtor PDFs**: Plus tier is **inappropriate** for this volume + sensitivity. Enterprise or Azure-hosted GPT-5 is acceptable.

## Cost class
- Plus: $20/user/mo flat — but rate-limited; not viable for 10k batch.
- API (GPT-5 with vision): roughly $1.25 per 1M input tokens, $10 per 1M output. A 2-page PDF ≈ 5–10k input tokens → **~$0.01–0.02 per PDF** → **$100–200 for the full 10k batch**. Order of magnitude.
- 💲💲 (LLM API tier)

## Fit verdict
**⚠️ Conditional** — strong as an Enterprise/API extractor; **inappropriate** via consumer Plus account due to LGPD + cost-per-call at scale. Recommend it as the *fallback extractor* if Document AI doesn't beat it on the benchmark, OR as the prototype-fast option before committing to a Doc-AI provider.

## Risks specific to this tool
- Refuses some prompts containing PII ("I can't process documents containing personal data") — handled by phrasing the prompt around "extract structured fields from this fictitious test document"
- Hallucinated CPFs are a real risk; we'll catch them via the rubric's hallucination penalty and via the cross-check pairs (name on page 1 == name on page 2)
- Versioning: GPT-5 behavior changes across model snapshots; pin a specific snapshot in production
