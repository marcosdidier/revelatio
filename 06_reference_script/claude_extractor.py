"""Page-2 extraction via Claude Sonnet 4.6 with Option-B cross-validation.

Option B: send page-2 OCR text plus page-1 client_name and CPF as anchors.
The LLM extracts page-2 fields AND flags any inconsistency between the
anchors and what it finds on page 2 (e.g., a different name on the bank
receipt, or a different CPF in the comprovante header).
"""
import json
import os
import re
import time
from typing import Any

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

# Sonnet 4.6 pricing (per 1M tokens) — used to project cost in audit log.
COST_PER_M_INPUT_USD = 3.0
COST_PER_M_OUTPUT_USD = 15.0

SCHEMA_TEXT = """{
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
  },
  "cross_validation": {
    "consistent": true,
    "mismatches": ["string"]
  }
}"""


def extract_page2(
    page2_text: str, expected_name: str, expected_cpf: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    client = Anthropic()

    prompt = f"""Você está extraindo dados da página 2 de um dossiê do Banco X (comprovantes de endereço e bancário) e validando consistência com a página 1.

INFORMAÇÃO DA PÁGINA 1 (use para cross-validation):
- Cliente esperado: {expected_name}
- CPF esperado: {expected_cpf}

TEXTO DA PÁGINA 2:
{page2_text}

Tarefa: extraia os campos da página 2 seguindo o schema abaixo. ADICIONALMENTE, valide consistência — o "proof_address_holder" e o "payer" no comprovante bancário devem corresponder ao Cliente esperado. Se houver qualquer divergência (nome diferente, dados que parecem ser de outra pessoa, etc.), liste descritivamente em "mismatches" e marque "consistent": false.

Regras:
1. Campos ausentes no texto: use null (NUNCA invente valor plausível).
2. Extração literal: para cada campo, devolva o valor completo que aparece após o rótulo, exatamente como está no texto. Não segmente valores compostos (ex.: se o texto contém "Bairro: Boa Vista - Recife/PE", extraia "Boa Vista - Recife/PE" inteiro, não apenas "Boa Vista"). Esta regra aplica-se a campos de texto livre; campos com formato específico abaixo (datas, valores, CEP, código de barras) seguem suas próprias regras de normalização.
3. Datas: ISO YYYY-MM-DD (ou YYYY-MM para mês/ano).
4. Valores monetários: string decimal sem R$ e sem separador de milhar (ex: "184.72").
5. CEP: formato NNNNN-NNN.
6. Código de barras: apenas dígitos, sem pontos nem espaços.
7. paid_stamp_present: true se o texto contém "PAGO" como carimbo visual, false caso contrário.

Schema obrigatório:
{SCHEMA_TEXT}

Retorne APENAS o objeto JSON. Comece com {{ e termine com }}. Sem markdown, sem comentários, sem texto antes nem depois.
"""

    t0 = time.perf_counter()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.perf_counter() - t0

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    extraction = json.loads(raw)

    in_tok = response.usage.input_tokens
    out_tok = response.usage.output_tokens
    cost = (
        in_tok * COST_PER_M_INPUT_USD / 1_000_000
        + out_tok * COST_PER_M_OUTPUT_USD / 1_000_000
    )

    telemetry = {
        "latency_s": round(elapsed, 2),
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "estimated_cost_usd": round(cost, 5),
    }
    return extraction, telemetry
