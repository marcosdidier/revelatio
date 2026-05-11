"""Deterministic page-1 parser.

Reads the Campo/Informação tables that Azure DI Layout auto-detects on page 1
of the Banco X dossier. No LLM call. Validated zero-shot on brief + F01 + F07
in Epic 5.7-5.8.
"""
from typing import Any

# Maps Portuguese labels (with/without accents) to our schema keys.
FIELD_MAP: dict[str, str] = {
    "Nome completo": "client_name",
    "CPF": "cpf",
    "Data de nascimento": "birth_date",
    "Telefone": "phone",
    "E-mail": "email",
    "Email": "email",
    "Endereco": "address",
    "Endereço": "address",
    "CEP": "postal_code",
    "Contrato": "contract_number",
    "Produto": "product",
    "Data de contratacao": "contract_date",
    "Data de contratação": "contract_date",
    "Valor original": "original_amount",
    "Saldo atualizado": "updated_balance",
    "Dias em atraso": "days_overdue",
    "Status interno": "status",
    "Ultima tentativa de contato": "last_contact_attempt",
    "Última tentativa de contato": "last_contact_attempt",
    "Responsavel interno": "internal_owner",
    "Responsável interno": "internal_owner",
}


def parse_page1(layout: dict[str, Any]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for table in layout.get("tables", []):
        if not _is_page1_table(table):
            continue
        rows: dict[int, dict[int, str]] = {}
        for cell in table.get("cells", []):
            r = cell.get("rowIndex", cell.get("row_index"))
            c = cell.get("columnIndex", cell.get("column_index"))
            rows.setdefault(r, {})[c] = (cell.get("content") or "").strip()
        for row_idx, cols in rows.items():
            if row_idx == 0:
                continue
            label = cols.get(0, "")
            value = cols.get(1, "")
            if not label or not value:
                continue
            if label == "CPF":
                value = value.replace("(ficticio)", "").replace("(fictício)", "").strip()
            schema_key = FIELD_MAP.get(label)
            if schema_key:
                parsed[schema_key] = value
    return _normalize(parsed)


def _is_page1_table(table: dict[str, Any]) -> bool:
    for region in table.get("boundingRegions", table.get("bounding_regions", [])):
        if region.get("pageNumber", region.get("page_number")) == 1:
            return True
    return False


def _normalize(d: dict[str, Any]) -> dict[str, Any]:
    for date_key in ("birth_date", "contract_date", "last_contact_attempt"):
        if d.get(date_key) and "/" in d[date_key]:
            parts = d[date_key].split("/")
            if len(parts) == 3:
                d[date_key] = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"

    for money_key in ("original_amount", "updated_balance"):
        if d.get(money_key):
            v = (
                d[money_key]
                .replace("R$", "")
                .replace(" ", "")
                .replace(".", "")
                .replace(",", ".")
            )
            d[money_key] = v

    if d.get("days_overdue"):
        digits = "".join(c for c in str(d["days_overdue"]) if c.isdigit())
        if digits:
            d["days_overdue"] = int(digits)

    return d
