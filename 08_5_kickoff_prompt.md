# Epic 8.5 — Kickoff Prompt (paste into a fresh Claude Code session)

> **Use**: open Claude Code in `/Users/marcosdidier/testeRevelatio/` in a new conversation. Paste the block under "## The prompt" verbatim as the first message. The rest of this file is context for *you* (the human) — not part of the paste.

> **Why this exists between Epic 8 and Epic 9**: the relatório (Epic 8) describes a recommended architecture; the video (Epic 9) demos it. Until now the demo would have been a recording of `app.py` running locally on the candidate's laptop. Deploying `app.py` to a public URL with Google Sheets write-back turns that into a *real link the panel can click and exercise themselves* — strictly stronger evidence of "Capacidade de implementação" (brief §1).

---

## The prompt

```
Continue Project Revelatio. Read SESSION_RESUME.md and 08_5_kickoff_prompt.md
first — they have the complete status and the Epic 8.5 specification.

Where we are: Epics 0–8 are done. The relatório PT-BR is at
08_deliverables/relatorio.md (+ relatorio.pdf). The reference Python
pipeline at 06_reference_script/ is the primary recommendation (D-006),
empirically validated at 100% on a 3-PDF baseline + OOD holdout
(F09_brief_shape) with 0 hallucinations and $0.00934 per dossier.
Streamlit demo `app.py` exists but runs locally only.

What I'm starting today: Epic 8.5 — Deploy the Streamlit demo to a
public URL AND add a "write to Google Sheets" button so the result of
every extraction is appended into a configured spreadsheet that the
hiring panel can click into. Target platform: Streamlit Community Cloud
(share.streamlit.io). Target auth for Sheets: Google Cloud service
account (the cleanest path for a single-tenant demo).

Scope:
  - Add a Sheets writer module that the demo invokes after a successful
    extraction.
  - Make app.py read secrets from both st.secrets (Streamlit Cloud) and
    .env (local) without breaking local dev.
  - Pin runtime deps in a top-level requirements.txt that Streamlit
    Cloud can install.
  - Document the deploy steps in DEPLOY.md so the user can execute the
    parts only a human can do (Google Cloud project, service account
    JSON, GitHub push, Streamlit Cloud "New app", secrets config).

Out of scope:
  - DO NOT change the relatório, SCOREBOARD, diagrams, ROI, or any
    Epic 7 docs to claim "we deployed" until the live URL is verified
    end-to-end. The relatório's current "we built the engine, didn't
    build the orchestration" posture is the methodologically clean
    fallback if deploy fails.
  - DO NOT introduce n8n or any orchestrator. Streamlit's built-in
    upload + button UI is the orchestration layer for this demo.
  - DO NOT push the repo or create accounts on behalf of the user —
    surface those as explicit user action items in DEPLOY.md.

Pacing for today: structured planning, then code, then I do the human-
only setup steps (Google Cloud + GitHub + Streamlit Cloud) following
DEPLOY.md, then we smoke-test the URL together.

Start by: entering plan mode, reading 06_reference_script/app.py and
06_reference_script/extract_dossier.py (the modules being wrapped),
checking .gitignore (already excludes .env — good) and .env.example
(template to extend), and proposing the file-change set with a clear
list of (a) what files to create/modify and (b) what manual steps the
user has to do. Don't start writing code until I approve the outline.

There are three open questions to raise via AskUserQuestion before
finalizing the outline — they're listed in 08_5_kickoff_prompt.md
under "Open questions for the user". Get answers, then plan.
```

---

## Context for the human (you)

### What's done (don't redo)

| Epic | Deliverable | Where |
|---|---|---|
| 0–7 | Setup, ground truth, tool universe, external research, synthetic PDFs + golds, hands-on tool tests, SCOREBOARD, reference Python pipeline, Streamlit demo `app.py`, architecture/LGPD/ROI docs | various |
| 8 | Relatório PT-BR + PDF | `08_deliverables/relatorio.md` + `relatorio.pdf` |
| **8.5 (this epic)** | **Public URL + Sheets write-back** | NEW |
| 9 (pending) | Video PT-BR ≤ 5 min | `09_video/` + `09_kickoff_prompt.md` |
| 10 (pending) | QA + bundle + submit | `10_submission/` (not yet created) |

### Files this epic will create / modify (rough outline — let the planning agent confirm)

| File | Status | Purpose |
|---|---|---|
| `06_reference_script/sheets_writer.py` | NEW | `append_dossiers(rows, columns, sheet_id, worksheet_name)` using `gspread` + a service-account JSON loaded from env |
| `06_reference_script/app.py` | MODIFY | (a) bridge `st.secrets` → `os.environ` at startup so libs see the same vars locally and on Cloud; (b) add a "📤 Enviar para Planilha Google" button after the CSV download; (c) display the sheet URL on success |
| `requirements.txt` | NEW (repo root) | Pinned deps for Streamlit Cloud: `streamlit`, `anthropic`, `python-dotenv`, `azure-ai-documentintelligence`, `gspread`, `google-auth` |
| `.env.example` | MODIFY | Add `GOOGLE_SHEET_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON` to the documented template |
| `DEPLOY.md` | NEW (repo root) | Step-by-step instructions for the user (Google Cloud project + service account + JSON key download, Google Sheet creation + share, GitHub repo + push, Streamlit Cloud "New app" + secrets in TOML) |
| `.streamlit/secrets.toml` | NOT in git | User-side only (Streamlit Cloud has its own secrets UI; for local Cloud-mode testing this lives outside git) |
| `08_deliverables/relatorio.md` etc. | **DO NOT TOUCH** in this epic | Only update after the URL is verified live. Until then, keep the relatório's "we built the engine, n8n is one option among several" framing intact |

### What the user (human) will need to do manually

These can't be automated — flag them clearly in DEPLOY.md:

1. **Google Cloud setup** (~10 min):
   - Create a new project at `console.cloud.google.com`.
   - Enable the **Google Sheets API** (search bar → "Sheets API" → Enable).
   - **IAM & Admin → Service Accounts → Create**: name `revelatio-demo` (any name fine); role `Editor` (or just sheets-specific roles if you want to be tight).
   - On the service account: **Keys → Add Key → Create new key → JSON**. Download. This is `GOOGLE_SERVICE_ACCOUNT_JSON`.
   - Note the service account email (looks like `revelatio-demo@<project-id>.iam.gserviceaccount.com`).

2. **Google Sheet setup** (~2 min):
   - Create a new Google Sheet (drive.google.com → New → Google Sheets).
   - **Share** with the service account email, role **Editor**.
   - From the URL `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`, copy `<SHEET_ID>`. This is `GOOGLE_SHEET_ID`.
   - Optional: rename the default tab `Sheet1` → `Dossiers` (or let the Sheets writer auto-create it).

3. **GitHub push** (~5 min, free):
   - `gh repo create marcosdidier/revelatio --public --source=. --remote=origin --push` (or via the GitHub UI if you prefer).
   - Public is simplest because Streamlit Community Cloud's free tier supports public repos out of the box. Private repos need a paid Streamlit plan.
   - Sanity-check: `git status` shows nothing tracked under `.env`, `.venv/`, or `__pycache__/`.

4. **Streamlit Community Cloud deploy** (~5 min, free):
   - Sign in at `share.streamlit.io` with the GitHub account.
   - **New app** → repository `marcosdidier/revelatio`, branch `main`, **main file path** `06_reference_script/app.py`.
   - Advanced settings → **Secrets** → paste TOML (template is in DEPLOY.md):
     ```toml
     ANTHROPIC_API_KEY = "sk-ant-..."
     AZURE_DI_ENDPOINT = "https://<region>.api.cognitive.microsoft.com/"
     AZURE_DI_KEY = "..."
     GOOGLE_SHEET_ID = "..."
     GOOGLE_SERVICE_ACCOUNT_JSON = """
     { ...the entire contents of the downloaded JSON key... }
     """
     ```
   - Deploy. URL will be `https://<app-name>.streamlit.app`.

5. **Smoke test** (~5 min):
   - Open the URL. Upload `05_synthetic_data/pdfs/F09_brief_shape.pdf`. Click "▶ Extrair". Verify 100% extraction. Click "📤 Enviar para Planilha Google". Confirm the row appears in the shared sheet.

### Open questions for the user (Epic 8.5 session should ask via AskUserQuestion before finalizing the outline)

1. **GitHub repo visibility**: Public (free Streamlit Cloud, simplest, the panel can read the source — a feature for a take-home) or private (requires Streamlit Cloud paid tier)?
   - *Recommendation*: Public. For a take-home submission, source transparency is a positive signal; Streamlit Cloud free tier is plenty for demo scale.

2. **Sheets append behavior**: Append-only (each upload adds new rows below existing data; sheet grows over time) or replace-on-write (each upload clears the previous extraction first)?
   - *Recommendation*: Append-only with an extra `extracted_at` timestamp column added by the writer — the panel can see multiple runs without overwriting.

3. **Cost-control on the public URL**: Add a soft cap inside `app.py` (e.g., refuse to process more than N PDFs per session, or display a warning when API spend in a single session crosses a threshold)? Public URL means a stranger could in principle burn through API credit.
   - *Recommendation*: Add a small soft cap (e.g., 5 PDFs per upload click) plus a visible disclaimer line: *"Demo: dados sintéticos apenas; uploads limitados a 5 PDFs por sessão."* Not bulletproof but signals operational awareness.

### Pacing guidance

Same as Epics 7, 8, 9 — depth + insights welcome during planning and code review; short execution updates during the actual Google Cloud / GitHub / Streamlit Cloud setup steps. The auto-memory's 5 feedback rules apply automatically.

### Estimated time

- Code (planning agent does this): ~45 min
- User setup steps (only the human can do): ~30 min wall-clock spread across the four blocks above
- Smoke test + debugging: ~30 min
- Total: ~2 hours, including a buffer for the inevitable "oh the service account didn't have permission" round-trip.

### Final gates before Epic 8.5 ships (run before considering it done)

```bash
# 1. Live URL responds and the app loads
curl -s -o /dev/null -w "%{http_code}\n" https://<app-name>.streamlit.app   # 200

# 2. A reference PDF round-trips end-to-end through the live URL
# (manual: upload F09_brief_shape, click extract, click Sheets, verify row)

# 3. The shared Google Sheet has rows
# (manual: open the sheet URL, see the appended rows + extracted_at timestamps)

# 4. Local dev still works (we didn't break the .env path)
.venv/bin/python -m streamlit run 06_reference_script/app.py   # should open localhost without error
```

### After Epic 8.5 ships — what to update across the repo

**Only after** the URL is verified working in production, propagate the new capability:

| File | Change |
|---|---|
| `SESSION_RESUME.md` | Add Epic 8.5 row to the status table; add live URL to the "Strategic angles" section |
| `08_deliverables/relatorio.md` | §5 caminho principal — replace "*o motor foi orquestrado via CLI no PoC*" framing with "*o motor é exposto via interface web hospedada em `<URL>`, com gravação automática em Google Sheets como destino de planilha; código em `06_reference_script/app.py` + `sheets_writer.py`*". Regenerate `relatorio.pdf` via `08_deliverables/generate_pdf.py` |
| `decisions.md` | Add D-007 (or whatever the next slot is — backlog.md reserved D-007 for the submission ADR; rename if needed) recording the deploy decision |
| `09_kickoff_prompt.md` | Add a line in the Act 3 demo cue sheet: *"open the live URL instead of running localhost"* — gives the video a stronger artifact to point at |
| `07_architecture/diagrams.md` | Diagram 2: the `A` node can drop the "CLI used in PoC" caveat and instead say "Streamlit hosted at `<URL>`"; the production-form HITL annotation stays |

These updates happen in a small follow-up batch (~15 min) after the URL passes the smoke test. **They do not happen during Epic 8.5 development itself** — same discipline as the rest of the project: only claim what's empirically verified.
