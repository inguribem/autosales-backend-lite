import os
import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

APPOINTMENTS_SHEET_ID = os.getenv("APPOINTMENTS_SHEET_ID")
SHEET_TAB = "Hoja 1"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Maps Google Form header text → canonical API field name (Spanish + English)
HEADER_MAP = {
    "marca temporal": "timestamp",
    "timestamp": "timestamp",
    "nombre": "customerName",
    "name": "customerName",
    "empresa": "company",
    "compañía": "company",
    "company": "company",
    "correo electrónico": "email",
    "correo": "email",
    "email": "email",
    "teléfono": "customerPhone",
    "telefono": "customerPhone",
    "phone": "customerPhone",
    "fecha": "date",
    "date": "date",
    "hora": "time",
    "time": "time",
    "notas": "notes",
    "nota": "notes",
    "notes": "notes",
    "tipo": "appointmentType",
    "tipo de cita": "appointmentType",
    "categoría": "appointmentType",
    "categoria": "appointmentType",
    "type": "appointmentType",
    "status": "status",
    "estado": "status",
}


def _canonical(header: str) -> str:
    return HEADER_MAP.get(header.strip().lower(), header.strip().lower())


def _get_sheet() -> gspread.Worksheet:
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON env var not set")
    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(APPOINTMENTS_SHEET_ID).worksheet(SHEET_TAB)


def _raw_headers(sheet: gspread.Worksheet) -> list[str]:
    return sheet.row_values(1)


def _build_row(raw_headers: list[str], data: dict, preserve_timestamp: str | None = None) -> list[str]:
    """Build a sheet row in column order from canonical data dict."""
    row = []
    for h in raw_headers:
        canonical = _canonical(h)
        if canonical == "timestamp":
            row.append(preserve_timestamp or datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        else:
            row.append(str(data.get(canonical, "")))
    return row


# ── READ ──────────────────────────────────────────────────────────────────────

def get_appointments_from_sheet() -> list[dict]:
    try:
        sheet = _get_sheet()
    except Exception as e:
        print(f"[sheets] Auth error: {e}")
        return []

    rows = sheet.get_all_values()
    if len(rows) < 2:
        return []

    headers = [_canonical(h) for h in rows[0]]
    print(f"[sheets] Columns: {headers}")

    appointments = []
    for i, row in enumerate(rows[1:], start=1):
        padded = row + [""] * (len(headers) - len(row))
        record = dict(zip(headers, padded))
        record["id"] = str(i)
        appointments.append(record)

    return appointments


# ── CREATE ────────────────────────────────────────────────────────────────────

def append_appointment(data: dict) -> dict:
    sheet = _get_sheet()
    raw_hdrs = _raw_headers(sheet)
    row = _build_row(raw_hdrs, data)
    sheet.append_row(row, value_input_option="USER_ENTERED")
    return {"success": True}


# ── UPDATE ────────────────────────────────────────────────────────────────────

def update_appointment(row_id: int, data: dict) -> dict:
    """row_id is 1-based data index (excludes header); sheet row = row_id + 1."""
    sheet = _get_sheet()
    raw_hdrs = _raw_headers(sheet)
    sheet_row = row_id + 1

    # Preserve the existing timestamp
    existing = sheet.row_values(sheet_row)
    padded = existing + [""] * (len(raw_hdrs) - len(existing))
    ts_idx = next(
        (i for i, h in enumerate(raw_hdrs) if _canonical(h) == "timestamp"), None
    )
    existing_ts = padded[ts_idx] if ts_idx is not None else None

    row = _build_row(raw_hdrs, data, preserve_timestamp=existing_ts)
    end_col = chr(64 + len(raw_hdrs)) if len(raw_hdrs) <= 26 else "Z"
    sheet.update(f"A{sheet_row}:{end_col}{sheet_row}", [row], value_input_option="USER_ENTERED")
    return {"success": True}


# ── DELETE ────────────────────────────────────────────────────────────────────

def delete_appointment(row_id: int) -> dict:
    """row_id is 1-based data index (excludes header); sheet row = row_id + 1."""
    sheet = _get_sheet()
    sheet.delete_rows(row_id + 1)
    return {"success": True}
