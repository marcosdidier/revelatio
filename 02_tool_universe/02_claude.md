# Dossier — Claude

> Brief-listed tool · Will test hands-on in **Epic 5.3** (web upload **and** API).

## What it is
Anthropic's flagship chatbot + API. Current models: **Opus 4.7** (highest reasoning), **Sonnet 4.6** (balanced), **Haiku 4.5** (fast/cheap). Native PDF support up to 100 pages; vision built in; structured output via tool-use forcing a JSON schema; available via Anthropic API direct, AWS Bedrock, and GCP Vertex AI.

## Where it fits in our pipeline
- **Extractor candidate**: yes, both pages — vision handles the comprovantes, native PDF handles the text layer in one pass.
- **Orchestrator**: no.
- **Downstream consumer**: yes — Projects on claude.ai with the spreadsheet attached.

## Hands-on plan (Epic 5.3)
1. **Web (claude.ai)**: upload PDF → prompt with explicit JSON schema → record response.
2. **API (Python SDK)**:
   ```python
   import anthropic
   client = anthropic.Anthropic()
   r = client.messages.create(
       model="claude-opus-4-7",
       max_tokens=4096,
       messages=[{
           "role": "user",
           "content": [
               {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64_pdf}},
               {"type": "text", "text": "Extract per the schema: {...}. Return only JSON."}
           ]
       }]
   )
   ```
3. Compare web vs API output quality, latency, and cost.

## LGPD / data-residency
- **Pro / Team / Enterprise**: zero retention by default; not used for training. Hosted in US.
- **API direct**: zero retention available; sign DPA.
- **Bedrock SA-East-1 (São Paulo)** ✅ — hosts Claude 4 family in **Brazilian data center** → strongest LGPD posture among hosted LLMs in this dossier set.
- **Vertex AI**: Claude available in `us-central1` and others; check current regions for BR availability.

## Cost class
- API direct (Opus 4.7): ~$15 per 1M input, ~$75 per 1M output. A 2-page PDF as document ≈ 10k input tokens → **~$0.15 per PDF on Opus**.
- API direct (Sonnet 4.6): ~$3 / $15 per 1M → **~$0.03 per PDF**.
- API direct (Haiku 4.5): ~$0.25 / $1.25 per 1M → **~$0.003 per PDF**.
- For 10k PDFs: Opus = ~$1500, Sonnet = ~$300, Haiku = ~$30.
- 💲💲 on Sonnet, 💲 on Haiku

## Fit verdict
**✅ Strong candidate** — especially **via Bedrock SA-East-1** for LGPD compliance. Recommend testing **Sonnet 4.6** as the production tier (best cost/accuracy tradeoff for structured extraction) and **Haiku 4.5** as the fast/cheap baseline. Native PDF support is a meaningful win vs services that need separate OCR + LLM steps.

## Risks specific to this tool
- 100-page PDF limit — fine for 2-page dossiers, watch for multi-attachment cases
- Tool-use schema enforcement is good but not perfect — still validate with pydantic downstream
- Bedrock requires AWS account + IAM setup; trade simplicity of direct API for residency
