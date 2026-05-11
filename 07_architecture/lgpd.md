# Project Revelatio — LGPD Compliance Posture

> **Status**: Epic 7 deliverable (3 of 3). Written 2026-05-11. Internal language: EN. PT-BR translation lives in the relatório (Epic 8 §7).

A debtor dossier is dense personal data: CPF, nome completo, endereço, telefone, email, valor da dívida, dados de cobrança. This document is the engineering attestation of how Project Revelatio handles that data, article-by-article against the LGPD (Lei nº 13.709/2018). It names the known production gaps honestly, gives the firm's DPO a checklist they can sign off on, and resists the "but is this legal?" stakeholder question with concrete article-level posture.

This is **not legal advice.** It is a controlador-side attestation that the DPO and outside counsel can use as input to their own Relatório de Impacto à Proteção de Dados (RIPD) and final compliance signoff.

---

## 1. Scope and PII categories

**Personal data flowing through the system** (all from Banco X dossiers):

| Category | Examples in the dossier | LGPD Art. 5 classification |
|---|---|---|
| Identifying | Nome completo, CPF | dado pessoal (Art. 5º, I) |
| Contact | Endereço, telefone, email | dado pessoal (Art. 5º, I) |
| Financial | Valor da dívida, número do contrato, datas de contratação e vencimento | dado pessoal (Art. 5º, I) |
| Behavioral / inferred | Status interno, dias em atraso, responsável interno | dado pessoal (Art. 5º, I) |

**Dados pessoais sensíveis** (Art. 5º, II — origem racial, convicção religiosa, saúde, biometria, etc.): **none in scope**. Banco X dossiers do not contain sensitive categories. If this changes in a future intake (e.g., medical-debt dossiers including diagnoses), the posture below must be re-evaluated.

**Roles** (Art. 5º, VI–IX):

| Role | Entity in our deployment |
|---|---|
| **Controlador** | The contracting law firm (decides finalidade and meios) |
| **Operador (engine)** | Project Revelatio pipeline running in firm-controlled infrastructure (M365 tenant or self-hosted Python) |
| **Operadores (sub-processadores)** | Microsoft (Azure DI, M365), Anthropic (Claude API). Both bound by their respective DPAs. |
| **Encarregado / DPO** | Designated by the controlador per Art. 41 |
| **Titulares** | The debtors named in each dossier |

---

## 2. Bases legais (Art. 6 e Art. 7)

### Princípios (Art. 6º)

Each princípio with the corresponding system-side measure:

| Princípio (Art. 6º) | How the system honors it |
|---|---|
| I — finalidade | Specific purpose: extracting fields from debtor dossiers for cobrança execution. No re-use for unrelated purposes. |
| II — adequação | The 32-field schema is exactly what cobrança requires; no over-collection. |
| III — necessidade | Only the fields needed for the cobrança workflow are extracted (vs. dumping the entire OCR). |
| IV — livre acesso | Direitos do titular flow in §8. |
| V — qualidade dos dados | Cross-validation gate + HITL queue prevent low-quality rows from propagating (`07_architecture/diagrams.md` §3). |
| VI — transparência | This document + relatório §7 + firm's published privacy notice. |
| VII — segurança | §9 below: encryption-at-rest, TLS-in-transit, RBAC, audit trail. |
| VIII — prevenção | HITL queue prevents automated harm to the titular (§10 below). |
| IX — não-discriminação | No demographic field is used; routing decisions (HITL) are based on data-quality signals only. |
| X — responsabilização | Audit log (`audit.csv`) + Power Automate run history provide demonstrable compliance evidence. |

### Hipóteses (Art. 7º)

Primary basis: **Art. 7º, V — execução de contrato ou procedimentos preliminares**. The dossier extraction is preparatory work for cobrança judicial / extrajudicial, which is the firm's contractual mandate from Banco X.

Secondary basis: **Art. 7º, IX — legítimo interesse do controlador** (LGPD Art. 10). The automation step itself (vs. doing the same extraction manually) is justified by legítimo interesse in operational efficiency, balanced against titular impact (no automated *decision-making* — see §10).

Banco X's *own* legal basis for processing the debtors' data is upstream of this project and presumed to be Art. 7º, V (contrato bancário) and/or Art. 7º, VI (exercício regular de direitos em processo judicial / administrativo). The firm should confirm in its DPA with Banco X.

---

## 3. Data residency (Art. 33–36 — transferência internacional)

### Current state — honestly flagged

| Component | Current region | Status |
|---|---|---|
| M365 tenant | **United States** (`revelatiotest2026.onmicrosoft.com`) | ⚠️ trial choice — see below |
| Azure Document Intelligence resource | East US (`di-revelatio-test`) | ⚠️ same |
| Anthropic API (Claude) | US infrastructure (default) | acceptable with DPA, see below |
| `dossiers.csv` / `audit.csv` (PoC outputs) | Local filesystem (`06_reference_script/test_corpus/`) | PoC-only; production lives in firm-controlled storage |

The US tenant region is documented in `SESSION_RESUME.md` (Tenant info §) and `04_experiments/02_power_automate/notes.md` Phase 0.2: the trial was provisioned in the US to bypass the CNPJ requirement of the BR signup flow. **This was an evaluation-time workaround, not a production decision.**

### Production posture — required before real Banco X data is processed

**Option A (preferred): in-country processing.**
- Move M365 tenant to a Brazilian licensee (firm's actual CNPJ-bound tenant).
- Provision Azure DI in **Brazil South** region.
- Document in the firm's RoPA (registro das operações de tratamento, Art. 37) that all in-region processing happens in Brazil South.

**Option B (acceptable with safeguards): cross-border transfer.**
- Document the transfer under **Art. 33** with one of: (I) país adequado, (II) cláusulas contratuais-padrão, (III) normas corporativas globais, (V) garantia de cumprimento dos princípios, or (VII) execução de contrato com o titular.
- Microsoft and Anthropic both publish DPAs that the firm can incorporate by reference (Microsoft Online Services DPA; `anthropic.com/legal/data-processing-addendum`).
- Maintain a Brazil-resident DPO and ANPD-facing point of contact regardless.

**Anthropic API geography note**: Anthropic processes API requests in US infrastructure by default. Cross-border transfer under Art. 33 is required regardless of whether Brazil South is used for M365/Azure DI, unless the firm switches to a Brazil-hosted LLM (e.g., self-hosted open-source model). The cost of switching is high; the cost-benefit favors keeping Anthropic + executing the Art. 33 paperwork properly.

---

## 4. Retention policy

Proposed retention schedule. Final durations must be aligned with the firm's existing document retention policy and any specific obligations from the Banco X master agreement.

| Artifact | Proposed retention | Legal basis |
|---|---|---|
| `dossiers.csv` (or its production equivalent) | **5 years from cobrança closure**, then anonymized | Cobrança execution period + audit window (Art. 16, V — obrigação legal); CC Art. 206 §5º I (5 anos para cobrança) |
| `audit.csv` (per-row trace including cross-val reason strings) | **2 years from row write**, then anonymized | Incident investigation window (Art. 46); shorter than dossiers because PII content in mismatch reasons is the highest-risk asset |
| Source PDFs in SharePoint / object storage | **Per firm's master document retention policy** (typically 5–10 years for cobrança) | Same as `dossiers.csv` |
| HITL queue closed entries | **2 years** | Mirrors `audit.csv` reasoning |
| API request/response logs (Anthropic, Azure DI) | Per provider DPA (Anthropic operational retention is short; Azure DI temp storage is 24h, see §7) | Out of firm's direct control; documented in DPAs |
| Anonymized aggregates (Project Revelatio metrics) | Indefinite | Art. 12 — anonymized data is outside LGPD scope |

**Operationalizing**: each artifact should have a scheduled deletion job (cron / Power Automate scheduled flow) keyed on the timestamp column. The audit log itself must record the deletion event.

---

## 5. Access control (RBAC matrix)

Principle: **least-privilege**. A paralegal sees only their assigned HITL queue rows, not the full backlog. A DPO has read access to audit logs but not write access to dossiers.

| Role | `dossiers.csv` | `audit.csv` | HITL queue | Source PDFs | System logs |
|---|---|---|---|---|---|
| Paralegal | R (assigned rows only) | — | R/W (own assignments) | R (own assignments) | — |
| Supervisor | R/W (review approvals) | R | R/W (queue management) | R | — |
| DPO / Encarregado | R | R | R | R | R |
| IT admin | R/W (operational maintenance) | R/W (rotation) | — | R | R/W |
| Sistema (service principal) | W (insert) | W (append) | W (insert) | R | W (append) |

**Implementation notes**:
- M365 path: enforce via SharePoint document-library permissions + AAD security groups; service principal uses managed identity.
- Non-M365 path: enforce via firm SSO (SAML/OIDC) integrated with the production replacement for `app.py`; service principal uses a scoped API key with `INSERT`-only DB privileges.
- **Paralegal access scoping** ("own assignments only") is enforced by row-level filters keyed on the assignee field, not by hiding columns. Test this with a read-only audit query before production cutover.

---

## 6. PII redaction in audit logs

### The gap

The current PoC writes cross-validation mismatch descriptions to `audit.csv` in plain text. If a mismatch involves CPF values (e.g., "page-1 CPF 123.456.789-01 does not match page-2 CPF 987.654.321-09"), those CPFs land in the audit log unredacted. This is documented in `06_reference_script/notes.md` line 75 as production hardening checklist item #5.

### The mitigation

Two-layer redaction:

1. **Masking for human-readable log lines**: render CPFs as `***.***.***-XX` (preserving the last two digits for disambiguation during a paralegal review).
2. **Hash-only for matching / dedupe**: store SHA-256(`CPF + per-firm salt`) in a separate column when cross-row correlation is needed without exposing the CPF itself.

Same approach for any other PII that lands in mismatch strings (email, phone). Names are harder — full-name redaction harms paralegal review effectiveness — so names are retained in audit logs but the audit log itself has stricter RBAC (§5).

### Why this matters under LGPD

Audit logs that contain unmasked PII expand the breach blast radius: a compromise of the audit log (typically lower-privilege than the production dossier store) leaks PII at scale. Art. 46 requires *medidas de segurança aptas a proteger os dados pessoais* — keeping CPFs out of secondary logs is a baseline expectation, not an enhancement.

---

## 7. In-tenant processing — no third-party logging

### Anthropic API (Claude)

> *"Anthropic may not train models on Customer Content from Services."*
> — Anthropic Commercial Terms, Section B, [anthropic.com/legal/commercial-terms](https://www.anthropic.com/legal/commercial-terms) (verified 2026-05-11)

API content is therefore not used for model training. Operational retention specifics (durations, sub-processor list) are defined in the Anthropic Data Processing Addendum: [anthropic.com/legal/data-processing-addendum](https://www.anthropic.com/legal/data-processing-addendum). The firm should incorporate the DPA by reference in its operador agreement with Anthropic.

### Azure Document Intelligence

> *"The incoming data is processed in the same region where the Document Intelligence resource was created."*
> *"Analyze response is stored for 24 hours from when the operation completes for retrieval. Customers can delete the analysis response at any time by utilizing the **Delete Analyze Result** API."*
> — Microsoft Learn, *Data, privacy, and security for Document Intelligence*, [learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/data-privacy-security](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/data-privacy-security) (verified 2026-05-11)

Production behavior implications:
- All Azure DI processing is in-region (Brazil South under the production posture in §3).
- The temporary 24-hour analysis-result storage is purgeable on demand via the `Delete Analyze Result` API. The reference Python engine should call this API immediately after retrieving results, narrowing the residency window to seconds (production hardening — `06_reference_script/notes.md` item to add).
- Custom model training (Azure DI Custom Neural) uses training data from customer-controlled blob storage, which inherits the firm's residency and retention posture.

### M365 / SharePoint / Power Automate

Inherit the M365 tenant region (per §3). Microsoft's Online Services DPA covers all sub-services consistently.

### Summary

No customer dossier content leaves the operadores' scoped processing flow. There is no third-party logging or analytics injection. The remaining cross-border transfer risk is the *infrastructure region* of the operadores themselves, addressed by §3 (production tenant in BR South + Art. 33 paperwork for the Anthropic geography).

---

## 8. Direitos do titular (Art. 18)

Each direito with the system-side process:

| Direito (Art. 18) | Process |
|---|---|
| I — confirmação da existência | Encarregado queries `dossiers.csv` by CPF, returns yes/no within SLA. |
| II — acesso | Encarregado exports the titular's row(s) and returns a human-readable copy. |
| III — correção | Paralegal uses the HITL queue review form to correct; audit log records the edit + reviewer ID. |
| IV — anonimização, bloqueio ou eliminação | Eliminação: row delete + cascade to source PDF deletion if no other legal basis applies. Anonymização: replace CPF / nome / endereço with hashes or "[ANONIMIZADO]" tokens; keep aggregated fields. |
| V — portabilidade | Export titular's data as CSV or JSON (LGPD does not specify format). |
| VI — informação sobre compartilhamento | Encarregado provides the list of operadores (Microsoft, Anthropic) and the firm's outbound use (Banco X workflow). |
| VII — informação sobre revogação | The titular is informed via the firm's privacy notice that the legal basis is execução de contrato + legítimo interesse, not consent — so revogação does not generally apply. Where it does (e.g., a specific marketing consent overlay), revogação is honored via a documented process. |
| VIII — peticionamento à ANPD | Encarregado provides contact channel for petição. |
| IX — revisão de decisões automatizadas | Not applicable — system does not make automated decisions affecting the titular. See §10. |

**SLA**: Art. 19 sets 15 dias úteis for *confirmação da existência e acesso* (item I/II). Other rights have no explicit statutory SLA but the firm should commit to 15 dias úteis as a uniform internal standard, with documented escalation if a specific request requires longer (e.g., cross-system search for the titular's data).

**Single point of contact**: titular requests must enter through a documented channel (typically `dpo@firm.com.br` or a web form on the firm's site) that creates a tracked ticket. The system itself does not expose a titular-facing endpoint.

---

## 9. Segurança e governança (Art. 46–49)

### Medidas técnicas (Art. 46)

| Control | Implementation |
|---|---|
| Encryption at rest | Azure Storage / SharePoint default encryption (AES-256); reference engine outputs encrypted at rest via OS-level encryption |
| Encryption in transit | TLS 1.2+ on all API calls (Azure DI, Anthropic, M365). Verified per Azure DI doc cited in §7 |
| Authentication | M365 path: AAD SSO; non-M365 path: firm SSO (SAML/OIDC) into the HITL queue UI |
| Authorization | RBAC per §5; row-level filters for paralegal scoping |
| Audit logging | Power Automate run history (M365) + `audit.csv` append-only (non-M365) + Azure Monitor for Azure DI calls |
| Secret management | API keys in `.env` (PoC); production uses Azure Key Vault / firm-standard secret store |
| Network isolation | M365 path: native to tenant; non-M365 path: production deployment should restrict Anthropic / Azure DI egress to known IP ranges where possible |

### Medidas administrativas

- DPO / Encarregado designated (Art. 41) — name and contact in the firm's public privacy notice.
- Incident response runbook — see §11 for invocation triggers.
- Paralegal training — annual LGPD refresher + Project Revelatio-specific HITL queue walkthrough.
- DPA register — Microsoft and Anthropic DPAs filed; renewal tracking for both.

### Comunicação de incidente (Art. 48)

| Trigger | Action |
|---|---|
| Unauthorized access to `dossiers.csv` or `audit.csv` | DPO notifies ANPD + affected titulares within "prazo razoável" (per Art. 48) |
| Compromised Anthropic / Azure DI credentials | Rotate keys immediately + assess whether dossier content was accessed via the keys' usage logs |
| Mass HITL queue rejection (>20% sustained) | Operational alert (not a privacy incident, but a quality-of-data alert that may indicate upstream tampering) |

### RIPD (Art. 38)

This processing activity should have a **Relatório de Impacto à Proteção de Dados** on file before production cutover, given:
- Scale (10k+ titulares per backlog batch; recurring intake)
- Automation (although not Art. 20 automated decisions — see §10)
- Cross-border transfer (Anthropic US infrastructure, possibly Azure US trial region)

The RIPD is the controlador's responsibility. This document provides the engineering inputs the DPO needs.

---

## 10. Decisões automatizadas (Art. 20)

**Posture**: the system does **not** make automated decisions that affect the titular's legal interests, credit, or rights.

What the system does:
- Extracts fields from PDFs into structured rows.
- Flags low-confidence rows for human review (HITL queue, `07_architecture/diagrams.md` §4).
- Cross-validates page-1 / page-2 consistency and routes mismatches to HITL.

What the system does **not** do:
- Decide whether to file an execução fiscal or similar enforcement step.
- Determine credit-worthiness, risk scoring, or any other rating that would change the titular's standing.
- Communicate with the titular directly.

Every consequential decision (cobrança strategy, judicial filing, settlement offer) is made by an attorney or supervisor downstream of the spreadsheet, with the spreadsheet being one input among many.

**Why this matters**: framing the system as a *data-preparation* operation (not a *decision* operation) keeps it outside Art. 20's review-on-request obligation, which would otherwise require human review of every dossier on titular request. The cross-validation gate + mandatory HITL on low-confidence rows is the affirmative evidence of this framing.

Document the framing in the firm's RoPA + privacy notice.

---

## 11. Known production gaps — honest checklist

These are gaps **as of the PoC state (2026-05-11)**. None of them is a blocker for the PoC's evaluation conclusions; all of them are blockers for processing real Banco X dossiers in production. Cross-referenced to `06_reference_script/notes.md` "Production hardening checklist" where applicable.

| # | Gap | Anchor | Fix before production |
|---|---|---|---|
| 1 | M365 tenant region is US (trial workaround) | `SESSION_RESUME.md` Tenant info §; `04_experiments/02_power_automate/notes.md` Phase 0.2 | Migrate to BR South or execute Art. 33 paperwork (§3 above) |
| 2 | `audit.csv` does not redact CPFs in mismatch strings | `06_reference_script/notes.md` hardening item #5 | Implement masking + hashing per §6 above |
| 3 | No formal RIPD on file | This document §9 | DPO produces RIPD using §1–§10 above as inputs |
| 4 | `app.py` (Streamlit demo) has no SSO | `06_reference_script/notes.md` hardening item #6 | Replace with production HITL form behind firm SSO; `app.py` stays as demo / video artifact only |
| 5 | Idempotency / replay-attack hardening pending | `06_reference_script/notes.md` hardening item #7 | Cache by content hash; reject duplicate uploads |
| 6 | Azure DI `Delete Analyze Result` not called explicitly | This document §7 | Add post-retrieval delete call to `azure_di_client.py`; narrows 24h temp storage to seconds |
| 7 | No scheduled deletion job for retention enforcement | This document §4 | Cron / scheduled Power Automate flow keyed on timestamp columns |
| 8 | Anthropic DPA not formally signed by firm | This document §7 | Firm legal team signs Anthropic DPA before production |
| 9 | Paralegal LGPD training not yet codified | This document §9 medidas administrativas | Annual training + Revelatio-specific HITL walkthrough |
| 10 | No incident response runbook published | This document §9 Art. 48 | Draft runbook covering the three trigger rows in §9 |

---

## 12. Anchors index

Every claim above maps to one of:

| Claim | Anchor |
|---|---|
| PII categories list | Direct enumeration from `06_reference_script/test_corpus/dossiers.csv` schema |
| No dados sensíveis in scope | Field-by-field check vs. Art. 5º, II |
| Primary base legal = Art. 7º, V | Project context — cobrança execution is preparatory work for contract enforcement |
| US tenant region is trial-only | `SESSION_RESUME.md` Tenant info §; `04_experiments/02_power_automate/notes.md` Phase 0.2 |
| Anthropic does not train on customer content | [anthropic.com/legal/commercial-terms](https://www.anthropic.com/legal/commercial-terms) §B (verified WebFetch 2026-05-11) |
| Anthropic DPA referenced | [anthropic.com/legal/data-processing-addendum](https://www.anthropic.com/legal/data-processing-addendum) |
| Azure DI in-region processing + 24h temp retention | [learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/data-privacy-security](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/data-privacy-security) (verified WebFetch 2026-05-11) |
| Cross-validation gate motivation | `04_experiments/02_power_automate/notes.md` Phase 1.5 finding #5 |
| HITL queue prevents Art. 20 review obligation | `07_architecture/diagrams.md` §4 design |
| `audit.csv` CPF leak | `06_reference_script/notes.md` hardening item #5 |
| `dossiers.csv` schema (RBAC, retention) | `06_reference_script/test_corpus/dossiers.csv` headers |
| Production hardening list | `06_reference_script/notes.md` "Production hardening checklist" §1–§8 |
| LGPD article references | Lei nº 13.709/2018 (public law, no URL anchor needed) |
