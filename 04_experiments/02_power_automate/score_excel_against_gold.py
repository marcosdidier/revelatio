"""Score Power Automate's Excel output against gold JSONs (Phase 5).

Reads `raw_output/debtor_extraction.xlsx`, matches each row to its
`05_synthetic_data/gold/F0X.json` by filename, applies the normalization
rules from `01_field_map/scoring_rubric.md`, and emits both per-cell
results and per-fixture aggregates to `scorecard.json` + a stdout summary.

Run: .venv/bin/python 04_experiments/02_power_automate/score_excel_against_gold.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

REPO = Path(__file__).resolve().parents[2]
EXCEL = REPO / "04_experiments/02_power_automate/raw_output/debtor_extraction.xlsx"
GOLD_DIR = REPO / "05_synthetic_data/gold"
SCORECARD = REPO / "04_experiments/02_power_automate/scorecard.json"

# Map Excel column -> (dot path into gold JSON, value type for normalization, weight)
FIELD_MAP: dict[str, tuple[str, str, int]] = {
    # Page 1 — Identificação Cliente
    "Nome completo": ("page1.client_name", "text", 1),
    "CPF": ("page1.cpf", "cpf", 2),  # weight 2 — primary identifier
    "Data de nascimento": ("page1.birth_date", "date", 1),
    "Telefone": ("page1.phone", "phone", 1),
    "E-mail": ("page1.email", "text", 1),
    "Endereço": ("page1.address", "text", 1),
    "CEP": ("page1.postal_code", "postal", 1),
    # Page 1 — Informações Dívida
    "Número do contrato": ("page1.contract_number", "text", 2),  # weight 2 — primary debt key
    "Produto": ("page1.product", "text", 1),
    "Data de contratação": ("page1.contract_date", "date", 1),
    "Valor original": ("page1.original_amount", "currency", 1),
    "Saldo atualizado": ("page1.updated_balance", "currency", 1),
    "Dias em atraso": ("page1.days_overdue", "days", 1),
    "Status interno": ("page1.status", "text", 1),
    "Última tentativa de contato": ("page1.last_contact_attempt", "date", 1),
    "Responsável interno": ("page1.internal_owner", "text", 1),
    # Page 2 — Comprovante Endereço
    "Titular do comprovante": ("page2.comprovante_endereco.proof_address_holder", "text", 1),
    "Endereço do comprovante": ("page2.comprovante_endereco.proof_address_line", "text", 1),
    "Bairro/Cidade/UF": ("page2.comprovante_endereco.proof_address_neighborhood", "text", 1),
    "CEP do comprovante": ("page2.comprovante_endereco.proof_address_postal", "postal", 1),
    "Tipo de conta (Referência)": ("page2.comprovante_endereco.proof_reference", "text", 1),
    "Mês/Ano de referência": ("page2.comprovante_endereco.proof_period", "month_year", 1),
    "Valor da conta": ("page2.comprovante_endereco.proof_value", "currency", 1),
    "Código de barras": ("page2.comprovante_endereco.proof_barcode", "barcode", 1),
    # Page 2 — Comprovante Bancário
    "Banco": ("page2.comprovante_bancario.bank_name", "text", 1),
    "Agência": ("page2.comprovante_bancario.bank_branch", "text", 1),
    "Conta": ("page2.comprovante_bancario.bank_account", "text", 1),
    "Data da transação": ("page2.comprovante_bancario.transaction_date", "date", 1),
    "Tipo de transação": ("page2.comprovante_bancario.transaction_type", "text", 1),
    "Pagador": ("page2.comprovante_bancario.payer", "text", 1),
    "Recebedor": ("page2.comprovante_bancario.payee", "text", 1),
    "Valor pago": ("page2.comprovante_bancario.amount_paid", "currency", 1),
    "Código de autenticação": ("page2.comprovante_bancario.authentication_code", "text", 1),
}
assert len(FIELD_MAP) == 33

PDF_TO_GOLD = {
    "F01_perfect.pdf": "F01_perfect.json",
    "F02_missing_email.pdf": "F02_missing_email.json",
    "F03_missing_phone.pdf": "F03_missing_phone.json",
    "F04_low_quality_page2.pdf": "F04_low_quality_page2.json",
    "F05_cpf_no_separators.pdf": "F05_cpf_no_separators.json",
    "F06_alternate_labels.pdf": "F06_alternate_labels.json",
    "F07_skewed_page2.pdf": "F07_skewed_page2.json",
    "F08_partial_obscure_page2.pdf": "F08_partial_obscure_page2.json",
}


def get_gold(gold: dict, dot_path: str) -> Any:
    cur: Any = gold
    for part in dot_path.split("."):
        if cur is None or not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normalize(value: Any, vtype: str) -> str | None:
    """Normalize a value to a canonical form for comparison. Returns None for missing."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    if isinstance(value, (datetime, date)):
        d = value.date() if isinstance(value, datetime) else value
        if vtype == "date":
            return d.isoformat()
        if vtype == "month_year":
            return d.strftime("%Y-%m")
        value = d.isoformat()

    s = str(value).strip()

    if vtype == "text":
        # case-insensitive, accent-insensitive, whitespace-collapsed, no trailing punct
        s = re.sub(r"\s+", " ", s)
        s = s.rstrip(".,;:")
        return strip_accents(s).lower()

    if vtype == "cpf":
        return re.sub(r"\D", "", s)  # 11 digits

    if vtype == "phone":
        digits = re.sub(r"\D", "", s)
        return digits[-11:] if len(digits) >= 10 else digits

    if vtype == "postal":
        return re.sub(r"\D", "", s)  # 8 digits

    if vtype == "barcode":
        return re.sub(r"\D", "", s)  # strip everything that isn't a digit

    if vtype == "days":
        m = re.search(r"\d+", s)
        return m.group(0) if m else s

    if vtype == "currency":
        s = re.sub(r"R\$\s*", "", s, flags=re.IGNORECASE).strip().replace(" ", "")
        # Detect format: comma present → BR-format (dots are thousands, comma is decimal).
        # No comma → already in ISO/US format ("18450.00"), leave dots as decimal point.
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
        try:
            return f"{Decimal(s):.2f}"
        except (InvalidOperation, ValueError):
            return s

    if vtype == "date":
        # Accept DD/MM/YYYY, YYYY-MM-DD, ISO datetimes, MM/YYYY, YYYY-MM
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(s.split(".")[0].rstrip("Z"), fmt).date().isoformat()
            except ValueError:
                continue
        return s  # fall through unparsed; comparison may still succeed

    if vtype == "month_year":
        # Accept MM/YYYY or YYYY-MM
        m = re.match(r"^(\d{2})/(\d{4})$", s)
        if m:
            return f"{m.group(2)}-{m.group(1)}"
        m = re.match(r"^(\d{4})-(\d{2})$", s)
        if m:
            return f"{m.group(1)}-{m.group(2)}"
        return s

    return s


def grade(extracted_norm: str | None, gold_norm: str | None) -> tuple[str, float]:
    """Return (label, raw_score) per scoring_rubric.md."""
    if gold_norm is None and extracted_norm is None:
        return ("exact", 1.0)  # both correctly absent
    if gold_norm is None and extracted_norm is not None:
        return ("hallucination", -0.5)
    if gold_norm is not None and extracted_norm is None:
        return ("miss", 0.0)
    if extracted_norm == gold_norm:
        return ("exact", 1.0)
    # substring match either direction → partial
    if extracted_norm in gold_norm or gold_norm in extracted_norm:
        return ("partial", 0.5)
    return ("miss", 0.0)


def score_row(row: dict[str, Any], gold: dict, headers: list[str]) -> dict:
    """Score one Excel row against its gold. Returns per-cell + aggregates."""
    cells = []
    page1_score = 0.0
    page2_score = 0.0
    page1_max = 0.0
    page2_max = 0.0
    halls = 0

    for col_name, (path, vtype, weight) in FIELD_MAP.items():
        idx = headers.index(col_name)
        extracted = row[idx] if idx < len(row) else None
        gold_value = get_gold(gold, path)

        ext_norm = normalize(extracted, vtype)
        gold_norm = normalize(gold_value, vtype)

        label, raw = grade(ext_norm, gold_norm)
        weighted = raw * weight

        is_page1 = path.startswith("page1.")
        if is_page1:
            page1_max += weight
            if raw > 0:
                page1_score += weighted
        else:
            page2_max += weight
            if raw > 0:
                page2_score += weighted

        if label == "hallucination":
            halls += 1
            # Penalty applies regardless of page (subtract from both)
            if is_page1:
                page1_score += weighted  # weighted is negative
            else:
                page2_score += weighted

        cells.append(
            {
                "field": col_name,
                "extracted": extracted,
                "gold": gold_value,
                "extracted_norm": ext_norm,
                "gold_norm": gold_norm,
                "result": label,
                "weight": weight,
                "weighted_score": weighted,
            }
        )

    total_max = page1_max + page2_max
    return {
        "cells": cells,
        "page1_score": round(page1_score, 2),
        "page1_max": page1_max,
        "page2_score": round(page2_score, 2),
        "page2_max": page2_max,
        "total_score": round(page1_score + page2_score, 2),
        "total_max": total_max,
        "overall_pct": round((page1_score + page2_score) / total_max * 100, 1) if total_max else 0,
        "hallucinations": halls,
    }


def verdict(pct: float) -> str:
    if pct >= 95:
        return "Production-ready as primary extractor"
    if pct >= 85:
        return "Production-ready with HITL on flagged rows"
    if pct >= 70:
        return "Useful as one stage of a hybrid pipeline"
    if pct >= 50:
        return "Marginal; cite as a baseline only"
    return "Not recommended for this use case"


def main() -> None:
    wb = load_workbook(EXCEL, data_only=True)
    ws = wb.active
    headers = [c.value for c in ws[1]]

    fixtures: dict[str, dict] = {}
    for r in range(2, ws.max_row + 1):
        row = [c.value for c in ws[r]]
        pdf = row[0]
        if not pdf:  # placeholder row
            continue

        gold_path = GOLD_DIR / PDF_TO_GOLD.get(pdf, "__missing__")
        if not gold_path.exists():
            print(f"⚠ skip {pdf}: no gold JSON ({gold_path.name})")
            continue

        gold = json.loads(gold_path.read_text())
        result = score_row(row, gold, headers)
        result["pdf"] = pdf
        result["confidence_at_runtime"] = row[2]
        result["verdict"] = verdict(result["overall_pct"])
        fixtures[pdf] = result

    summary = {
        "fixtures": fixtures,
        "aggregate": {
            "n_fixtures": len(fixtures),
            "avg_overall_pct": round(
                sum(f["overall_pct"] for f in fixtures.values()) / len(fixtures), 1
            )
            if fixtures
            else 0,
            "avg_page1_pct": round(
                sum(f["page1_score"] / f["page1_max"] * 100 for f in fixtures.values())
                / len(fixtures),
                1,
            )
            if fixtures
            else 0,
            "avg_page2_pct": round(
                sum(f["page2_score"] / f["page2_max"] * 100 for f in fixtures.values())
                / len(fixtures),
                1,
            )
            if fixtures
            else 0,
            "total_hallucinations": sum(f["hallucinations"] for f in fixtures.values()),
        },
    }

    SCORECARD.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str))

    print(f"\n{'PDF':<50} {'Overall':>8} {'Page1':>8} {'Page2':>8} {'Hall':>5}  Verdict")
    print("-" * 130)
    for pdf, f in fixtures.items():
        p1 = f"{f['page1_score']:.1f}/{f['page1_max']:.0f}"
        p2 = f"{f['page2_score']:.1f}/{f['page2_max']:.0f}"
        print(
            f"{pdf:<50} {f['overall_pct']:>7.1f}% {p1:>8} {p2:>8} {f['hallucinations']:>5}  {f['verdict']}"
        )
    agg = summary["aggregate"]
    print("-" * 130)
    print(
        f"{'AVERAGE':<50} {agg['avg_overall_pct']:>7.1f}% "
        f"p1_avg={agg['avg_page1_pct']:.1f}% p2_avg={agg['avg_page2_pct']:.1f}% "
        f"total_halls={agg['total_hallucinations']}"
    )
    print(f"\nFull scorecard written to: {SCORECARD}")


if __name__ == "__main__":
    main()
