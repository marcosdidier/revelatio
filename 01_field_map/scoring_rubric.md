# Scoring Rubric — How we grade each tool against the gold

> **Why this file exists:** in Epic 5 we run the same PDF through ≥ 6 tools (including the chosen primary, Power Automate, plus its Azure DI cross-validator) and get back wildly different outputs. Without a rubric, "which tool won?" is a vibes contest. With this rubric, it's a number we can put in a table, defend in the relatório (§4 "Qual ferramenta faz mais sentido"), and show in the video. It also forces us to commit to the metric *before* we see the outputs — a bias check against quietly tilting the verdict toward whichever tool we already wanted to pick.

> **Where it's used:** Epic 5.9 fills `04_experiments/scoreboard.md`; Epic 7 cites it as evidence; Epic 8.1 §4 references it; Epic 9 shows the resulting table on the matrix slide.

---

## Scoring per field

For each field in `gold_truth.json`:

| Result | Score | Rule |
|---|---|---|
| **Exact** | 1.0 | After normalization, tool's value == gold |
| **Partial** | 0.5 | Substring match, or correct after light cleanup (one extra word, missing accent, one digit transposition that still keeps the format) |
| **Miss** | 0.0 | Field absent or value materially wrong |
| **Hallucination penalty** | −0.5 | Tool returned a confident value for a field that **doesn't exist** in the PDF — applied **once per hallucinated field**. Encodes our preference: a tool that admits ignorance > a tool that invents plausible-but-wrong values. (For a cobrança team, a hallucinated CPF means calling the wrong person.) |

## Field weights

Most fields weight = **1**. Two fields weight = **2** (downstream join keys; an error here corrupts every record):

| Field | Weight | Why |
|---|---|---|
| `cpf` | **2** | Primary identifier; mandatory join key with bank's records; CPF errors block cobrança operations entirely |
| `contract_number` | **2** | Primary debt-record key; one-to-many with future installments; wrong here = wrong debt referenced |
| (all others) | 1 | |

Total weight across the 34 fields = **36 weight points** (32 × 1 + 2 × 2).

## Normalization (applied to BOTH gold and tool output before comparison)

| Field type | Rule |
|---|---|
| CPF | Strip dots, dashes, spaces; lowercase; compare 11 digits. (`123.456.789-09` ↔ `12345678909` are equal.) |
| Phone | Strip non-digits; compare last 10–11 digits. |
| Postal (CEP) | Strip dashes; compare 8 digits. |
| Currency | Strip "R$", spaces, thousand-separators; convert "," → "."; compare as Decimal. |
| Dates | Parse to ISO `YYYY-MM-DD` (handle `DD/MM/YYYY`, `MM/YYYY`); compare as date. |
| Days overdue | Strip " dias"; compare as int. |
| Free text (name, address, status, owner) | Strip extra spaces; case-insensitive; remove trailing punctuation; treat unicode-equivalent forms (`ã` ↔ `a~`) as equal. |
| Boleto barcode | Strip spaces; compare digit-only string. |
| Bool (paid stamp) | Compare as bool; "true"/"yes"/"sim"/"PAGO" all → true. |

## Subscores reported per tool

Each tool's row in the scoreboard reports five numbers:

1. **Page-1 score** — out of 18 weight points (16 fields, 2 weighted ×2)
2. **Page-2 score** — out of 18 weight points (16 fields × 1, plus 2 free for the cross-checks if the tool surfaces them)
3. **Hallucination count** — invented fields/values; reported separately as a quality signal
4. **Latency** — wall-clock seconds end-to-end on the example PDF (and avg over 4 random synthetic PDFs)
5. **Cost class** — free / <$0.001 / <$0.01 / <$0.10 / >$0.10 per PDF

## Aggregate score

`overall = (page1_score + page2_score) / 36 × 100`, then a one-line judgment:

| Range | Verdict |
|---|---|
| ≥ 95 | Production-ready as primary extractor |
| 85–94 | Production-ready with HITL on flagged rows |
| 70–84 | Useful as one stage of a hybrid pipeline |
| 50–69 | Marginal; cite as a baseline only |
| < 50 | Not recommended for this use case |

## Tie-breakers (when two tools score within 3 points)

1. Lower hallucination count wins
2. Better LGPD posture wins (self-host > BR-region cloud > generic-region cloud > consumer LLM)
3. Lower cost class wins
4. Lower latency wins

This ordering encodes the firm's values: "we'll trade a couple of points of accuracy for a tool that doesn't lie to us *and* keeps the data in Brazil."

## How to fill it in (Epic 5 procedure)

1. Run tool on `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf`.
2. Copy `score_template.csv` to `04_experiments/<NN>_<tool>/score.csv`.
3. For each row, paste the tool's value into `tool_value`.
4. Apply normalization rules → mark `result` as exact / partial / miss / hallucination.
5. Compute `score = result_score × weight`.
6. Sum and divide by 36 → push to `scoreboard.md`.
7. Optional: re-run on 4 random synthetic PDFs for the latency/avg-accuracy numbers.
