# Field Map — example PDF → Excel columns

> Source PDF: `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` (2 pages, structure: page 1 digital text in tables, page 2 image-based comprovantes).
> Goal: trace **every** extractable value to its location, format, and recommended extraction strategy. This is the contract for `01_field_map/gold_truth.json` and the reference for `06_reference_script/page1_parser.py` and `page2_parser.py`.

## Page 1 — Identificação do Cliente + Informações da Dívida

Layer: **digital text in 2-column tables**. No OCR needed. Strategy: `pdfplumber.extract_tables()` then key-value lookup by left-column anchor.

| # | Campo (PT) | Field (EN) | Anchor (left col) | Sample value | Format pattern | Extraction strategy | Required? |
|---|---|---|---|---|---|---|---|
| 1 | Nome completo | client_name | `Nome completo` | Maria Almeida Costa | `[\p{L}\s]+` | table cell right of anchor | ✅ brief |
| 2 | CPF | cpf | `CPF` | 123.456.789-09 | `\d{3}\.\d{3}\.\d{3}-\d{2}` | regex on table cell; strip "(fictício)" suffix | ✅ brief |
| 3 | Data de nascimento | birth_date | `Data de nascimento` | 14/08/1983 | `\d{2}/\d{2}/\d{4}` | direct | bonus |
| 4 | Telefone | phone | `Telefone` | (81) 98888-1122 | `\(\d{2}\)\s?\d{4,5}-\d{4}` | direct | ✅ brief |
| 5 | E-mail | email | `E-mail` | maria.costa.exemplo@emailficticio.com | RFC 5322 simple | direct | ✅ brief |
| 6 | Endereço | address | `Endereço` | Rua das Laranjeiras, 145, Apto 302 - Boa Vista - Recife/PE | free text | direct | ✅ brief |
| 7 | CEP | postal_code | `CEP` | 50050-120 | `\d{5}-\d{3}` | direct | bonus |
| 8 | Contrato | contract_number | `Contrato` | BX-2024-0004587 | `[A-Z]{2}-\d{4}-\d{7}` | direct (key field — **weight 2x** in scoring) | ✅ brief |
| 9 | Produto | product | `Produto` | Empréstimo pessoal | free text | direct | ✅ brief |
| 10 | Data de contratação | contract_date | `Data de contratação` | 12/02/2024 | `\d{2}/\d{2}/\d{4}` | direct | bonus |
| 11 | Valor original | original_amount | `Valor original` | R$ 18.450,00 | `R\$\s?[\d\.]+,\d{2}` | normalize to `Decimal("18450.00")` | ✅ brief |
| 12 | Saldo atualizado | updated_balance | `Saldo atualizado` | R$ 22.780,35 | same | normalize to Decimal | ✅ brief |
| 13 | Dias em atraso | days_overdue | `Dias em atraso` | 147 dias | `\d+\s*dias?` | extract int; sanity check ≥ 0 | ✅ brief |
| 14 | Status interno | status | `Status interno` | Em negociação | controlled vocabulary likely | direct; build set as we see more PDFs | ✅ brief |
| 15 | Última tentativa de contato | last_contact_attempt | `Última tentativa de contato` | 25/04/2026 | date | direct | ✅ brief |
| 16 | Responsável interno | internal_owner | `Responsável interno` | Equipe Cobrança - Núcleo 03 | free text | direct | ✅ brief |

**13 brief-required + 3 bonus = 16 page-1 fields**.

### Page-1 anchors that are not data (skip)

- "Documento ficticio para teste tecnico - nao utilizar como documento real Pagina 1" (header)
- "BANCO X - DOSSIÊ DE CLIENTE DEVEDOR" (title)
- "1. Identificação do Cliente" / "2. Informações da Dívida" (section headings)
- "3. Dados a serem extraidos para planilha" + "4. Observações" (meta-instructions in the example only — likely absent in production PDFs; safe to ignore)

## Page 2 — Anexos do Cliente (Comprovantes — image OCR required)

Layer: **rasterized image** of two boxed receipts. OCR + field extraction. Strategy: Document AI service (Azure DI / AWS Textract / GCP Doc AI) OR vision-LLM (Claude/GPT-5/Gemini) with structured output. Tabula will return nothing here (we'll demonstrate that in 5.4).

### 2.A — Comprovante de Endereço

| # | Campo (PT) | Field (EN) | Anchor | Sample value | Format pattern | Notes |
|---|---|---|---|---|---|---|
| 17 | Titular | proof_address_holder | `Titular:` | Maria Almeida Costa | name | should match field #1 — **cross-validation opportunity** |
| 18 | Endereço (comprovante) | proof_address_line | `Endereço:` | Rua das Laranjeiras, 145, Apto 302 | free text | should match field #6 prefix — **cross-validation** |
| 19 | Bairro/Cidade/UF | proof_address_neighborhood | `Bairro:` | Boa Vista - Recife/PE | `bairro - cidade/UF` | join key for #6 suffix |
| 20 | CEP | proof_address_postal | `CEP:` | 50050-120 | `\d{5}-\d{3}` | should match #7 |
| 21 | Referência | proof_reference | `Referência:` | Conta de energia - Companhia Fictícia de Energia | free text | identifies the bill type |
| 22 | Mês/Ano | proof_period | `Mês/Ano:` | 03/2026 | `MM/YYYY` | for staleness check (≤ 90 dias regra geral) |
| 23 | Valor | proof_value | `Valor:` | R$ 184,72 | currency | normalize to Decimal |
| 24 | Código de barras | proof_barcode | `Código de barras:` | 34191.79001 01043.510047 91020.150008 1 99990000018472 | boleto 47-digit pattern | strip spaces; **could decode boleto** for vencimento + valor cross-check |

### 2.B — Comprovante Bancário

| # | Campo (PT) | Field (EN) | Anchor | Sample value | Format pattern | Notes |
|---|---|---|---|---|---|---|
| 25 | Banco | bank_name | `Banco:` | Banco Exemplo S.A. | free text | |
| 26 | Agência | bank_branch | `Agência:` | 1234 | `\d{3,5}` | |
| 27 | Conta | bank_account | `Conta:` | 00098765-4 | `\d+-\d{1}` | |
| 28 | Data da transação | transaction_date | `Data da transação:` | 18/03/2026 | date | |
| 29 | Tipo | transaction_type | `Tipo:` | Pagamento parcial de acordo | free text | controlled vocabulary likely |
| 30 | Pagador | payer | `Pagador:` | Maria Almeida Costa | name | should match #1 — **cross-validation** |
| 31 | Recebedor | payee | `Recebedor:` | Banco X - Carteira de Cobrança | free text | |
| 32 | Valor pago | amount_paid | `Valor pago:` | R$ 750,00 | currency | normalize to Decimal |
| 33 | Autenticação | authentication_code | `Autenticação:` | BX26.03.18.00045.99871.FICT | bank-specific | unique per transaction |
| 34 | Carimbo "PAGO" | paid_stamp_present | (visual circle) | true | bool | vision-only signal; OCR may catch the word |

**18 page-2 fields total**.

## Aggregate

- Total fields cataloged: **34** (13 brief-required + 3 bonus on page 1; 18 on page 2 attachments).
- **Cross-validation pairs**: (#1 ↔ #17 ↔ #30) name; (#6 ↔ #18) address line; (#7 ↔ #20) CEP. The script (Epic 6.5) will use mismatches as a confidence-lowering signal.
- **Highest-weight fields for scoring**: CPF (#2) and Contrato (#8) — these are the join keys downstream; weight 2× in `scoring_rubric.md`.
- **Fields most likely to fail** on bad scans: #24 (código de barras — long digit string), #33 (autenticação — alphanumeric), #34 (visual stamp).

## Notes for production scale

- Some axes of variation we should be ready for (and that `05_synthetic_data/` will exercise):
  - Multi-debt clients: more than one Contrato per PDF → list-of-debts schema
  - Missing email or phone (contact gaps are common in cobrança data)
  - CPF written without separators (`12345678909`) or with masked digits (`***.***.789-09`)
  - Bad-quality scans on page 2 (skewed, low DPI, printer streaks)
  - Alternate field labels ("Nome:" vs "Nome completo:")
