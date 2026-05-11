# External Research — LLM-with-Vision API options

> Direct API use of multimodal frontier models, as distinct from their wrapped consumer chat products in Epic 2 (ChatGPT, Claude). Different evaluation lens because at the API layer we get: structured output enforcement, zero data retention contractually, regional hosting choices, and per-PDF cost predictability.

> **Verdict ahead of detail**: Claude API via Bedrock SA-East-1 advances to Epic 5.4 hands-on as the strongest LLM alternative if firm is not on M365. GPT-5 (via Azure OpenAI) and Gemini are documented as comparable alternatives.

## 1. Anthropic Claude API (current generation: Opus 4.7, Sonnet 4.6, Haiku 4.5)

| Aspect | Detail |
|---|---|
| PDF support | **Native** — `document` content block in API; up to 100 pages per request; preserves layout and embedded images |
| Vision | Built into all Claude 4.x models |
| Structured output | Via tool-use forcing a JSON schema; enforced output |
| Cost (Sonnet 4.6) | $3 / $15 per 1M input/output tokens |
| **Per-PDF cost** | **~$0.03 (Sonnet) · ~$0.003 (Haiku) · ~$0.15 (Opus)** |
| **10k batch (Sonnet)** | **~$300** |
| Hosting / region | Anthropic direct (US) · **AWS Bedrock SA-East-1** ✅ Brazil region · GCP Vertex AI |
| LGPD posture | 3–4/5 — Bedrock SA-East-1 elevates to 4. Zero-retention contractually (sign DPA). |
| Why we hands-on test it (Epic 5.4) | Strongest LLM-based extractor with native PDF + BR region option; serves as the **alternative-flow primary extractor** for non-M365 firms. |

## 2. OpenAI GPT-5 (via Responses API or Azure OpenAI)

| Aspect | Detail |
|---|---|
| PDF support | **Via file uploads + Code Interpreter (Responses API)**; vision native for images. PDF needs preprocessing in some setups. |
| Vision | Built in |
| Structured output | `response_format` with JSON schema enforcement; stable |
| Cost (GPT-5) | ~$1.25 / $10 per 1M input/output tokens |
| **Per-PDF cost (2 pages)** | **~$0.01–0.02** |
| **10k batch** | **~$100–200** |
| Hosting / region | OpenAI direct (US) · **Azure OpenAI** with regional control (Brazil South via Azure subscription that enables it; verify availability of GPT-5 specifically per region) |
| LGPD posture | 3/5 direct · 4/5 via Azure OpenAI with BR region + zero-retention |
| Why we don't hands-on test the API directly | We do hands-on the **product** (ChatGPT) in Epic 5.3 — that test informs the API story. Adding a separate API hands-on would be redundant given Claude API is our chosen LLM-API hands-on (5.4). |

## 3. Google Gemini API (current generation: Gemini 2.5 Pro, Gemini 2.5 Flash)

| Aspect | Detail |
|---|---|
| PDF support | **Native** — files API + 1M-token context allows ingesting full multi-page PDFs in a single request |
| Vision | Built in (multimodal natively) |
| Structured output | `responseSchema` field — JSON schema enforcement |
| Cost (Flash) | ~$0.30 / $2.50 per 1M input/output tokens |
| **Per-PDF cost** | **~$0.003 (Flash) · ~$0.05 (Pro)** |
| **10k batch (Flash)** | **~$30** |
| Hosting / region | Google AI Studio (consumer) · Vertex AI (enterprise) — **southamerica-east1 (São Paulo)** for some Gemini variants |
| LGPD posture | 3–4/5 via Vertex AI with BR region + DPA |
| Why we don't hands-on test | Excellent product, especially Gemini 2.5 Flash on price. Documented here for completeness; not selected because Claude API better fits our chosen-primary cross-validation story (Anthropic on Bedrock keeps us in the "BR region + zero-retention" pattern Power Automate already establishes, simplifying the relatório's compliance narrative). |

## Side-by-side summary

| Capability | Claude API | GPT-5 / Azure OpenAI | Gemini API |
|---|---|---|---|
| Native PDF ingestion | ✅ document block | ⚠️ via file uploads / preprocessing | ✅ native |
| Brazil region | ✅ Bedrock SA-East-1 | ✅ Azure OpenAI BR South (verify GPT-5 availability) | ✅ Vertex SA-East-1 (verify Gemini availability) |
| Structured-output mode | ✅ tool use | ✅ response_format | ✅ responseSchema |
| Cost class (10k batch, mid-tier model) | 💲💲 (~$300 Sonnet) | 💲💲 (~$100–200 GPT-5) | 💲 (~$30 Flash) |
| Selected for hands-on | ✅ Epic 5.4 | ❌ (covered via product test 5.3) | ❌ |

## When to prefer LLM APIs over Document AI APIs

- **Variable / unpredictable document templates** — LLMs handle "we've never seen this layout" better than custom-extraction models that require retraining
- **Light document volume** (< 1000/mo) — fixed Document AI training cost not amortized
- **Conversational extraction** ("extract every field that mentions a date") rather than schema-driven
- **Migration windows** — LLM as the bridge while training a Document AI custom model

## When NOT to prefer LLM APIs

- **Hallucination risk** on missing fields. Document AI APIs return confidence scores; LLMs invent confidently. Mitigation: rubric's hallucination penalty + confidence-floor + cross-validation.
- **Large-scale fixed-template extraction** — Document AI custom-extraction-model is more accurate AND cheaper per page once trained.
- **Audit-rigor requirements** — Document AI confidence scores are more directly defensible than LLM "I'm pretty sure."

## Position in the comparison matrix
- **Claude API via Bedrock SA-East-1** is the **alternative-flow primary extractor** for non-M365 firms. See `02_tool_universe/05_n8n.md` for orchestrator pairing.
