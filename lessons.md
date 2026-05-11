# Lessons — Project Revelatio

Per the user's global CLAUDE.md rule: capture patterns from corrections, write rules-for-self that prevent repeats, and review at session start.

Format: `[YYYY-MM-DD] short title — pattern observed → rule for self`.

---

- **[2026-05-08] Explain-purpose-before-writing-non-trivial-artifacts** — when I batched the scoring rubric write into a sequence of related files, the user accepted the structure but pushed back: *"I like the structure but I didn't understand the reason of the doc, explain"*. The structure was fine; the missing piece was a "why this artifact exists" framing **before** writing it.
  → **Rule for self**: for any artifact whose purpose isn't obvious from its filename (rubric, schema, playbook, ADR, anything novel-named), state in 2–3 sentences *what problem it solves and where it gets used downstream* **before** writing the file. Lightweight artifacts (READMEs, simple JSON, things with obvious names like `field_map.md`) can skip this. Cost of a 30-second framing is small; cost of a misaligned 200-line doc is large.

- **[2026-05-08] Propagate-strategic-choices-immediately-across-all-artifacts** — partway through writing tool dossiers, the user pivoted from "Azure DI primary" to "Power Automate primary" and added: *"make sure all the codebase reflects this choice"*. I had three rejections in a single batch because earlier-written dossiers already implied a different primary tool and the comparison matrix was about to inherit the wrong ranking.
  → **Rule for self**: when the user changes a strategic decision mid-execution, **stop**, acknowledge the pivot in 1 paragraph (with reasoning the user can validate), enumerate **every** artifact that needs to update, then write all changes in **one batch**. Never leave the codebase half-pivoted across turns. Add a fresh ADR to `decisions.md` capturing the pivot + reasoning so the audit trail is intact.

- **[2026-05-08] User values pragmatic real-world fit over technical purity** — the Power Automate pivot was driven by reasoning the user articulated: brief-listed tool + likely-existing M365 stack at a Brazilian law firm + AI Builder is built on Azure DI under the hood (so we get the proxy-testing argument for free).
  → **Rule for self**: when recommending tools/architectures for this project, weight `[Diff:UsoReal]` (real-world office fit) heavily. Default to brief-listed tools that match the customer's likely existing stack, unless benchmark evidence forces otherwise. Don't reach for unlisted "best" tools just to look proactive.
