"""Append extracted dossier rows to a shared Google Sheet.

Single public function: append_dossiers(rows, sheet_id, worksheet_name).
Authorizes with a Google Cloud service-account JSON read from the env
var GOOGLE_SERVICE_ACCOUNT_JSON. The sheet must be shared (Editor) with
the service-account email — see DEPLOY.md.

Append-only: each call adds a new row per dossier with an extracted_at
UTC timestamp written by this module (not by the pipeline), so multiple
runs against the same sheet stay distinguishable.
"""
import json
import os
from datetime import UTC, datetime

import gspread
from google.oauth2.service_account import Credentials

from extract_dossier import DOSSIER_COLUMNS

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_COLUMNS = DOSSIER_COLUMNS + ["extracted_at"]


class SheetsWriterError(RuntimeError):
    """Raised for any failure path. Message is safe to surface in UI."""


def _load_credentials() -> Credentials:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise SheetsWriterError(
            "GOOGLE_SERVICE_ACCOUNT_JSON não está configurado. "
            "Veja DEPLOY.md (bloco 1)."
        )
    info = raw if isinstance(raw, dict) else json.loads(raw)
    try:
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    except (ValueError, KeyError) as exc:
        raise SheetsWriterError(
            f"JSON da service account inválido: {exc}"
        ) from exc


def _open_or_create_worksheet(
    client: gspread.Client, sheet_id: str, worksheet_name: str
) -> gspread.Worksheet:
    try:
        spreadsheet = client.open_by_key(sheet_id)
    except gspread.SpreadsheetNotFound as exc:
        raise SheetsWriterError(
            f"Planilha {sheet_id} não encontrada. Verifique o GOOGLE_SHEET_ID "
            "e se a planilha foi compartilhada com a service account (Editor)."
        ) from exc
    except gspread.exceptions.APIError as exc:
        raise SheetsWriterError(
            f"Erro de API ao abrir a planilha: {exc}. "
            "Confirme o compartilhamento com a service account."
        ) from exc
    try:
        return spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(
            title=worksheet_name, rows=1000, cols=len(SHEET_COLUMNS)
        )


def append_dossiers(
    rows: list[dict],
    sheet_id: str,
    worksheet_name: str = "Dossiers",
    header_labels: dict[str, str] | None = None,
) -> str:
    """Append rows to the shared sheet. Returns the sheet URL.

    Adds extracted_at (UTC ISO-8601) to each row. Writes the header row
    if the worksheet is empty; header uses header_labels when provided
    (English-key -> display-label), else the raw English keys.
    """
    if not rows:
        raise SheetsWriterError("Nenhuma linha para enviar.")
    if not sheet_id:
        raise SheetsWriterError(
            "GOOGLE_SHEET_ID não está configurado. Veja DEPLOY.md (bloco 2)."
        )

    creds = _load_credentials()
    client = gspread.authorize(creds)
    worksheet = _open_or_create_worksheet(client, sheet_id, worksheet_name)

    extracted_at = datetime.now(UTC).isoformat(timespec="seconds")
    enriched = [{**row, "extracted_at": extracted_at} for row in rows]
    values = [[str(row.get(col, "")) for col in SHEET_COLUMNS] for row in enriched]
    labels = header_labels or {}
    header_row = [labels.get(col, col) for col in SHEET_COLUMNS]

    try:
        if not worksheet.row_values(1):
            worksheet.append_row(header_row, value_input_option="USER_ENTERED")
        worksheet.append_rows(values, value_input_option="USER_ENTERED")
    except gspread.exceptions.APIError as exc:
        raise SheetsWriterError(f"Falha ao gravar na planilha: {exc}") from exc

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
