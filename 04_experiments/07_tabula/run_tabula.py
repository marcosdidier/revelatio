"""
Epic 5.8 — Tabula hands-on test.

Goal: empirical OSS data point for the relatório.
Prediction: Tabula succeeds on page-1 table structure, fails on page-2 image content
(no OCR — Tabula reads PDF text streams only).
"""
import time
from pathlib import Path
import tabula

TARGETS = [
    ("brief", Path("00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf")),
    ("F01", Path("05_synthetic_data/pdfs/F01_perfect.pdf")),
    ("F07", Path("05_synthetic_data/pdfs/F07_skewed_page2.pdf")),
]
OUT_DIR = Path("04_experiments/07_tabula")


def run_one(label: str, pdf_path: Path) -> dict:
    print(f"\n=== {label}: {pdf_path.name} ===")
    result = {"label": label, "pdf": str(pdf_path), "pages": {}}

    for page in (1, 2):
        t0 = time.perf_counter()
        try:
            dfs = tabula.read_pdf(
                str(pdf_path),
                pages=str(page),
                multiple_tables=True,
                lattice=False,  # try stream mode first (no ruled lines in our PDFs)
                stream=True,
                silent=True,
            )
            elapsed = time.perf_counter() - t0
            tables = len(dfs)
            total_cells = sum(df.size for df in dfs)
            print(f"  page {page}: {tables} table(s), {total_cells} cells, {elapsed:.2f}s")
            for i, df in enumerate(dfs):
                csv_path = OUT_DIR / f"{label}_page{page}_table{i+1}.csv"
                df.to_csv(csv_path, index=False)
            result["pages"][page] = {
                "tables_detected": tables,
                "total_cells": total_cells,
                "latency_s": round(elapsed, 2),
            }
        except Exception as e:
            elapsed = time.perf_counter() - t0
            print(f"  page {page}: ERROR — {type(e).__name__}: {e}")
            result["pages"][page] = {
                "tables_detected": 0,
                "total_cells": 0,
                "latency_s": round(elapsed, 2),
                "error": f"{type(e).__name__}: {e}",
            }
    return result


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = [run_one(label, pdf) for label, pdf in TARGETS]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in summary:
        print(f"\n{r['label']} ({Path(r['pdf']).name})")
        for page, info in r["pages"].items():
            err = f"  ERROR: {info['error']}" if "error" in info else ""
            print(
                f"  page {page}: {info['tables_detected']} tables, "
                f"{info['total_cells']} cells, {info['latency_s']}s{err}"
            )


if __name__ == "__main__":
    main()
