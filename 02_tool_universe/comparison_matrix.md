# Comparison Matrix — 8 brief-listed tools

> **Why this exists**: a hiring manager will spend ~30 seconds on this table. It's the executive summary of `02_tool_universe/` — every cell is backed by the per-tool dossier. The "Score" column is filled in Epic 5.10 after benchmarks.

> **Reading order**: tools are grouped by role, with the **chosen primary solution (D-005) at the top of the extractor group**. Within each group, ranked by overall recommendation for this firm's context.

## Headline matrix

### Group 1 — Extractor candidates (the core decision)

| # | Tool | Hands-on test | LGPD posture (1-5) | Cost class | Score | Fit verdict | One-liner |
|---|---|---|---|---|---|---|---|
| **1** ⭐ | **Power Automate + AI Builder** | ✅ **Epic 5.2 (chosen primary)** | 4 (M365 BR) | 💲💲💲 | TBD from 5.2 | **✅ CHOSEN (D-005)** | Brief-listed; M365-native; Excel out-of-the-box; AI Builder = Azure DI under the hood (cross-validated in 5.7) |
| 2 | **Claude (via Bedrock SA-East-1 or API)** | ✅ Epic 5.4 | 4 (BR-region cloud) | 💲💲 (Sonnet) | TBD | ✅ Strong **alternative** (non-M365 firms) | Native PDF + vision + structured output + BR region |
| 3 | **ChatGPT (Enterprise / Azure OpenAI)** | ✅ Epic 5.3 | 3 (US cloud, opt-out) | 💲💲 | TBD | ⚠️ Conditional alternative | Strong but Plus tier inappropriate at scale |
| 4 | **Tabula** | ✅ Epic 5.5 | 5 (local) | 💲 free | TBD | ⚠️ Useful as page-1 baseline only | No OCR; insufficient alone but free |

### Group 2 — Orchestrator candidates

| # | Tool | Hands-on test | LGPD posture | Cost class | Fit verdict | One-liner |
|---|---|---|---|---|---|---|
| 1 | **Power Automate** (covered above) | ✅ Epic 5.2 | 4 (M365 BR) | 💲💲💲 | ✅ Chosen if firm on M365 | End-to-end inside the chosen primary solution |
| 2 | **n8n (self-hosted)** | ✅ Epic 5.6 | 5 (self-host) | 💲 | ✅ Recommended for **alternative flow** (Diff:AltFlow) | Best LGPD posture; primary orchestrator if firm not on M365 |
| 3 | **Make** | ❌ redundant w/ n8n | 2 (EU/US cloud) | 💲 | ⚠️ Conditional | Equivalent capability to n8n but no self-host option |

### Group 3 — Downstream consumers (natural-language analytics over the resulting spreadsheet)

| # | Tool | Hands-on test | LGPD posture | Cost class | Fit verdict | One-liner |
|---|---|---|---|---|---|---|
| 1 | **Microsoft Copilot (in Excel/M365)** | ❌ analytical only | 4 (M365 BR) | 💲💲 | ✅ Recommended as M365 add-on | Pairs with Power Automate; natural-language Q&A on the output |
| 2 | **NotebookLM** | ⚠️ Epic 5.8 (misfit demo) | 4 (Workspace BR) | 💲 (existing seat) | ✅ Alternative consumer if firm on Google Workspace | Wrong layer for extraction; great for post-pipeline Q&A |

### Cross-validation pair (architecturally important)

| Pair | What it validates | Where |
|---|---|---|
| **Power Automate (5.2) ↔ Azure Document Intelligence (5.7)** | AI Builder Document Processing runs on the Azure DI engine. Two independent hands-on tests of the same extraction layer = redundant evidence for the accuracy claim. Expected score divergence < 5 points. | Epic 5.10 Score consolidation explicitly checks this. |

## LGPD posture scale
- **5** Self-hosted on firm's network (best)
- **4** Hosted in BR-region cloud (M365 BR, Bedrock SA-East-1, Azure BR South, GCP southamerica-east1, Workspace BR)
- **3** US/EU cloud with zero-retention/DPA
- **2** Cloud, no opt-out / training on data
- **1** No DPA available (consumer-tier free)

## Cost class
- 💲 ≤ $50 / 10k batch (or free)
- 💲💲 $50–500 / 10k batch
- 💲💲💲 > $500 / 10k batch (but typically lowest **TCO** when bundled with already-paid licenses)

## The recommendation, in one sentence

> **For a firm already on M365: Power Automate + AI Builder is the chosen primary solution; the legal team gets a flow they can maintain themselves, native Excel output, BR-region LGPD posture, and a Copilot-in-Excel layer for analytics. For a firm not on M365: n8n self-hosted + Claude (Bedrock SA-East-1) is the alternative flow with stronger pure-LGPD posture and lower license bundling.**

## Quick takeaways for the relatório

1. **No single brief-listed tool wins all roles.** The right answer is a **composition**: a Doc-AI extractor + an orchestrator + a downstream consumer. The brief's tool list spans these roles deliberately.
2. **Power Automate is the chosen primary** because it delivers all three roles in one platform aligned with the firm's likely existing M365 stack — and our hands-on validation is reinforced by an independent test of the same underlying engine (Azure DI in 5.7).
3. **Strongest pure LGPD posture**: Tabula (page-1 only) and n8n self-hosted (orchestrator). They cover layer 1 and orchestration but neither does layer 2 OCR. That's why an alternative-flow firm pairs n8n with Claude on Bedrock SA-East-1 or with a local OSS extractor (Docling/Marker — see Epic 3).
4. **One tool we deliberately don't hands-on-test**: Make (functionally redundant with n8n hands-on in 5.6). Microsoft Copilot also no hands-on, but as a downstream consumer rather than extractor — analytical coverage suffices.
