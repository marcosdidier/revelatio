# Walkthrough — Epic 5.2 Power Automate + AI Builder Hands-On Test

> **Format**: pair-testing. Marcos drives the browser; AI co-pilot prepares prompts/specs and helps interpret outputs.
> **Estimated time**: 2–3 hours total, broken into phases that can be paused between.
> **Prerequisite**: 8 synthetic PDFs in `05_synthetic_data/pdfs/` (already done, Epic 4).

## Test phases (status updated as we go)

| Phase | Activity | Time | Status |
|---|---|---|---|
| 0 | Provisioning (M365 trial + Power Automate Premium + AI Builder credits) | ~30 min | ✅ closed 2026-05-09 (~75 min actual) |
| 1 | Custom Document Processing model: upload, tag, train | ~30 min | ✅ closed 2026-05-10 |
| 2 | Power Automate flow build (SharePoint → AI Builder → Excel + Approvals) | ~60 min | ✅ closed 2026-05-10 (pragmatic-core scope) |
| 3 | Run on example PDF | ~10 min | ✅ closed 2026-05-10 — example PDF surfaced the layout-drift finding |
| 4 | Run on 4 synthetic PDFs (incl. F04 corrupted to verify HITL routing) | ~15 min | ✅ closed 2026-05-10 — all 4 routed to Verdadeiro, no hallucinations |
| 5 | Score against gold; capture artifacts; write notes.md | ~30 min | ✅ closed 2026-05-10 — **avg 92.8% / 0 hallucinations** (see notes.md) |

## Phase 0 — Provisioning

### Step 0.1 — Decide starting state

Two options:
- **A. Fresh M365 trial** (recommended): clean slate, no contamination from existing tenant settings, easy to discard after the test
- **B. Existing M365**: reuse what you have; faster but might bump into corporate policies blocking Power Automate Premium / AI Builder

Decision will be recorded in `notes.md`.

### Step 0.2 — Sign up for M365 Business Basic 30-day trial

URL: https://www.microsoft.com/en-us/microsoft-365/business/microsoft-365-business-basic

What to capture:
- Tenant name (e.g. `yourname.onmicrosoft.com`)
- Admin email
- Date provisioned

### Step 0.3 — Activate Power Automate Premium trial

Inside the M365 admin center → Billing → Purchase services → Trials → Power Automate Premium.

### Step 0.4 — Activate AI Builder credits trial

Power Platform admin center (`admin.powerplatform.microsoft.com`) → Resources → Capacity → Add-ons → AI Builder credits trial.

(Microsoft may renumber UI paths; navigate by intent rather than by exact words.)

### Step 0.5 — Confirm everything works

Open `make.powerautomate.com` → AI Builder → "Build a model" — should see Document Processing as an option.

If you see it: ✅ phase 0 done.
If you don't: paste the error/screenshot here so we troubleshoot.

## Phase 1 — Train the Custom Document Processing model

**Spec for the model**:
- Type: **Document Processing → Custom**
- Document type description: *"Banco X debt-collection client dossier (2 pages)"*
- Sample documents to upload: 5 PDFs from `05_synthetic_data/pdfs/`:
  - F01_perfect.pdf
  - F02_missing_email.pdf
  - F05_cpf_no_separators.pdf
  - F06_alternate_labels.pdf
  - F07_skewed_page2.pdf
- Fields to tag (16 page-1 + 17 page-2 = 33 fields total — see `01_field_map/field_map.md` for the canonical list)

**Recommended field-tag groups in AI Builder UI**:
1. Group "Identificação Cliente": client_name, cpf, birth_date, phone, email, address, postal_code
2. Group "Informações Dívida": contract_number, product, contract_date, original_amount, updated_balance, days_overdue, status, last_contact_attempt, internal_owner
3. Group "Comprovante Endereço": proof_address_holder, proof_address_line, proof_address_neighborhood, proof_address_postal, proof_reference, proof_period, proof_value, proof_barcode
4. Group "Comprovante Bancário": bank_name, bank_branch, bank_account, transaction_date, transaction_type, payer, payee, amount_paid, authentication_code

**What to capture**:
- Screenshot of the field-tagging UI on at least 2 PDFs (`screenshots/01_tagging_F01.png`, `02_tagging_F02.png`)
- Final accuracy report (after training): screenshot → `screenshots/03_accuracy_report.png`
- Raw JSON of one prediction → `raw_output/ai_builder_prediction_F01.json`

## Phase 2 — Build the Power Automate flow

> **Scope decision (2026-05-10)**: building the **pragmatic-core flow** rather than the full spec below. The Approvals workflow and Teams notification are documented in `02_tool_universe/07_power_automate.md` and will be screenshotted-but-not-wired so the relatório can describe them as trivial extensions. Time budget: ~30-40 min vs. ~60-90 min for full spec, preserving runway for Epics 5.3-5.10, 6, 7, 8, 9, 10 before 2026-05-13 deadline.

### Pragmatic-core flow (what we're actually building)
```
Trigger:    SharePoint — When a file is created in folder /Documents/IncomingPDFs
Action 1:   AI Builder — Predict using "Revelatio Custom Doc Processing" model
Action 2:   Initialize variable ConfidenceFloor = 0.85 (Float)
Action 3:   Compose — Average per-field confidence from prediction output
Condition:  avg confidence ≥ ConfidenceFloor
  Yes →   Excel Online (Business): Add row to /Documents/Output/debtor_extraction.xlsx (table "Debtors")
  No  →   SharePoint: Create item in "Pending Review" list (PDF, JSON, avg_conf, Status=Pending)
```

### Full spec (kept for reference; not built)

**Flow spec**:

```
Trigger: SharePoint — When a file is created in folder
  Site: <your test site>
  Folder: /Documents/IncomingPDFs

Action 1: AI Builder — Predict using your model
  Model: <the one trained in Phase 1>
  Document file: from trigger output

Action 2: Initialize variable "ConfidenceFloor"
  Type: Float
  Value: 0.85

Action 3: Compose — Average per-field confidence
  Inputs: <the predicted fields' confidence scores>

Condition: If average ≥ ConfidenceFloor
  Yes branch:
    - Excel Online (Business): Add a row into a table
      Workbook: /Documents/Output/debtor_extraction.xlsx
      Table: Debtors
      Map: each AI Builder field → spreadsheet column
  No branch:
    - SharePoint: Create item in "Pending Review" list
      Fields: PDF filename, extracted_json (compose), avg_confidence
    - Approvals: Start and wait for an approval (Approve/Reject)
    - On approval: Excel Online → Add row
    - On rejection: SharePoint list item flagged "Rejected"

Final action: Teams — Post a message to channel
  Body: "Flow run complete: {file} processed; {decision}"
```

**What to capture**:
- Flow JSON export: `raw_output/flow_export.json`
- Screenshot of the canvas view: `screenshots/04_flow_canvas.png`
- Run history of at least one execution: `raw_output/run_history_run1.json`

## Phase 3 — Run on the example PDF

Drop `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` into the trigger SharePoint folder. Watch the run complete.

**Capture**:
- Resulting Excel file → `output.xlsx`
- Screenshot of the populated row → `screenshots/05_excel_row.png`
- Run history JSON → `raw_output/run_history_example.json`

## Phase 4 — Run on 4 synthetic PDFs

Drop these 4 PDFs in sequence:
- F02_missing_email.pdf — should produce a row with email empty (NOT invented)
- F04_low_quality_page2.pdf — likely to score lower confidence; should route to Approvals queue
- F06_alternate_labels.pdf — tests anchor-by-semantic vs anchor-by-text
- F08_partial_obscure_page2.pdf — should partially extract; expect HITL routing

**Capture**:
- Each run history → `raw_output/run_history_F0X.json`
- The Approvals queue snapshot → `screenshots/06_approvals_queue.png`
- The "Pending Review" SharePoint list → `screenshots/07_review_list.png`

## Phase 5 — Scoring

Open `score.csv` (already copied here from the template). For each row:
1. Find the AI Builder predicted value in the per-PDF prediction JSON
2. Paste into `tool_value` column
3. Apply normalization rules from `scoring_rubric.md`
4. Mark `result`: exact / partial / miss / hallucination
5. Compute `score = result_score × weight`

Sum scores across all rows → divide by 36 × 100 → final per-PDF percentage.

Then write `notes.md` answering all the prompts from `00_test_plan.md` ("Notes.md template" section).

## Cost recording

Open `cost_log.md` (will be created in Phase 5):
- AI Builder credits consumed for training: ____ credits
- AI Builder credits per prediction: ____ credits/page
- Trial license value if purchased commercially: ~$15/seat (Premium) + $500/mo for 20k credits
- **Estimated 10k-batch cost**: ____

## Known sticking points to watch for

- AI Builder may require a Dataverse environment to be created first; takes ~5 min, blocks the model creation
- Custom Document Processing models work best with at least 5 sample documents — that's why we provide 5 from the synthetic corpus
- AI Builder's accuracy report sometimes shows misleadingly low numbers if the page-2 image is too noisy on a small sample size
- Trial signups occasionally bounce on email domain restrictions — have a backup email ready

## Where this test feeds downstream

- **score.csv** → `04_experiments/scoreboard.md` (Epic 5.10)
- **notes.md** → relatório §2 ("o que funcionou") and §3 ("o que não funcionou") in PT-BR
- **screenshots/** → pulled into the video (Epic 9.2 slides + 9.3 demo) for visual evidence
- **cost_log.md** → `07_recommendation/roi.md` ROI model
- **flow_export.json** → bundled in `08_deliverables/materiais_adicionais/`
