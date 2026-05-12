# Epic 5.7 — Azure Document Intelligence (Layout) hands-on

**Date**: 2026-05-10
**Resource**: `di-revelatio-test` (East US, F0/free tier)
**Subscription**: Azure Free Trial ($200 credit, personal MS account — see SESSION_RESUME for why M365 admin signup failed with CNPJ requirement)
**Model**: `prebuilt-layout` (API 2024-11-30, 4.0 GA)
**Input**: `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf` (the PDF Power Automate hallucinated on)
**Output**: `output.json` (~10.5k lines, full Layout response)

## Method

1. Provisioned Document Intelligence resource via Azure Portal (F0 free tier, 500 Layout pages/month free).
2. Opened Document Intelligence Studio (`contentunderstanding.ai.azure.com`).
3. Configured studio with `di-revelatio-test` resource (Access By → Resource, not key paste).
4. Uploaded brief PDF, ran Layout analysis.
5. Inspected Content tab (Text + Tables + Selection marks + Figures).
6. Downloaded full JSON.

## Results

### Page 1 — table structure (zero-shot)

Two tables auto-detected with correct Campo/Informação column structure:

| Table | Rows | Field-value pairs extracted |
|---|---|---|
| Identificação do Cliente | 7 | Nome, CPF, Data nasc., Telefone, E-mail, Endereço, CEP |
| Informações da Dívida | 9 | Contrato, Produto, Data contr., Valor orig., Saldo atual., Dias atraso, Status, Última tent., Responsável |

All 16 page-1 fields extracted correctly. No training. No labeling. Same result Power Automate + AI Builder achieved only after explicit training on a synthetic corpus.

### Page 2 — paragraph structure (the key test)

Every comprovante field detected as a discrete paragraph with label intact:

- `Titular: Maria Almeida Costa`
- `Endereço: Rua das Laranjeiras, 145, Apto 302`
- `Bairro: Boa Vista - Recife/PE`
- `CEP: 50050-120`
- `Referência: Conta de energia - Companhia Ficticia de Energia`
- `Mês/Ano: 03/2026`
- `Valor: R$ 184,72`
- `Código de barras: 34191.79001 01043.510047 91020.150008 1 99990000018472`
- Banking: `Banco: Banco Exemplo S.A.`, `Agência: 1234 | Conta: 00098765-4`, `Data: 18/03/2026`, `Tipo: Pagamento parcial de acordo`, `Pagador / Recebedor`, `Valor pago: R$ 750,00`, `Autenticação: BX26.03.18.00045.99871.FICT`
- `PAGO` stamp detected as its own paragraph element

**No footer hallucinations. No pagination-as-field-value bug.** This is the failure mode AI Builder exhibited on the same PDF — and Azure DI Layout, with zero training, did not exhibit it.

## Strategic findings

1. **The PA page-2 hallucination problem is NOT a property of Azure's OCR.** It is a property of AI Builder's template-matching behavior when fed an out-of-distribution layout. Azure DI Layout's structure recognition handles the layout drift cleanly.

2. **Layout returns text + tables + paragraphs, but NOT key-value pairs for unstructured paragraph data.** To get structured page-2 extraction, you need a downstream step:
   - **LLM on top** (canonical production pattern — Azure Layout for clean text, Claude/GPT for field mapping)
   - **Custom Neural** (Azure DI's trainable model — but requires ~30–100 labeled real Banco X dossiers)
   - **Custom Template** (only works for fixed-layout docs)

3. **Cost class**: Layout = $1.50 per 1,000 pages (S0 tier; free tier covers 500 pages/month). At 10k dossiers × 2 pages = 20k pages = ~$30/month for OCR alone. LLM call on top adds ~$50. **~$80 total for 10k dossiers**, well under any commercial alternative.

4. **Region selection matters**: East US has the broadest model availability. Brazil South lacks several prebuilt models — for production deployment, recommend East US as primary region (with the obvious LGPD trade-off documented in Epic 7).

## Production architecture implication

The empirically-validated production stack for non-M365 firms:

```
PDF
  → Azure DI Layout (deterministic OCR + table + paragraph structure)
  → Page 1: parse tables directly from Layout JSON (no LLM needed)
  → Page 2: send paragraph text to LLM (Claude/GPT) with field schema
  → Cross-validate (name consistency: page-2 Titular and Pagador match page-1 client_name; CPF passed as prompt context but absent from page-2 layout)
  → Output: CSV row + audit log + HITL queue for low-confidence
```

This is what Epic 6 (`reference Python script`) will implement.

## Methodological caveats for relatório §3

- Tested on **n=1** real-shape document (the brief example PDF). Production deployment requires validation on a real Banco X sample of 30–100 dossiers.
- We did **not** test Custom Neural (requires ~30 min training time + 5+ labeled docs, out of scope for this evaluation window).
- Studio UI testing measured **end-to-end including upload + studio rendering**, not pure API latency. For production, expect ~2–4s per dossier via direct API.
