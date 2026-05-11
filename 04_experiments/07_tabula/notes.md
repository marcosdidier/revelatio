# Epic 5.8 — Tabula hands-on

**Date**: 2026-05-10
**Tool**: tabula-py 2.10.0 (Python wrapper around Tabula Java jar)
**Runtime**: Java 24, Python 3.13 (project `.venv`)
**Method**: `04_experiments/07_tabula/run_tabula.py` (stream mode, multiple_tables=True)
**Inputs tested**: brief example PDF, F01 (perfect synthetic), F07 (skewed page 2)

## Why this experiment exists

Empirical OSS data point for the relatório. Tabula represents the free deterministic-PDF-table-extraction class (alongside pdfplumber, PyPDF2, etc.). Predicted result: page-1 table extraction works, page-2 image content fails entirely (Tabula has no OCR).

## Results

| PDF | Page 1 tables | Page 1 cells | Page 2 tables | Page 2 cells | Latency p1 | Latency p2 |
|---|---|---|---|---|---|---|
| brief | 2 | 32 | 0 | 0 | 1.79s | 0.81s |
| F01 perfect | 2 | 32 | 0 | 0 | 0.78s | 0.81s |
| F07 skewed page 2 | 2 | 32 | 0 | 0 | 0.71s | 0.86s |

### Page 1 — brief PDF extraction (full output)

**Table 1 — Identificação do Cliente** (7 rows, all correct):
```
Campo,Informacao
Nome completo,Maria Almeida Costa
CPF,123.456.789-09 (ficticio)
Data de nascimento,14/08/1983
Telefone,(81) 98888-1122
E-mail,maria.costa.exemplo@emailficticio.com
Endereco,"Rua das Laranjeiras, 145, Apto 302 - Boa Vista - Recife/PE"
CEP,50050-120
```

**Table 2 — Informações da Dívida** (9 rows, all correct):
```
Campo,Informacao
Contrato,BX-2024-0004587
Produto,Emprestimo pessoal
Data de contratacao,12/02/2024
Valor original,"R$ 18.450,00"
Saldo atualizado,"R$ 22.780,35"
Dias em atraso,147 dias
Status interno,Em negociacao
Ultima tentativa de contato,25/04/2026
Responsavel interno,Equipe Cobranca - Nucleo 03
```

### Page 2 — universal failure

Zero tables, zero cells, no error raised — Tabula simply finds no extractable text streams on image-embedded pages. F07 (skewed) behaves the same as F01 (perfect) and brief, confirming this is a class-level failure mode (no OCR), not a layout issue.

## Strategic findings

1. **For page-1 extraction, Tabula matches commercial tools at zero cost.** Identical 16/16 field-value extraction as Azure DI Layout, ~7× faster (0.7s vs ~5s for Azure round-trip), no API key, no cost. Genuine OSS win on the table-structured portion.

2. **For full dossier extraction, Tabula is unusable alone.** Page-2 image content is invisible to it. Any OCR-free approach (Tabula, pdfplumber, PyPDF2) will hit this exact wall — this is a **class-level finding**, not Tabula-specific.

3. **Cost-optimal hybrid emerges**:
   - **Page 1**: Tabula or pdfplumber (free, deterministic, fast)
   - **Page 2**: Azure DI Layout + LLM (~$0.008/dossier)
   - **= ~$80/10k dossiers** with even higher page-1 confidence than pure Azure DI (because Tabula gives clean CSV rows without an LLM step on page 1).

4. **Production caveat — layout drift**: Tabula's stream-mode table detection is heuristic. Worked perfectly on our 3 PDFs because they share the same Campo/Informação two-column layout. Real Banco X dossiers with different page-1 layouts may need lattice mode, area constraints, or per-template tuning. **Not a free lunch in production**.

## Relatório positioning

Tabula belongs in the "evaluated alternatives" section as **the cheapest viable page-1 component**, with the explicit caveat that it is **not a complete solution**. The empirical observation (16/16 page-1 cells correct, 0/0 page-2 cells) is the single cleanest piece of evidence for the relatório's core argument:

> *"Free deterministic tools handle clean tabular page 1; image-embedded content requires OCR + AI. This is why the recommended architecture is a hybrid stack, not a single-tool solution."*

## Artifacts

- `run_tabula.py` — reproducible test script
- `brief_page1_table1.csv` / `brief_page1_table2.csv` — extracted page-1 tables
- `F01_page1_table{1,2}.csv` / `F07_page1_table{1,2}.csv` — synthetic stress tests
