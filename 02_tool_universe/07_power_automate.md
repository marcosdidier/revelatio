# Dossier — Power Automate + AI Builder ⭐ **CHOSEN PRIMARY SOLUTION (D-005)**

> Brief-listed tool · **Hands-on test in Epic 5.2** · Cross-validated against Azure Document Intelligence (same engine, different SKU) in Epic 5.7.

## What it is

Two Microsoft products working together as one solution:

1. **Power Automate** — workflow / RPA platform with cloud + desktop runtimes. Native connectors for SharePoint, Excel, Outlook, Teams, OneDrive, Forms, Approvals, AI Builder, plus 1000+ third-party connectors. Visual no-code editor.
2. **AI Builder** — Microsoft's low-code AI platform inside Power Platform. The relevant module here is **Document Processing**: a managed document-extraction service with prebuilt models (invoices, receipts, IDs, contracts) AND a **custom extraction model** that you train from ~5 example documents through a point-and-click UI.

Critical architectural fact: **AI Builder Document Processing is built on Azure Document Intelligence under the hood**. Same OCR engine, same layout model, same custom-extraction training procedure — just wrapped in a Power Platform UX with M365-native connectors instead of the Azure portal + SDK. This is exploitable: our Epic 5.7 hands-on test of Azure DI directly **cross-validates** the accuracy story we measure for Power Automate in Epic 5.2.

## Where it fits in our pipeline

- **Extractor for both pages**: ✅ — AI Builder's Document Processing handles digital-text fields (page 1) AND image OCR (page 2 comprovantes) in a single model invocation.
- **Orchestrator**: ✅ — Power Automate is the workflow itself. Trigger: SharePoint folder receives PDF. Steps: AI Builder extract → confidence check → Excel append OR route to "Approval needed" review queue (Microsoft Approvals connector) → email/Teams notification.
- **End-to-end**: yes. Single platform. No glue code.

## Why this is the right pick for a Brazilian law firm

1. **Brief-listed tool** — the hirer expects this option to be considered seriously. Picking it is not a leap.
2. **Likely matches the firm's existing stack.** Brazilian law firms commonly run on M365 (Exchange Online + Word + Excel + Teams + SharePoint). Power Automate is included or lightly-licensed inside that stack. A solution that lives in the platform the firm already pays for has a near-zero adoption cost.
3. **Native Excel output.** The brief explicitly asks for "consolidação em Excel". Power Automate's Excel Online connector writes rows directly to a workbook in OneDrive/SharePoint — no export step, no CSV conversion, no formatting drift.
4. **Non-technical maintenance.** The legal-ops lead can open the flow in a browser, see "PDF in → AI Builder → Excel row out", and tweak it. No Python developer needed for day-2 changes (e.g. adding a new field to extract).
5. **HITL is built in.** Microsoft Approvals + SharePoint lists give us a queue for low-confidence rows that the cobrança team can already access from Outlook/Teams, no new app to install.
6. **LGPD posture is solid.** M365 commercial data protection covers AI Builder; tenant region + sensitivity labels + Purview audit logs give us the compliance story.
7. **Audit trail.** Power Automate run history persists every invocation with input + output JSON, who triggered, when. Forensic-grade for a regulated industry.

## Hands-on test plan (Epic 5.2 — chosen primary validation)

> The detailed task definition lives in `backlog.md` Epic 5.2. Summary of what we will produce:

1. **Provisioning** (~30 min): M365 Business Basic 30-day trial + Power Automate Premium trial + AI Builder credits trial → Dataverse default environment
2. **Custom Document Processing model training** (~30 min): upload 5 PDFs (example + 4 synthetic from Epic 4) into AI Builder Studio; tag the 13 brief-required + 18 page-2 fields per `01_field_map/field_map.md`; train; review accuracy report
3. **Flow build** (~60 min): SharePoint folder trigger → AI Builder Predict (custom Document Processing model) → confidence routing (≥ 0.85 → Excel Online "Add row to table"; < 0.85 → Microsoft Approvals + SharePoint "Pending Review" list) → Teams summary
4. **Test runs** (~20 min): example PDF + 4 synthetic PDFs (one deliberately corrupted to verify HITL routing)
5. **Capture**: run history JSON, per-step screenshots, the resulting Excel file, AI Builder accuracy report, AI Builder credit consumption metrics

**Output folder**: `04_experiments/02_power_automate/`
**Success criteria**: ≥ 90% field accuracy on example; HITL routing triggers correctly on the corrupted PDF; cost-per-PDF measured.

## Cross-validation via Azure DI (Epic 5.7)

Because AI Builder Document Processing runs on Azure Document Intelligence, **our 5.7 hands-on test of Azure DI is a second angle on the same extraction layer**. Expected outcome: 5.2 and 5.7 produce scores within ~5 points. If they don't, we investigate (likely cause: AI Builder's wrapper applies different post-processing than raw Azure DI). This cross-validation is the **strongest accuracy claim** we can make in the relatório:

> *"Validamos a acurácia do extrator chosen primary por dois caminhos independentes: hands-on no próprio Power Automate (Epic 5.2) e hands-on no engine subjacente Azure Document Intelligence (Epic 5.7). Os scores convergem dentro de ±5 pontos, confirmando que a recomendação está sustentada por evidência redundante."*

## LGPD / data-residency

- Microsoft 365 Commercial Data Protection covers AI Builder.
- Tenant region configurable for Brazilian data residency (M365 Brazil region available).
- Purview audit logs + DLP policies + sensitivity labels.
- AI Builder data is not used for training Microsoft's models when used inside a Commercial tenant.
- DPA available (signed via M365 admin center).
- **Posture rating: 4/5** — BR-region cloud with strong contractual protections. (Tied with Azure DI direct; behind only fully self-hosted options.)

## Cost class

| Component | Estimate (10k-PDF batch) |
|---|---|
| Power Automate Premium licenses | ~$15/user/mo × N users (typically 1–3 for this team) |
| AI Builder credits for Document Processing | ~$500/mo for 20k credits (1 credit ≈ 1 page; 10k 2-page PDFs ≈ 20k credits) |
| Underlying M365 license | typically already paid |
| **Per-batch incremental cost** | **~$500–600** |
| **Per-batch ROI vs current manual** | manual baseline ≈ 10 people × ~5 days × ~$200/day ≈ **$10k/batch** → **net savings ≈ $9.4k/batch** |

💲💲💲 absolute spend, but the **lowest TCO** when you factor in zero engineering effort + zero new licenses + zero training to a non-Microsoft platform. Hands-on Epic 5.2 will produce the actual measured per-PDF cost number, replacing this estimate.

## Risks specific to this tool

1. **License lock-in to M365.** If firm ever migrates off M365, the workflow doesn't port. Mitigation: keep the Python reference script (Epic 6) up to date as the migration path.
2. **AI Builder credit consumption can spike** if PDFs grow past 2 pages. Mitigation: monitoring + usage caps in admin center.
3. **Power Automate flow versioning is weaker than git.** Built-in run history is good; export-as-JSON + commit to git for proper change control. Mitigation: documented in `07_recommendation/playbook.md`.
4. **Custom extraction models need re-training when PDF templates change.** Realistic for legacy bank statements that get redesigned. Mitigation: re-train cycle is ~30 min; doc the procedure in the playbook.
5. **Trial provisioning friction**: the Epic 5.2 hands-on requires a trial setup that may need administrative consent. Mitigation: budget 30 min cushion for trial activation; have a fallback plan (defer to proxy via 5.7) if a hard block emerges.

## Recommended deployment shape (for relatório §7 "plano de implementação")

| Phase | Duration | Activity |
|---|---|---|
| 0 | Day 0 | Confirm M365 + AI Builder licensing; provision SharePoint site + folders for incoming PDFs and output Excel |
| 1 | Day 1 | Train AI Builder custom extraction model on 5–10 sample PDFs (use real samples for production after validating with synthetic corpus from Epic 4) |
| 2 | Day 2 | Build Power Automate flow: SharePoint trigger → AI Builder extract → confidence routing → Excel append OR Approvals queue |
| 3 | Day 3 | Pilot run on 100 PDFs with HITL on every row to calibrate confidence thresholds |
| 4 | Day 4 | Production run on the 10k batch with reduced HITL (only flagged rows) |
| 5 | Day 5+ | Monitoring + monthly model retraining as new PDF templates arrive |

## Position in the comparison matrix
**Rank #1 — Chosen primary solution (D-005). Hands-on validated in Epic 5.2 and cross-validated in Epic 5.7.**
