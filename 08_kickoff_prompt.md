# Epic 8 — Kickoff Prompt (paste into a fresh Claude Code session)

> **Use**: open Claude Code in `/Users/marcosdidier/testeRevelatio/` in a new conversation. Paste the block under "## The prompt" verbatim as the first message. The rest of this file is context for *you* (the human) — not part of the paste.

---

## The prompt

```
Continue Project Revelatio. Read SESSION_RESUME.md and 08_kickoff_prompt.md first
— they have the complete status and Epic 8 specification.

Where we are: Epics 0–7 are done and committed (5 commits on `main`, most recent
`1d8d791`). The reference pipeline is empirically validated at 99.07% / 0
hallucinations / $0.00886 per dossier. Epic 7 produced four stakeholder-facing
documents in `07_architecture/` (diagrams.md, roi.md, lgpd.md, manual_timing.md)
anchored to empirical artifacts and WebFetch-verified external policy URLs.

What I'm starting today: Epic 8 — Relatório PT-BR. The take-home deliverable.
The brief prescribes seven explicit sections (see `00_brief/spec_decoded.md`
§6), in this order:

  1. Ferramentas testadas
  2. O que funcionou em cada uma
  3. O que não funcionou
  4. Qual ferramenta faz mais sentido para o caso
  5. Como essa ferramenta seria utilizada no fluxo da equipe
  6. Possíveis limitações ou cuidados da solução
  7. Possível plano inicial de implementação

Most of the prose pulls from existing artifacts (mapping in
`08_kickoff_prompt.md`). The work is: structure the doc cohesively, translate
EN→PT-BR, weave in the brief's five diferenciais naturally, and make it read
as a single voice not a stitched-together summary.

Output target: a single PT-BR markdown file `08_deliverables/relatorio.md`
(later exported to PDF in Epic 10). Length: ~10–15 pages PDF equivalent
(~3000–5000 words). Style: formal-but-direct PT-BR appropriate for a Brazilian
law firm's hiring panel.

Pacing for today: depth + insights welcome (writing, not hands-on execution).
Anchor every quantitative claim to a specific artifact so a skeptical reader
can verify in under a minute — same discipline as Epic 7.

Start by: entering plan mode, reading the four 07_architecture/ docs +
SCOREBOARD.md + spec_decoded.md, and proposing the relatório's outline
(section breakdown with target word counts and source artifacts per section,
~10 min). Don't start writing PT-BR prose until I approve the outline.

There are three open questions you should raise via AskUserQuestion before
finalizing the outline — they're listed in `08_kickoff_prompt.md` under
"Open questions for the user". Get answers, then plan.
```

---

## Context for the human (you)

### What's done (don't redo)

| Epic | Deliverable | Where |
|---|---|---|
| 0 | Setup + docs discipline | repo root |
| 1 | Ground truth + scoring rubric | `01_field_map/` |
| 2 | 8 tool dossiers + comparison matrix | `02_tool_universe/` |
| 3 | External research sprint | `03_external_research/` |
| 4 | Synthetic PDFs + golds (8 fixtures) | `05_synthetic_data/` |
| 5.2–5.9 | Tool hands-on tests (PA, ChatGPT, Claude, NotebookLM, Azure DI, Tabula) + SCOREBOARD synthesis | `04_experiments/` |
| 6 | Reference Python pipeline (99.07% / 0 hallucinations / $0.0089) + Streamlit demo UI | `06_reference_script/` |
| 7 | Architecture / LGPD / ROI stakeholder docs | `07_architecture/` |

### Section-to-artifact mapping (the prose backbone)

| Relatório § | Source artifacts to pull from |
|---|---|
| §1 Ferramentas testadas | `04_experiments/SCOREBOARD.md` §1 (headline table) + per-tool `notes.md` files |
| §2 O que funcionou em cada uma | `04_experiments/SCOREBOARD.md` §2 + `06_reference_script/notes.md` empirical results |
| §3 O que não funcionou | `04_experiments/02_power_automate/notes.md` Phase 1.5 (AI Builder OOD page-2 failure) + SCOREBOARD §5 methodology caveats |
| §4 Qual ferramenta faz mais sentido | `04_experiments/SCOREBOARD.md` §3 + §6 one-paragraph PT-BR summary (already written, can be lifted) |
| §5 Como seria utilizada no fluxo | `07_architecture/diagrams.md` §1, §2, §4, §5 (M365 + non-M365 paths + HITL lifecycle + decision rubric) |
| §6 Limitações ou cuidados | `07_architecture/lgpd.md` (full doc condensed) + SCOREBOARD §5 |
| §7 Plano inicial de implementação | `07_architecture/diagrams.md` §1/§2 (architecture) + `07_architecture/roi.md` §6 (hidden costs) + §7 (payback) + `06_reference_script/notes.md` "Production hardening checklist" |

### Diferenciais to weave in (brief §5 — bonus criteria)

The brief explicitly bolds *"A busca e sugestão de ferramentas adicionais será considerada um diferencial **importante**"*. The relatório must not treat the diferenciais as a separate section — they should be woven into the prose:

| Diferencial | Where it lands in the relatório |
|---|---|
| Ferramenta não listada inicialmente | §1 or §4 — Azure DI Layout was not in the brief's tool list; surfaced via Epic 3 external research |
| Fluxo alternativo de automação | §5 — the non-M365 path (n8n + reference engine) is the explicit alternative |
| Script básico | §7 — point to `06_reference_script/` as the working artifact |
| Preocupação com escala e organização operacional | §5 HITL queue lifecycle + §6 LGPD + §7 ROI sensitivity table |
| Solução pensada para uso real | §5 decision rubric + §6 honest LGPD gaps checklist |

### What goes in the bundle (brief §8)

| Artifact | Status |
|---|---|
| Relatório PT-BR (`08_deliverables/relatorio.md` → PDF) | Epic 8 produces |
| Vídeo ≤ 5 min PT-BR | Epic 9 produces |
| Script Python (reference pipeline) | ✅ `06_reference_script/` |
| Materiais adicionais (scorecards, audit logs, scoreboard) | ✅ `04_experiments/` + `06_reference_script/test_corpus/` |
| README PT-BR at bundle top | Epic 8 secondary deliverable (extra polish per brief) |

### Open questions for the user (Epic 8 session should ask via AskUserQuestion before finalizing outline)

1. **Length target**: brief is silent on relatório length. Default proposal: ~10–15 pages PDF (3000–5000 words). Acceptable, or aim shorter/longer?

2. **Tone register**: formal-but-direct PT-BR for a hiring panel at a law firm. Specifically: do they want *first person plural* ("Avaliamos…", "Recomendamos…") which is professional-services standard, or *third person* ("Foram avaliadas…", "Recomenda-se…") which is more academic/legal? First person plural is the conventional choice for this kind of deliverable.

3. **Honesty on the synthetic-vs-real-layout caveat**: the methodology has a known limitation (the synthetic corpus shares field labels but not visual layout with real Banco X dossiers — see SCOREBOARD §5 finding #2). Place it: (a) up-front in §3 as the headline caveat, (b) end of §3 as one of several caveats, or (c) only in §6 limitações? Recommendation: (a) — putting it first builds credibility for everything after. Confirm.

### Pacing guidance

Same as Epic 7: depth + insights welcome, this is writing not execution. Anchor every quantitative claim. Don't fabricate causal narratives if numbers are surprising — ask for the artifact line first (per the auto-memory feedback rule "Don't fabricate analytical narratives").

The auto-memory's 5 feedback rules still apply in the new session — they'll load automatically.

### Estimated time

~4–6 hours of writing, possibly split across two sessions. If splitting, the natural cutpoint is between §4 (recommendation locked in) and §5 (implementation details begin).

### Final gates before Epic 8 ships (run before considering Epic 8 done)

```bash
# 1. All brief checklist items closed
grep -c '\[ \]' 00_brief/spec_decoded.md   # must equal 0
grep -c '\[~\]' 00_brief/spec_decoded.md   # must equal 0

# 2. Relatório word count in target range
wc -w 08_deliverables/relatorio.md         # target 3000–5000

# 3. Every quantitative claim has an anchor
# (manual review pass — Epic 7's anchors index pattern is the template)
```

After Epic 8 ships, Epics 9 (video) and 10 (QA + bundle + submit) remain.
