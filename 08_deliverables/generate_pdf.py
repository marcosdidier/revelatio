#!/usr/bin/env python3
"""Convert relatorio.md → relatorio.pdf.

Reads `08_deliverables/relatorio.md`, applies hiring-panel-appropriate CSS
(clean sans-serif, comfortable tables, A4, ~2cm margins) and writes
`08_deliverables/relatorio.pdf`.

Run from project root:
    .venv/bin/python 08_deliverables/generate_pdf.py
"""
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section

HERE = Path(__file__).parent
SRC = HERE / "relatorio.md"
OUT = HERE / "relatorio.pdf"

CSS = """
body {
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #1f1f1f;
}
h1 { font-size: 19pt; margin: 0 0 6pt 0; }
h2 { font-size: 14pt; margin: 16pt 0 6pt 0; border-bottom: 0.5pt solid #c0c0c0; padding-bottom: 3pt; }
h3 { font-size: 12pt; margin: 12pt 0 4pt 0; }
p { margin: 6pt 0; text-align: justify; }
strong { color: #111111; }
em { color: #333333; }
hr { border: none; border-top: 0.5pt solid #c0c0c0; margin: 12pt 0; }

table { border-collapse: collapse; margin: 8pt 0; width: 100%; }
th, td { border: 0.4pt solid #b0b0b0; padding: 4pt 6pt; vertical-align: top; font-size: 9.5pt; }
th { background: #e6eef7; font-weight: bold; }

code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9pt; background: #f5f5f5; padding: 0 2pt; border-radius: 2pt; }

ul, ol { margin: 4pt 0 4pt 18pt; padding: 0; }
li { margin: 2pt 0; }

blockquote { border-left: 2pt solid #c0c0c0; padding: 0 8pt; color: #444444; margin: 6pt 0; }
"""


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")

    md = SRC.read_text(encoding="utf-8")

    pdf = MarkdownPdf(toc_level=2, optimize=True)
    pdf.add_section(
        Section(md, toc=True, paper_size="A4", borders=(54, 54, -54, -54)),
        user_css=CSS,
    )

    pdf.meta["title"] = "Relatório — Implementador de IA & Automações"
    pdf.meta["author"] = "Projeto Revelatio"
    pdf.meta["subject"] = "Avaliação de ferramentas e recomendação de arquitetura para extração de dossiês do Banco X"
    pdf.meta["creator"] = "markdown-pdf"

    pdf.save(str(OUT))
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
