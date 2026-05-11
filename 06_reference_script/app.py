"""Streamlit demo UI for the Revelatio extraction pipeline.

Wraps extract_dossier.process_one() for a drag-drop UX. This is a DEMO
skin, not a production tool — in real deployment, the pipeline sits
behind an n8n workflow or a custom web app built by the firm's IT.

Run with:  streamlit run 06_reference_script/app.py
"""
import csv
import io
import sys
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from extract_dossier import AUDIT_COLUMNS, DOSSIER_COLUMNS, process_one

load_dotenv()

st.set_page_config(
    page_title="Revelatio — Extração de Dossiês",
    page_icon="📄",
    layout="wide",
)
st.title("Revelatio — Extração de Dossiês")
st.caption(
    "Faça upload de PDFs do Banco X · extração automática via Azure DI + Claude · "
    "CSV pronto para Excel."
)

with st.expander("Como funciona"):
    st.markdown(
        """
        1. **Upload** de um ou mais PDFs de dossiê de cliente devedor.
        2. **Página 1** é extraída deterministicamente (Azure DI Layout — sem LLM).
        3. **Página 2** é extraída via Claude Sonnet 4.6 com cross-validation
           (o sistema verifica se o nome e CPF da página 2 batem com a página 1).
        4. **CSV** é gerado pronto para abrir no Excel. A coluna `needs_review`
           identifica os dossiês que precisam de revisão manual.
        """
    )

uploaded = st.file_uploader(
    "PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    help="Pode arrastar múltiplos PDFs de uma vez.",
)

if uploaded and st.button(
    f"▶ Extrair {len(uploaded)} dossiê(s)", type="primary"
):
    progress = st.progress(0.0)
    status = st.empty()
    dossier_rows, audit_rows = [], []

    for i, upload in enumerate(uploaded):
        status.write(f"Processando: **{upload.name}**")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(upload.read())
            tmp_path = Path(tmp.name)
        try:
            dossier, audit = process_one(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
        dossier["pdf_filename"] = upload.name
        audit["pdf_filename"] = upload.name
        dossier_rows.append(dossier)
        audit_rows.append(audit)
        progress.progress((i + 1) / len(uploaded))

    flagged = sum(1 for r in dossier_rows if r.get("needs_review") == "TRUE")
    status.success(
        f"Concluído. {len(dossier_rows)} dossiê(s) processado(s) · "
        f"{flagged} marcado(s) para revisão."
    )

    st.subheader("Resultado")
    st.dataframe(dossier_rows, use_container_width=True)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=DOSSIER_COLUMNS)
    writer.writeheader()
    writer.writerows(dossier_rows)
    st.download_button(
        "⬇ Baixar dossiers.csv",
        buf.getvalue(),
        "dossiers.csv",
        "text/csv",
        type="primary",
    )

    with st.expander("Detalhes operacionais (audit log)"):
        st.dataframe(audit_rows, use_container_width=True)
        audit_buf = io.StringIO()
        audit_writer = csv.DictWriter(audit_buf, fieldnames=AUDIT_COLUMNS)
        audit_writer.writeheader()
        audit_writer.writerows(audit_rows)
        st.download_button(
            "⬇ Baixar audit.csv", audit_buf.getvalue(), "audit.csv", "text/csv"
        )

        total_cost = sum(
            float(a.get("estimated_cost_usd") or 0) for a in audit_rows
        )
        avg_latency = (
            sum(float(a.get("total_latency_s") or 0) for a in audit_rows)
            / len(audit_rows)
            if audit_rows
            else 0
        )
        st.metric("Custo total estimado (USD)", f"${total_cost:.4f}")
        st.metric("Latência média por dossiê (s)", f"{avg_latency:.1f}")
