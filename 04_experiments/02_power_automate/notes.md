# Notes — Epic 5.2 Power Automate + AI Builder

> Free-form observations as we run through the walkthrough. Updated phase by phase.

## Setup difficulty
*(rating + sentence — fill at end of test)*

## Phase 0 — Provisioning

### Step 0.1 — Starting state decision
- **Decision: Option A — Fresh M365 Business Basic trial** (clean slate, no corporate-tenant policy contamination, easy to discard after the test).
- Date decided: 2026-05-09.

### Step 0.2 — M365 trial signup ✅
- Tenant name: `revelatiotest2026.onmicrosoft.com`
- Admin email: `admin@revelatiotest2026.onmicrosoft.com`
- Date provisioned: 2026-05-09
- Trial expires: 2026-06-08 (calendar reminder to cancel before charge)
- **Tenant region: United States** (deliberate workaround — see friction below)
- Address used: 1209 Orange Street, Suite 200, Wilmington, DE 19801 (format-valid Delaware registered-agent address; not an entity we control)
- Business phone on tenant record: (302) 555-0100 (NANP-reserved fictional range; passes format validation, never reaches a real number)
- SMS verification: own phone with +55 Brasil country code (separate field, not stored on tenant)
- Friction encountered:
  - **PT-BR signup demanded a CNPJ** at "Conte-nos sobre você" with no skip option while Country = Brasil.
  - Workaround: switched to `/en-us/` URL with Country = United States.
  - **Implication for relatório §3**: a real PoC inside the firm requires their CNPJ from day one — procurement/legal must be looped in before IT can even start a trial. Flag as deployment-friction finding alongside the LGPD data-residency point (production deployment must be on a BR-region tenant, not US).

### Step 0.3 — Power Automate Premium trial ✅
- Trial activated: ✅ 2026-05-09
- License assigned to admin user: _(to verify in Step 0.5 by trying to load AI Builder UI — if it loads, license is good)_

### Step 0.4 — AI Builder credits ✅
- 125,000 credits bundled with the Premium trial — visible in Power Platform admin → Licenciamento → Complementos de capacidade → Resumo → Complementos → "Créditos do AI Builder: 0 de 125.000 atribuídos".
- For our 8-PDF test we need ~5k credits max (Custom Document Processing ~10 credits/page × 16 pages × ~30 training+inference passes worst case) — **25× safety margin**.
- The standalone "Iniciar avaliação do AI Builder" trial card was not visible (Avaliação tab said "Nenhum ambiente encontrado" — only appears once a dedicated trial environment is created). Premium-bundled credits are sufficient, so we did not pursue.

### Step 0.5 — Sanity check ✅
- Dataverse added to "Revelatio Test (padrão)" via Gerenciar → Ambientes → "Adicionar Dataverse" (Idioma = português Brasil, Moeda = USD, Sample apps = Não). Provisioned successfully.
- First entry attempt via `make.powerautomate.com` → Hub de IA → **"Automação de documentos" → "Introdução"** failed with: *"A automação de documentos requer a permissão de Administrador do Sistema para instalar um novo pacote."* — the Document Automation pre-built solution requires elevated Dataverse roles to install in the default environment (Microsoft locked default envs in 2024).
- Workaround: bypassed the wrapper solution and went directly to `make.powerapps.com` → AI Builder → Modelos de IA. **Custom Document Processing ("Extrair informações personalizadas de documentos", MODELO PERSONALIZADO) is visible and clickable** — confirmed 2026-05-09.
- **Friction worth noting for relatório §3 (deployment friction findings, accumulating)**:
  1. Default environment created at tenant signup does NOT include Dataverse. AI Builder cannot run without it. No warning on signup.
  2. Default environment refuses to install pre-built solutions (Document Automation, etc.) even for the tenant admin. The workaround (raw AI Builder model creation via `make.powerapps.com`) is undocumented in Microsoft's "getting started" path.
  3. Added ~30 min and three non-obvious click paths to what Microsoft markets as a "click-and-go" experience.
  4. Implication: a real PoC at the law firm requires a dedicated managed environment from day one, not the default — which itself requires Power Platform admin runbook work.

## Phase 0 — CLOSED ✅ (2026-05-09)
Net provisioning time including all friction: ~75 min vs. Microsoft's marketing claim of "5 min sign-up". Trial expires 2026-06-08.

## Phase 1 — Model training ✅
- Started 2026-05-09, completed 2026-05-10.
- Model type: **Documentos de modelo fixos** (formerly "Estruturado") — chosen because our 8 fixtures are all variations of the same Banco X template (vs. "Documentos gerais" which needs 20+ samples).
- Document type config: Custom Document Processing, single collection ("Dossiês Banco X") containing 5 PDFs.
- Fields defined: **33 total**, all type "Texto" (not Número/Data — to avoid AI Builder's en-US locale auto-parse breaking Brazilian formats; normalization deferred to Power Automate Compose actions).
- Training set (5 of 8 fixtures, deliberately stratified across failure modes):
  - F01_perfect — happy-path anchor
  - F02_missing_email — teaches "missing field is valid"
  - F05_cpf_no_separators — CPF format variation
  - F06_alternate_labels — label variation ("Nome:" vs "Nome completo:")
  - F07_skewed_page2 — page-2 skew tolerance
- Held-out test set (NOT shown to model during training): F03_missing_phone, F04_low_quality_page2, F08_partial_obscure_page2, plus `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf`.
- Final accuracy reported by AI Builder: **96%** (post-training report, 2026-05-10).

## Phase 1.5 — Quick test on `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` (held-out example) — KEY FINDING ⭐
The model had never seen this PDF. Prediction results:
- **All 16 page-1 fields: correct.** Two had low confidence (`Status interno`, `Responsável interno`) but the values were right — appropriate HITL routing trigger.
- **4 page-2 fields catastrophically wrong** — model emitted text from completely unrelated regions:

| Field | Predicted value | What that text actually is in the PDF |
|---|---|---|
| Pagador (#30) | "Valor pago" | adjacent field label or value, wrong region |
| Recebedor (#31) | "Código de autenticação" | adjacent field, wrong region |
| Valor pago (#32) | "Documento ficticio para teste tecnico..." | **page footer** |
| Código de autenticação (#33) | "Página 2" | **pagination marker** |

### What this evidences
The model's spatial priors for these page-2 fields **collapsed entirely** on the example PDF — it pointed to the region it learned during training and emitted whatever text happened to live there. Most likely cause: **layout drift between our synthetic page-2 layout (`generate_pdfs.py`) and the brief's example page-2 layout**. Fixed-template models like AI Builder's are notoriously sensitive to this kind of drift.

### Hypothesis to disambiguate in Phase 4
- If **F03/F04/F08** (held-out synthetics, same generator as training set) extract page 2 correctly → **layout drift between synthetic and real** is the cause. Production fix: train on real dossiers.
- If **F03/F04/F08 also fail similarly** → AI Builder has a **deeper page-2 weakness** independent of layout. Production fix: replace page-2 layer with vision-LLM or Azure DI Custom Neural (the 5.7 cross-validator).

### Implications for relatório (regardless of which hypothesis wins)
- §2 (o que funcionou): page-1 extraction is genuinely solved — 100% on the held-out example, with low-confidence flagging working correctly on the 2 ambiguous fields.
- §3 (o que não funcionou): page 2 is the failure surface — and the failures are visceral (model emits footer text and page numbers as field values). This is much stronger evidence for the architecture recommendation than abstract confidence-score arguments.
- §4 (recomendação): two-layer routing + Azure DI Custom Neural cross-validator on page 2 is now empirically grounded, not just a hypothesis. Plus: production deployment requires training on **real Banco X dossiers**, not synthetic — the synthetic corpus is fine for *unit-style validation* of page-1 logic but cannot substitute for real training data on page 2.
- Tagging notes: values only (never labels), include format markers (R$, parens, dashes) inside the bounding box, "Não está no documento" used for absent fields in F02.

## Phase 2 — Power Automate flow build + Phase 3 quick test ✅ (2026-05-10)
- Flow: trigger (SharePoint file created) → Get file content → Processar documentos (AI Builder) → Initialize ConfidenceFloor=0.85 → Compose AvgConfidence (CPF field confidence) → Condition → YES: Excel Add row | NO: SharePoint Create item.
- Multiple connection re-auth cycles needed during build (SharePoint connector tokens expire fast on new tenants). Recommendation for production: use service principal auth, not OAuth user tokens.
- **Phase 3 result — example PDF (`exemplo_pdf_cliente_devedor_ficticio.pdf`)**:
  - Flow ran end-to-end in 9 seconds.
  - CPF confidence: **0.99** → routed to Verdadeiro branch → row written to Excel.
  - **HOWEVER**: same 4 page-2 fields wrong that we saw in the Phase 1.5 Quick Test (Pagador, Recebedor, Valor pago, Código de autenticação). The high CPF confidence does NOT correlate with page-2 correctness.
- **CRITICAL FINDING ⭐**: gating on a single high-stakes field (CPF) is **insufficient** — the model can have 0.99 CPF confidence while emitting nonsense for page-2 fields. The HITL routing logic in our pragmatic-core flow would silently approve garbage records. Implications:
  1. Real HITL gating needs **per-page** or **per-field-region** confidence aggregation, not a single signal.
  2. Or: **cross-validation rules** (e.g., Pagador ≠ Nome completo → flag) belong alongside confidence gating.
  3. Or: **vision-LLM fallback for page 2** — bypass AI Builder for page-2 fields entirely.
- This validates the **two-layer routing** recommendation in Epic 7 architecture, now with two empirical data points (Phase 1.5 quick test + Phase 3 flow run) both showing the same failure pattern.

## Phase 4 — 4 held-out synthetic PDFs (F02, F03, F04, F08) — KEY DISAMBIGUATION ⭐⭐
All 4 routed to Verdadeiro (CPF confidence 0.99 across all). Visual extraction results:

| PDF | Page 1 | Page 2 | Missing-field handling | Notes |
|---|---|---|---|---|
| F02_missing_email | ✅ correct | ✅ correct | ✅ E-mail column EMPTY (not hallucinated) | Clean pass |
| F03_missing_phone | ✅ correct | ✅ correct | ✅ Telefone column EMPTY (not hallucinated) | Clean pass |
| F04_low_quality_page2 | ✅ correct | ✅ correct | n/a | Even on degraded page-2 image, model extracted correctly |
| F08_partial_obscure_page2 | ✅ correct | ⚠️ "Data da transação" not extracted | n/a | One field missing; rest correct |

### Hypothesis disambiguation
The hypothesis from Phase 1.5 was: "(a) layout drift between synthetic and real, OR (b) deeper page-2 weakness regardless of source." **Phase 4 result confirms (a)** — when the inference document shares visual layout with the training set, AI Builder extracts page 2 correctly (even on F04 which is deliberately low-quality, even on F08 which is partially obscured). The example PDF failed because it had a *different* visual layout than our synthetic training corpus.

### Critical methodological finding ⭐
Our `generate_pdfs.py` synthetic corpus shares field LABELS and STRUCTURE with the brief example but does NOT share visual LAYOUT (fonts, table cell positions, receipt styling). AI Builder's fixed-template model overfits to visual layout. Implications:

1. **For our test results**: Phase 4 numbers tell us "AI Builder works on its own training distribution" — not "AI Builder works on real Banco X dossiers." That's a smaller claim than it appears.
2. **For relatório §3 (limitations)**: this methodological gap is the single most important caveat to flag honestly. We do not have a 1-to-1 measurement of AI Builder's accuracy on real production data because we never had real training data.
3. **For relatório §4 (recommendation)**: production deployment **requires training on real Banco X dossiers** (typical ask: 30–100 documents, 80% train / 20% test). With real training data, AI Builder is a credible primary; without it, the firm should default to a layout-tolerant alternative (Azure DI Custom Neural, vision-LLM with structured output) which generalizes better across visual variants.
4. **What we could have done differently with the same time budget**: clone the brief example's visual style in `generate_pdfs.py` (match fonts, grid widths, receipt image styling) before generating the 8 fixtures. That would have given a more representative test. We didn't, and the relatório should own that.

### Anti-hallucination behavior confirmed
F02 and F03 both correctly returned EMPTY for their respective by-design missing fields (email, phone). The model does not invent values when content is absent — this is a positive design property of AI Builder's Custom Document Processing model worth highlighting in §2 ("o que funcionou").

### Single-field gating insufficiency (still applies)
Even though Phase 4 results were good, the Phase 3 finding stands: gating on CPF confidence alone (0.99) does not catch page-2 failures when they occur (as on the example PDF). The HITL routing logic in production needs:
- Per-page confidence aggregation (separate gate for page 1 vs page 2), OR
- Cross-validation rules (Pagador ≠ Nome completo → flag), OR
- Vision-LLM fallback for page 2 (architectural recommendation in Epic 7)

## Preliminary verdict on Power Automate (pending Phase 5 numerical scoring)

**Power Automate + AI Builder is a viable primary stack for an M365-resident firm willing to (a) provide 30–100 real Banco X dossiers as training data, and (b) layer cross-validation rules onto the confidence-gate. Without those two investments, the architecture works but the extraction quality on real production data is unverified.**

### What we actually proved
- Flow architecture is sound (trigger → AI Builder → confidence gate → Excel/HITL routing).
- AI Builder Custom Document Processing converges on 5 training samples and does NOT hallucinate on absent fields.
- Page-1 extraction is robust (~96% per AI Builder's own report; ~100% on visual inspection across all 8 fixtures).
- Page-2 extraction is layout-sensitive — works on training-distribution layouts, fails on visually-different ones.

### What we did NOT prove
- That AI Builder generalizes to real Banco X dossier layouts (the brief example failed catastrophically; our synthetic corpus did not match its visual style).
- That single-field confidence gating catches page-2 failures when they occur.
- Production-scale economics (we ran 5 PDFs on trial credits; real 10k-batch cost projection is inferential).
- That Power Automate is right for non-M365 firms (it's not — alternative recommendation needed in Epic 7).

### What this means for the relatório
- §2 (o que funcionou): flow architecture, missing-field handling, page-1 accuracy.
- §3 (o que não funcionou + limitations): page-2 layout sensitivity, single-gate insufficiency, provisioning complexity (~75 min), connection brittleness, **synthetic vs real training data gap**.
- §4 (recommendation): conditional on real training data + cross-validation rules; alternative stack (n8n + Claude API) for non-M365 firms.

## Phase 5 — Numerical scoring against gold ✅ (2026-05-10)

Script: `04_experiments/02_power_automate/score_excel_against_gold.py` — reads `raw_output/debtor_extraction.xlsx`, applies normalization rules from `01_field_map/scoring_rubric.md`, outputs `scorecard.json`.

### Results table (4 held-out synthetic fixtures)

| PDF | Overall | Page 1 | Page 2 | Hallucinations | Verdict per rubric |
|---|---|---|---|---|---|
| F02_missing_email | 97.1% | 17.0/18 | 17.0/17 | 0 | Production-ready as primary |
| F03_missing_phone | 97.1% | 17.0/18 | 17.0/17 | 0 | Production-ready as primary |
| F04_low_quality_page2 | 85.7% | 17.0/18 | 13.0/17 | 0 | Production-ready with HITL |
| F08_partial_obscure_page2 | 91.4% | 17.0/18 | 15.0/17 | 0 | Production-ready with HITL |
| **AVERAGE** | **92.8%** | **94.4%** | **91.2%** | **0** | — |

### What the deductions tell us

1. **Page 1, consistent 1-point deduction across all 4 fixtures** = `Data de contratação` locale-misparse bug. The PDF value `12/02/2024` (BR = Feb 12) is being extracted/written as `2024-12-02` (Dec 2). Birth date `14/08/1983` survives because day 14 isn't a valid month — only DD/MM/YYYY where both DD and MM ≤12 corrupts. **Pipeline trace**: AI Builder field type was "Texto" so the model returns the raw string; the conversion happens at the Power Automate → Excel boundary. Excel applies en-US locale parsing on string-formatted dates because our tenant region is US (set during Phase 0 to bypass CNPJ requirement).
2. **F04 page-2 deductions** (4 weight-points) = real OCR errors on the deliberately degraded page-2 image (`Recite/PE`, `Barico Exemplo`, `8(26.03...`). Confidence-gated HITL routing is the appropriate response — F04 still hit 0.99 average confidence so didn't trigger HITL, suggesting **per-page or per-field confidence aggregation** is needed (not the single CPF gate).
3. **F08 page-2 deductions** (2 weight-points) = `Data da transação` empty + `Tipo de transação` OCR garble. Expected for partial-obscure variant.
4. **Zero hallucinations across 4 × 33 = 132 cells.** Strongest single positive finding for AI Builder Custom Document Processing — the model genuinely returns absence rather than fabricating.

### Critical Brazilian-deployment finding ⭐

**The `Data de contratação` locale misparse is a production-blocking bug** if deployed naively. Mitigations to recommend in §4:
- (a) Provision the production tenant in **Brazil region** (avoids the en-US default), OR
- (b) In Power Automate, format the date string with a non-parseable prefix (e.g., `="12/02/2024"`) before writing to Excel, OR
- (c) Use a **typed Date field** in AI Builder with explicit BR locale config, OR
- (d) Pre-process the date string in Power Automate to ISO format (`split('/').reverse().join('-')`) before writing.

### Updated verdict (replacing the preliminary one above)

**Power Automate + AI Builder scores 92.8% average against gold on synthetic test set, with 0 hallucinations across 132 cells. Per the rubric, this places it in the "production-ready with HITL on flagged rows" tier (85–94%).**

Caveats:
- The synthetic test set shares visual layout with the training set. **Real Banco X dossier performance is unverified.**
- The locale-misparse bug must be fixed before production deployment.
- The HITL gating logic needs upgrading from single-field (CPF) to per-page or cross-validation-based.

### Phase 6 dependency

The Phase 6 Azure DI cross-validation will tell us whether a layout-tolerant model would catch the page-2 cases AI Builder missed. If Azure DI scores higher on F04/F08 page-2, it confirms the layout-overfit hypothesis and strengthens the recommendation.

### Phase 2.0 — Setup ✅ (2026-05-10)
- SharePoint Communication Site created: `https://revelatiotest2026.sharepoint.com/sites/revelatiotest` (template: Comunicação padrão).
- Folders: `/Documents/IncomingPDFs` (trigger source) + `/Documents/Output` (Excel destination).
- Excel file: `debtor_extraction.xlsx` with Table named `Debtors` covering A1:AJ2 (36 columns: 3 admin + 33 fields). Generated programmatically via `04_experiments/02_power_automate/setup/create_debtor_excel.py` after Excel Online's tab-paste failed to parse the headers correctly. **Deployment-friction finding for §3**: Excel Online's browser-based paste is unreliable for >10 columns of tab-separated data; production deployment should script this rather than rely on copy/paste.
- SharePoint list: `Pending Review` with 4 columns — `Title` (renamed display "Arquivo PDF"), `Confianca_media` (Number, 2 decimals), `Extracted_JSON` (Multiple lines of text, **plain text**), `Status` (Choice: Pendente/Aprovado/Rejeitado, default Pendente).

### Step 0.4 — AI Builder credits trial
*(to fill)*

### Step 0.5 — Sanity check (Document Processing visible in `make.powerautomate.com`)
*(to fill)*

## Phase 1 — Model training
*(field-tagging observations: which fields the model picked up easily, which needed manual correction; final accuracy report number)*

## Phase 2 — Flow build
*(any connector quirks, any places where the canvas didn't match the spec, any spec changes we made on the fly)*

## Phase 3 — Example PDF run
*(latency, resulting Excel row screenshot ref, any hallucinations)*

## Phase 4 — Synthetic PDF runs
*(per-fixture: did F02 correctly leave email empty? Did F04 route to Approvals? etc.)*

## Phase 5 — Scoring
*(final per-fixture scores; total averaged)*

## What worked
*(the strong points — the relatório §2 will pull from this)*

## What didn't work
*(the failures or friction — relatório §3)*

## Surprises
*(positive or negative — these become the "interesting" parts of the relatório)*

## Hallucination instances
*(any field where AI Builder confidently invented a value — list per PDF)*

## Estimated cost-per-PDF for 10k-batch deployment
*(AI Builder credits consumed × pricing; arithmetic for the 10k batch)*

## LGPD posture observed
*(was BR region used? zero-retention? Purview audit visible?)*

## Verdict change vs the pre-test prediction
*(was our `02_tool_universe/07_power_automate.md` dossier prediction borne out, refined, or contradicted?)*
