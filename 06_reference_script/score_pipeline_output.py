"""Score the reference-script CSV output against gold JSONs.

Reads dossiers.csv, reconstructs each row into the gold-schema JSON shape,
then delegates to the existing 04_experiments/score_json_against_gold.py
for the verdict. Same scoring rules as every other tool's evaluation.
"""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCORER = REPO / "04_experiments/score_json_against_gold.py"
VENV_PY = REPO / ".venv/bin/python"

# Which gold belongs to which PDF.
GOLD_FOR: dict[str, Path] = {
    "exemplo_pdf_cliente_devedor_ficticio.pdf": REPO / "01_field_map/gold_truth.json",
    "F02_missing_email.pdf": REPO / "05_synthetic_data/gold/F02_missing_email.json",
    "F07_skewed_page2.pdf": REPO / "05_synthetic_data/gold/F07_skewed_page2.json",
    "F09_brief_shape.pdf": REPO / "05_synthetic_data/gold/F09_brief_shape.json",
}

PAGE1_FIELDS = [
    "client_name", "cpf", "birth_date", "phone", "email", "address", "postal_code",
    "contract_number", "product", "contract_date", "original_amount", "updated_balance",
    "days_overdue", "status", "last_contact_attempt", "internal_owner",
]
COMPROVANTE_ENDERECO = [
    "proof_address_holder", "proof_address_line", "proof_address_neighborhood",
    "proof_address_postal", "proof_reference", "proof_period", "proof_value", "proof_barcode",
]
COMPROVANTE_BANCARIO = [
    "bank_name", "bank_branch", "bank_account", "transaction_date", "transaction_type",
    "payer", "payee", "amount_paid", "authentication_code", "paid_stamp_present",
]


def _v(row: dict, key: str):
    """Return None for empty string (so it matches gold's null), else the string."""
    val = row.get(key, "")
    if val == "" or val is None:
        return None
    if key == "days_overdue":
        try:
            return int(val)
        except ValueError:
            return val
    if key == "paid_stamp_present":
        return val.lower() == "true"
    return val


def row_to_gold_schema(row: dict) -> dict:
    return {
        "page1": {k: _v(row, k) for k in PAGE1_FIELDS},
        "page2": {
            "comprovante_endereco": {k: _v(row, k) for k in COMPROVANTE_ENDERECO},
            "comprovante_bancario": {k: _v(row, k) for k in COMPROVANTE_BANCARIO},
        },
    }


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "06_reference_script/test_corpus/dossiers.csv"
    if not csv_path.exists():
        sys.exit(f"Not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Scoring {len(rows)} row(s) from {csv_path}\n")

    for row in rows:
        pdf_name = row["pdf_filename"]
        gold = GOLD_FOR.get(pdf_name)
        if not gold:
            print(f"  ! No gold mapped for {pdf_name}, skipping")
            continue
        if not gold.exists():
            print(f"  ! Gold file missing: {gold}")
            continue

        extracted = row_to_gold_schema(row)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump(extracted, tmp, ensure_ascii=False)
            tmp_path = Path(tmp.name)

        print(f"=== {pdf_name} ===")
        try:
            subprocess.run(
                [str(VENV_PY), str(SCORER), str(tmp_path), str(gold)],
                check=True,
            )
        finally:
            tmp_path.unlink(missing_ok=True)
        print()


if __name__ == "__main__":
    main()
