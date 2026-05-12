"""PT-BR labels for the dossier + audit columns.

Kept separate from extract_dossier.py so the pipeline stays presentation-
agnostic. Used by app.py (UI dataframe + CSV header) and sheets_writer.py
(sheet header). Internal dict keys remain in English everywhere.
"""

DOSSIER_LABELS_PT = {
    "pdf_filename": "Arquivo PDF",
    "client_name": "Nome do cliente",
    "cpf": "CPF",
    "birth_date": "Data de nascimento",
    "phone": "Telefone",
    "email": "E-mail",
    "address": "Endereço",
    "postal_code": "CEP",
    "contract_number": "Número do contrato",
    "product": "Produto",
    "contract_date": "Data de contratação",
    "original_amount": "Valor original",
    "updated_balance": "Saldo atualizado",
    "days_overdue": "Dias em atraso",
    "status": "Status",
    "last_contact_attempt": "Última tentativa de contato",
    "internal_owner": "Responsável interno",
    "proof_address_holder": "Comprovante — titular",
    "proof_address_line": "Comprovante — endereço",
    "proof_address_neighborhood": "Comprovante — bairro",
    "proof_address_postal": "Comprovante — CEP",
    "proof_reference": "Comprovante — referência",
    "proof_period": "Comprovante — período",
    "proof_value": "Comprovante — valor",
    "proof_barcode": "Comprovante — código de barras",
    "bank_name": "Banco",
    "bank_branch": "Agência",
    "bank_account": "Conta",
    "transaction_date": "Data da transação",
    "transaction_type": "Tipo de transação",
    "payer": "Pagador",
    "payee": "Beneficiário",
    "amount_paid": "Valor pago",
    "authentication_code": "Código de autenticação",
    "paid_stamp_present": 'Carimbo "Pago"',
    "needs_review": "Revisar",
    "extracted_at": "Extraído em (UTC)",
}

AUDIT_LABELS_PT = {
    "pdf_filename": "Arquivo PDF",
    "timestamp": "Timestamp",
    "total_latency_s": "Latência total (s)",
    "azure_latency_s": "Latência Azure DI (s)",
    "llm_latency_s": "Latência LLM (s)",
    "llm_input_tokens": "Tokens de entrada",
    "llm_output_tokens": "Tokens de saída",
    "estimated_cost_usd": "Custo estimado (USD)",
    "cross_val_consistent": "Cross-validation OK",
    "mismatches": "Inconsistências",
    "error": "Erro",
}


def relabel_rows(rows: list[dict], labels: dict[str, str]) -> list[dict]:
    """Return rows with their dict keys remapped via labels (unmapped keys passthrough)."""
    return [{labels.get(k, k): v for k, v in row.items()} for row in rows]
