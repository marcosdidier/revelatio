# Shared LLM extraction prompt (used in 5.3 ChatGPT, 5.4 Claude, 5.5 NotebookLM)

> Same prompt across all three tools so the comparison is apples-to-apples.
> Paste this into each chat **after attaching `00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf`** (or in NotebookLM: after adding it as a source).

---

## The prompt

Você é um assistente de extração de dados. Extraia as informações do PDF anexo (um dossiê de cliente devedor do Banco X — 2 páginas).

Retorne **APENAS** um objeto JSON válido seguindo exatamente este schema. Sem texto antes nem depois — apenas o JSON puro.

Regras importantes:
1. Para campos **ausentes** no PDF, use `null` (NUNCA invente um valor plausível).
2. Datas devem estar no formato ISO `YYYY-MM-DD` (ou `YYYY-MM` para mês/ano).
3. Valores monetários devem ser strings decimais sem `R$` nem separadores de milhar (ex: `"18450.00"`, NÃO `"R$ 18.450,00"`).
4. CPF mantenha o formato original com pontos e traço (ex: `"123.456.789-09"`).
5. Telefone mantenha o formato original com parênteses e traço (ex: `"(81) 98888-1122"`).
6. CEP mantenha o formato `NNNNN-NNN`.
7. Para `paid_stamp_present` (carimbo "PAGO" na visual da página 2), retorne `true` ou `false`.

Schema de saída:

```json
{
  "page1": {
    "client_name": "string",
    "cpf": "string",
    "birth_date": "YYYY-MM-DD",
    "phone": "string",
    "email": "string ou null",
    "address": "string",
    "postal_code": "NNNNN-NNN",
    "contract_number": "string",
    "product": "string",
    "contract_date": "YYYY-MM-DD",
    "original_amount": "decimal string",
    "updated_balance": "decimal string",
    "days_overdue": 0,
    "status": "string",
    "last_contact_attempt": "YYYY-MM-DD",
    "internal_owner": "string"
  },
  "page2": {
    "comprovante_endereco": {
      "proof_address_holder": "string",
      "proof_address_line": "string",
      "proof_address_neighborhood": "string",
      "proof_address_postal": "NNNNN-NNN",
      "proof_reference": "string",
      "proof_period": "YYYY-MM",
      "proof_value": "decimal string",
      "proof_barcode": "digits only, no dots/spaces"
    },
    "comprovante_bancario": {
      "bank_name": "string",
      "bank_branch": "string",
      "bank_account": "string",
      "transaction_date": "YYYY-MM-DD",
      "transaction_type": "string",
      "payer": "string",
      "payee": "string",
      "amount_paid": "decimal string",
      "authentication_code": "string",
      "paid_stamp_present": true
    }
  }
}
```

Comece sua resposta com `{` e termine com `}`. Sem markdown, sem comentários, sem explicações.
