"""Project Revelatio — reference extraction script.

Pipeline: PDF -> Azure DI Layout -> page-1 deterministic parse +
page-2 Claude Sonnet 4.6 with Option-B cross-validation -> CSV row.

Single-PDF or batch mode. Writes two CSVs: dossiers.csv (business data
for paralegals) and audit.csv (latencies, costs, mismatches for tech).

Run from project root or anywhere — uses sys.path so sibling modules
resolve regardless of cwd.
"""
import argparse
import csv
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

from azure_di_client import analyze_pdf
from claude_extractor import extract_page2
from page1_parser import parse_page1

DOSSIER_COLUMNS = [
    "pdf_filename",
    "client_name", "cpf", "birth_date", "phone", "email", "address", "postal_code",
    "contract_number", "product", "contract_date", "original_amount", "updated_balance",
    "days_overdue", "status", "last_contact_attempt", "internal_owner",
    "proof_address_holder", "proof_address_line", "proof_address_neighborhood",
    "proof_address_postal", "proof_reference", "proof_period", "proof_value", "proof_barcode",
    "bank_name", "bank_branch", "bank_account", "transaction_date", "transaction_type",
    "payer", "payee", "amount_paid", "authentication_code", "paid_stamp_present",
    "needs_review",
]

AUDIT_COLUMNS = [
    "pdf_filename", "timestamp",
    "total_latency_s", "azure_latency_s", "llm_latency_s",
    "llm_input_tokens", "llm_output_tokens", "estimated_cost_usd",
    "cross_val_consistent", "mismatches", "error",
]


def process_one(pdf_path: Path) -> tuple[dict, dict]:
    audit = {col: "" for col in AUDIT_COLUMNS}
    dossier = {col: "" for col in DOSSIER_COLUMNS}
    audit["pdf_filename"] = pdf_path.name
    audit["timestamp"] = datetime.now(UTC).isoformat()
    dossier["pdf_filename"] = pdf_path.name

    try:
        layout, azure_latency = analyze_pdf(pdf_path)
        audit["azure_latency_s"] = round(azure_latency, 2)

        page1 = parse_page1(layout)
        for k, v in page1.items():
            dossier[k] = "" if v is None else str(v)

        page2_text = _page2_text(layout)
        extraction, telemetry = extract_page2(
            page2_text,
            page1.get("client_name", ""),
            page1.get("cpf", ""),
        )
        audit.update({
            "llm_latency_s": telemetry["latency_s"],
            "llm_input_tokens": telemetry["input_tokens"],
            "llm_output_tokens": telemetry["output_tokens"],
            "estimated_cost_usd": telemetry["estimated_cost_usd"],
            "total_latency_s": round(azure_latency + telemetry["latency_s"], 2),
        })

        p2 = extraction.get("page2", {})
        for sub_key in ("comprovante_endereco", "comprovante_bancario"):
            for k, v in (p2.get(sub_key) or {}).items():
                dossier[k] = "" if v is None else str(v)

        cv = extraction.get("cross_validation", {})
        consistent = bool(cv.get("consistent", True))
        mismatches = cv.get("mismatches") or []
        audit["cross_val_consistent"] = "TRUE" if consistent else "FALSE"
        audit["mismatches"] = "; ".join(mismatches)
        dossier["needs_review"] = "FALSE" if consistent else "TRUE"

    except Exception as e:
        audit["error"] = f"{type(e).__name__}: {e}"
        dossier["needs_review"] = "TRUE"
        print(f"[ERROR] {pdf_path.name}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    return dossier, audit


def _page2_text(layout: dict) -> str:
    full = layout.get("content", "")
    pages = layout.get("pages", [])
    if len(pages) < 2:
        return ""
    spans = pages[1].get("spans", [])
    if spans:
        chunks = []
        for s in spans:
            offset = s.get("offset", 0)
            length = s.get("length", 0)
            chunks.append(full[offset:offset + length])
        return "\n".join(chunks)
    # Fallback: split at page boundary marker if spans aren't present
    marker = "Pagina 1"
    idx = full.find(marker)
    return full[idx + len(marker):].strip() if idx >= 0 else full


def write_csvs(dossier_rows: list[dict], audit_rows: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dossier_csv = out_dir / "dossiers.csv"
    audit_csv = out_dir / "audit.csv"
    with open(dossier_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=DOSSIER_COLUMNS)
        w.writeheader()
        w.writerows(dossier_rows)
    with open(audit_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=AUDIT_COLUMNS)
        w.writeheader()
        w.writerows(audit_rows)
    print(f"\nWrote {dossier_csv}")
    print(f"Wrote {audit_csv}")


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description="Revelatio — extract Banco X dossier PDFs to CSV.")
    p.add_argument("input", help="PDF file path, or directory if --batch")
    p.add_argument("--batch", action="store_true", help="treat input as a directory of PDFs")
    p.add_argument("--out", default=".", help="output directory for CSVs (default: cwd)")
    args = p.parse_args()

    in_path = Path(args.input)
    if args.batch:
        pdfs = sorted(in_path.glob("*.pdf"))
        if not pdfs:
            sys.exit(f"No PDFs found in {in_path}")
        print(f"Batch mode: {len(pdfs)} PDFs from {in_path}")
    else:
        pdfs = [in_path]

    dossier_rows, audit_rows = [], []
    for pdf in pdfs:
        print(f"  → {pdf.name}")
        d, a = process_one(pdf)
        dossier_rows.append(d)
        audit_rows.append(a)

    write_csvs(dossier_rows, audit_rows, Path(args.out))


if __name__ == "__main__":
    main()
