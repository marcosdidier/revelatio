# Decisions Log — Project Revelatio

One-line ADRs (Architecture Decision Records). Newest at the top. Format: `[YYYY-MM-DD] decision — rationale`.

## 2026-05-12 — D-007: reference engine exposed publicly via Streamlit Community Cloud + Google Sheets write-back

- **D-007 — The reference engine (D-006) is exposed publicly at `https://revelatio-demo.streamlit.app` via Streamlit Community Cloud, with an opt-in Google Sheets write-back as a shared demo sink for the hiring panel.** Same engine as D-006 (`06_reference_script/extract_dossier.process_one`); the deployment is a presentation + delivery layer, not an algorithmic change. *Why:*
  - **Strengthens "Capacidade de implementação" evidence (brief §1)**: the panel can click a real URL and exercise the engine on their own PDFs, not just watch a localhost recording. Strictly stronger artifact than the original "run `streamlit run` locally" demo posture.
  - **Single-tenant demo, single-service auth**: service-account JSON in Streamlit Cloud secrets (gspread + google-auth, scoped to `spreadsheets` only — not `drive`). No OAuth flow, no per-user state. Appropriate for a take-home demo, not a multi-tenant production app.
  - **PT-BR presentation labels**: UI dataframe, CSV download header, and Google Sheet header all use PT-BR via `06_reference_script/labels_pt.py`. Pipeline dict keys remain in English so `process_one()` and the rest of the codebase are unaffected.
  - **Production gaps honestly preserved**: the deployed app is a demo skin — no SSO, no per-field HITL review workflow, no rate limiting on the public URL. Production hardening checklist in `06_reference_script/notes.md` item #6 still applies; Diagram 2 in `07_architecture/diagrams.md` retains the pink-dashed HITL annotation.
  - **Repo public for transparency**: source at `https://github.com/marcosdidier/revelatio`. Public repo is a feature for a take-home, not a leak — and a hard requirement for Streamlit Community Cloud's free tier.

## 2026-05-12 — D-006 supersedes D-005: reference Python engine becomes the primary recommendation

- **D-006 — Primary recommended solution: the Python reference engine in `06_reference_script/` (Azure DI Layout + Claude Sonnet 4.6 with Option-B cross-validation), orchestrated in production by n8n.** Supersedes D-005 (which had Power Automate as primary) without invalidating its findings — Power Automate + AI Builder is reclassified as the *caminho alternativo* for firms already resident in Microsoft 365 that prefer no-code maintenance. *Why the flip*:
  - **What we built vs. what we recommended**: D-005 nominated Power Automate as primary, but the *complete* hybrid stack (page-1 deterministic + page-2 Azure DI Layout + Claude API field-mapping + cross-validation gate + HITL routing) was built and validated empirically as a Python pipeline in Epic 6, **not** inside Power Automate. The PA flow demonstrates page-1 (AI Builder) but the page-2 fallback layer that fixes the OOD failure was specified, not implemented inside PA.
  - **Empirical validation strengthened**: the Python engine scores **100% on a 3-PDF baseline corpus + 100% on the OOD holdout F09_brief_shape** (brief-faithful layout, completely new client data). 0 hallucinations across all 4 PDFs. Cost $0,00934 / dossier = $93,37 / 10k = R$ 457 at PTAX 4,8999. Leading with the artifact that has measured numbers is more defensible than leading with one whose recommended completion is unbuilt.
  - **Brief diferencial alignment**: the brief explicitly bonuses "criar um script básico" (`[Diff:Script]`) and "fluxo alternativo de automação" (`[Diff:AltFlow]`). With D-006, the script *is* the recommendation, and the alternative flow is a real architectural variant (M365), not a fallback narrative.
  - **n8n role disclosed honestly**: n8n is the recommended production orchestrator in the non-M365 path but was **not built** in the PoC (Epic 5.10 was deliberately skipped); the CLI in `extract_dossier.py` is the orchestrator we tested. This honesty is required by D-006's framing.
  - **M365 path remains a real recommendation** for M365-resident firms; the value of paralegal-maintainable no-code is real and the PA flow demonstrates the page-1 layer plus the architectural shape. Firms choose by the rubric in `07_architecture/diagrams.md` §5.

## 2026-05-08 — Strategic pivot to Power Automate as primary recommendation

- **D-005 — Primary recommended solution: Microsoft Power Automate + AI Builder Document Processing, validated hands-on in Epic 5.2.** *Why:*
  - Brief-listed tool — low risk pick aligned with the hirer's expectations.
  - Likely match for the firm's existing stack — most Brazilian law firms operate on M365; Power Automate slots into that ecosystem with native Excel/SharePoint integration, no new platform to onboard.
  - End-to-end inside one platform: AI Builder extracts → Power Automate orchestrates → Excel Online writes the spreadsheet → Approvals + SharePoint handle HITL.
  - **AI Builder Document Processing is built on the same Azure Document Intelligence engine** we also benchmark hands-on in Epic 5.7 → testing both Power Automate (5.2) AND Azure DI (5.7) gives us **two angles cross-validating the same extraction layer**. Stronger evidence than either alone.
  - Non-technical maintenance: legal-ops lead can edit a Power Automate flow without engineering resourcing.
  - Microsoft offers Brazilian data residency configurations under M365 commercial data protection.
  - LGPD posture is acceptable (BR region + tenant controls + DPA).
- **D-004 (UPDATED) — M365 access provisioned within deadline window**: user will provision M365 Business Basic 30-day trial + Power Automate Premium trial + AI Builder credits trial via admin center for the hands-on test in Epic 5.2. Provisioning is fast (instant signup + ~5 min Dataverse + ~10 min AI Builder setup); custom Document Processing model training takes ~10–30 min on the synthetic corpus. Total time investment: ~2–3 hours, fitting in the Day 3 morning slot.

## 2026-05-07 — Initial decisions (locked in via Q&A with planning AI)

- **D-001 — Deliverable language: PT-BR** for the final relatório, video, and recommendation doc; backlog and internal artifacts stay in EN. *Why:* matches the firm's language and the brief itself; signals cultural fit without doubling the writing budget.
- **D-002 — Approve ~US$5–20 budget** for Document AI API testing (Azure Document Intelligence primarily, optionally AWS Textract or Google Document AI for comparison). *Why:* the brief explicitly rewards an unlisted tool; running a real benchmark instead of citing docs is the strongest possible signal. **Note (post-D-005)**: Azure DI testing is now reframed as the *proxy test* for Power Automate's extraction engine, in addition to its standalone differential value.
- **D-003 — Generate 5–10 synthetic PDFs** that mimic the example structure with controlled variations. *Why:* n=1 is too weak to defend a 10k-scale recommendation; controlled variations (missing fields, OCR-noise on page 2, alternate field labels) let us prove robustness in the video demo.

## Architecture working hypothesis (validated/refined as we go)

- **WH-001 — Two-layer routing**: Page 1 (digital text) → deterministic parser like `pdfplumber` (or AI Builder's text extraction). Page 2 (image-based comprovantes) → OCR + field extraction via AI Builder Document Processing in production; Azure DI in our hands-on test. Avoid sending page 1 through a vision LLM at 10k scale — it's wasted spend on already-machine-readable text.
- **WH-002 — Hybrid orchestration**: **Power Automate** for the production pipeline IF firm is on M365 (D-005). **n8n self-hosted + Python script (Epic 6)** as the **alternative flow** if firm is not on M365. LLM/Doc-AI calls only as the OCR/extraction step, not as the orchestrator. Keeps cost predictable and the data flow auditable.
- **WH-003 — Human-in-the-loop gate**: any row whose extraction confidence falls below a threshold (e.g., 0.85 mean field confidence) is flagged into a review queue. At 10k records, even 5% review rate = 500 manual checks — still a 95% headcount reduction vs the current 10-people-for-days baseline. Power Automate's "Manual approval" connector + a SharePoint review list is the production HITL surface.
