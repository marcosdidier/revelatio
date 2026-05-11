"""Generic scorer: compare an extracted-JSON file against gold_truth.json.

Reuses normalization rules from `01_field_map/scoring_rubric.md` (same logic
as `02_power_automate/score_excel_against_gold.py` but reading a JSON
extraction result instead of an Excel row). Used for the LLM round-robin
(5.3 ChatGPT, 5.4 Claude, 5.5 NotebookLM) and any future tool whose output
fits the gold-JSON schema.

Run: .venv/bin/python 04_experiments/score_json_against_gold.py <extracted.json> [gold.json]
     gold.json defaults to 01_field_map/gold_truth.json (the brief example PDF gold)
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_GOLD = REPO / "01_field_map/gold_truth.json"

# (gold_dot_path, value_type, weight) — same schema/weights as the Excel scorer
FIELD_MAP: dict[str, tuple[str, str, int]] = {
    "client_name": ("page1.client_name", "text", 1),
    "cpf": ("page1.cpf", "cpf", 2),
    "birth_date": ("page1.birth_date", "date", 1),
    "phone": ("page1.phone", "phone", 1),
    "email": ("page1.email", "text", 1),
    "address": ("page1.address", "text", 1),
    "postal_code": ("page1.postal_code", "postal", 1),
    "contract_number": ("page1.contract_number", "text", 2),
    "product": ("page1.product", "text", 1),
    "contract_date": ("page1.contract_date", "date", 1),
    "original_amount": ("page1.original_amount", "currency", 1),
    "updated_balance": ("page1.updated_balance", "currency", 1),
    "days_overdue": ("page1.days_overdue", "days", 1),
    "status": ("page1.status", "text", 1),
    "last_contact_attempt": ("page1.last_contact_attempt", "date", 1),
    "internal_owner": ("page1.internal_owner", "text", 1),
    "proof_address_holder": ("page2.comprovante_endereco.proof_address_holder", "text", 1),
    "proof_address_line": ("page2.comprovante_endereco.proof_address_line", "text", 1),
    "proof_address_neighborhood": ("page2.comprovante_endereco.proof_address_neighborhood", "text", 1),
    "proof_address_postal": ("page2.comprovante_endereco.proof_address_postal", "postal", 1),
    "proof_reference": ("page2.comprovante_endereco.proof_reference", "text", 1),
    "proof_period": ("page2.comprovante_endereco.proof_period", "month_year", 1),
    "proof_value": ("page2.comprovante_endereco.proof_value", "currency", 1),
    "proof_barcode": ("page2.comprovante_endereco.proof_barcode", "barcode", 1),
    "bank_name": ("page2.comprovante_bancario.bank_name", "text", 1),
    "bank_branch": ("page2.comprovante_bancario.bank_branch", "text", 1),
    "bank_account": ("page2.comprovante_bancario.bank_account", "text", 1),
    "transaction_date": ("page2.comprovante_bancario.transaction_date", "date", 1),
    "transaction_type": ("page2.comprovante_bancario.transaction_type", "text", 1),
    "payer": ("page2.comprovante_bancario.payer", "text", 1),
    "payee": ("page2.comprovante_bancario.payee", "text", 1),
    "amount_paid": ("page2.comprovante_bancario.amount_paid", "currency", 1),
    "authentication_code": ("page2.comprovante_bancario.authentication_code", "text", 1),
}


def get_dot(d: dict, path: str) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normalize(value: Any, vtype: str) -> str | None:
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
        s = re.sub(r"\s+", " ", s).rstrip(".,;:")
        return strip_accents(s).lower()
    if vtype == "cpf":
        return re.sub(r"\D", "", s)
    if vtype == "phone":
        digits = re.sub(r"\D", "", s)
        return digits[-11:] if len(digits) >= 10 else digits
    if vtype == "postal":
        return re.sub(r"\D", "", s)
    if vtype == "barcode":
        return re.sub(r"\D", "", s)
    if vtype == "days":
        m = re.search(r"\d+", s)
        return m.group(0) if m else s
    if vtype == "currency":
        s = re.sub(r"R\$\s*", "", s, flags=re.IGNORECASE).replace(" ", "")
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
        try:
            return f"{Decimal(s):.2f}"
        except (InvalidOperation, ValueError):
            return s
    if vtype == "date":
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(s.split(".")[0].rstrip("Z"), fmt).date().isoformat()
            except ValueError:
                continue
        return s
    if vtype == "month_year":
        m = re.match(r"^(\d{2})/(\d{4})$", s)
        if m:
            return f"{m.group(2)}-{m.group(1)}"
        m = re.match(r"^(\d{4})-(\d{2})$", s)
        if m:
            return f"{m.group(1)}-{m.group(2)}"
        return s
    return s


def grade(ext_norm: str | None, gold_norm: str | None) -> tuple[str, float]:
    if gold_norm is None and ext_norm is None:
        return ("exact", 1.0)
    if gold_norm is None and ext_norm is not None:
        return ("hallucination", -0.5)
    if gold_norm is not None and ext_norm is None:
        return ("miss", 0.0)
    if ext_norm == gold_norm:
        return ("exact", 1.0)
    if ext_norm in gold_norm or gold_norm in ext_norm:
        return ("partial", 0.5)
    return ("miss", 0.0)


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
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    extracted_path = Path(sys.argv[1])
    gold_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_GOLD

    extracted = json.loads(extracted_path.read_text())
    gold = json.loads(gold_path.read_text())

    cells = []
    page1_score = page2_score = page1_max = page2_max = 0.0
    halls = 0

    for fld, (path, vtype, weight) in FIELD_MAP.items():
        ext_value = get_dot(extracted, path)
        gold_value = get_dot(gold, path)
        ext_norm = normalize(ext_value, vtype)
        gold_norm = normalize(gold_value, vtype)
        label, raw = grade(ext_norm, gold_norm)
        weighted = raw * weight

        is_p1 = path.startswith("page1.")
        if is_p1:
            page1_max += weight
            if raw > 0:
                page1_score += weighted
        else:
            page2_max += weight
            if raw > 0:
                page2_score += weighted
        if label == "hallucination":
            halls += 1
            (page1_score if is_p1 else 0)  # bookkeeping; weighted is negative
            if is_p1:
                page1_score += weighted
            else:
                page2_score += weighted

        cells.append(
            {
                "field": fld,
                "extracted": ext_value,
                "gold": gold_value,
                "result": label,
                "weight": weight,
                "weighted_score": weighted,
            }
        )

    total_max = page1_max + page2_max
    overall_pct = (page1_score + page2_score) / total_max * 100 if total_max else 0
    summary = {
        "extracted_path": str(extracted_path),
        "gold_path": str(gold_path),
        "page1_score": round(page1_score, 2),
        "page1_max": page1_max,
        "page1_pct": round(page1_score / page1_max * 100, 1) if page1_max else 0,
        "page2_score": round(page2_score, 2),
        "page2_max": page2_max,
        "page2_pct": round(page2_score / page2_max * 100, 1) if page2_max else 0,
        "overall_score": round(page1_score + page2_score, 2),
        "overall_max": total_max,
        "overall_pct": round(overall_pct, 1),
        "hallucinations": halls,
        "verdict": verdict(overall_pct),
        "cells": cells,
    }

    out_path = extracted_path.with_name(extracted_path.stem + "_scorecard.json")
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str))

    print(f"\n{extracted_path.name} vs {gold_path.name}")
    print("-" * 80)
    print(
        f"  Overall: {overall_pct:.1f}%  "
        f"(Page1 {summary['page1_pct']:.1f}% | Page2 {summary['page2_pct']:.1f}% | "
        f"Hallucinations: {halls})"
    )
    print(f"  Verdict: {summary['verdict']}")

    misses = [c for c in cells if c["result"] != "exact"]
    if misses:
        print(f"\n  Non-exact cells ({len(misses)}):")
        for c in misses:
            ext = str(c["extracted"])[:50]
            gold = str(c["gold"])[:50]
            print(f"    [{c['result']:13s}] {c['field']:30s} extracted={ext!r:52s} gold={gold!r}")
    print(f"\n  Full scorecard: {out_path}")


if __name__ == "__main__":
    main()
