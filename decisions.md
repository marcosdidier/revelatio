# Decisions Log — Project Revelatio

One-line ADRs (Architecture Decision Records). Newest at the top. Format: `[YYYY-MM-DD] decision — rationale`.

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
