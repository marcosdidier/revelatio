"""Streamlit demo UI for the Revelatio extraction pipeline.

Wraps extract_dossier.process_one() for a drag-drop UX. Deployed at
Streamlit Community Cloud; runs locally with .env. See DEPLOY.md for
the hosted-deploy runbook.
"""
import csv
import io
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))


def _bridge_secrets_to_env() -> None:
    """Copy st.secrets into os.environ before importing the pipeline.

    extract_dossier.* and sheets_writer.* read env vars at call/import
    time, so the bridge has to run first. Local .env is loaded after
    via load_dotenv(); existing env vars always win (no override).
    """
    keys = (
        "ANTHROPIC_API_KEY",
        "AZURE_DI_ENDPOINT",
        "AZURE_DI_KEY",
        "GOOGLE_SHEET_ID",
        "GOOGLE_SERVICE_ACCOUNT_JSON",
    )
    try:
        secrets = st.secrets
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return
    for key in keys:
        if key in secrets and key not in os.environ:
            value = secrets[key]
            os.environ[key] = value if isinstance(value, str) else str(value)


_bridge_secrets_to_env()
load_dotenv()

from extract_dossier import AUDIT_COLUMNS, DOSSIER_COLUMNS, process_one  # noqa: E402
from labels_pt import AUDIT_LABELS_PT, DOSSIER_LABELS_PT, relabel_rows  # noqa: E402
from sheets_writer import SheetsWriterError, append_dossiers  # noqa: E402

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
st.caption(":warning: Demo: use apenas com dados sintéticos.")

with st.expander("Como funciona"):
    st.markdown(
        """
        1. **Upload** de um ou mais PDFs de dossiê de cliente devedor.
        2. **Página 1** é extraída deterministicamente (Azure DI Layout — sem LLM).
        3. **Página 2** é extraída via Claude Sonnet 4.6 com cross-validation
           (o sistema verifica se o nome e CPF da página 2 batem com a página 1).
        4. **CSV** é gerado pronto para abrir no Excel. A coluna `needs_review`
           identifica os dossiês que precisam de revisão manual.
        5. **Opcional**: envie o resultado para uma planilha Google compartilhada
           com o painel (botão aparece após a extração).
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
    st.session_state["dossier_rows"] = dossier_rows
    st.session_state["audit_rows"] = audit_rows

if "dossier_rows" in st.session_state:
    dossier_rows = st.session_state["dossier_rows"]
    audit_rows = st.session_state["audit_rows"]

    st.subheader("Resultado")
    st.dataframe(
        relabel_rows(dossier_rows, DOSSIER_LABELS_PT),
        use_container_width=True,
    )

    buf = io.StringIO()
    csv_writer = csv.writer(buf)
    csv_writer.writerow([DOSSIER_LABELS_PT.get(c, c) for c in DOSSIER_COLUMNS])
    csv_writer.writerows(
        [row.get(c, "") for c in DOSSIER_COLUMNS] for row in dossier_rows
    )

    col_csv, col_sheet = st.columns(2)
    with col_csv:
        st.download_button(
            "⬇ Baixar dossiers.csv",
            buf.getvalue(),
            "dossiers.csv",
            "text/csv",
            type="primary",
        )
    with col_sheet:
        sheet_id = os.environ.get("GOOGLE_SHEET_ID", "")
        if st.button(
            "📤 Enviar para Planilha Google",
            disabled=not sheet_id,
            help=(
                "Anexa as linhas extraídas na planilha compartilhada."
                if sheet_id
                else "GOOGLE_SHEET_ID não configurado (ver DEPLOY.md)."
            ),
        ):
            try:
                url = append_dossiers(
                    dossier_rows,
                    sheet_id=sheet_id,
                    header_labels=DOSSIER_LABELS_PT,
                )
            except SheetsWriterError as exc:
                st.error(str(exc))
            else:
                st.success(
                    f"{len(dossier_rows)} linha(s) enviada(s) com sucesso."
                )
                st.markdown(f"[Abrir planilha]({url})")

    with st.expander("Detalhes operacionais (audit log)"):
        st.dataframe(
            relabel_rows(audit_rows, AUDIT_LABELS_PT),
            use_container_width=True,
        )
        audit_buf = io.StringIO()
        audit_csv_writer = csv.writer(audit_buf)
        audit_csv_writer.writerow(
            [AUDIT_LABELS_PT.get(c, c) for c in AUDIT_COLUMNS]
        )
        audit_csv_writer.writerows(
            [row.get(c, "") for c in AUDIT_COLUMNS] for row in audit_rows
        )
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
