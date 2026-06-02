import os
import json
from collections import defaultdict

import gspread
from google.oauth2.service_account import Credentials

ASSET_SHEET_ID = os.getenv("ASSET_SHEET_ID")
ASSET_TAB = "Historico_Movimientos"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Maps sheet header text → canonical field name (Spanish + English variants)
ASSET_HEADER_MAP = {
    "id_vehiculos": "vehicleId",
    "id vehiculos": "vehicleId",
    "id_vehiculo": "vehicleId",
    "id vehiculo": "vehicleId",
    "vehiculo": "vehicleId",
    "vehicle": "vehicleId",
    "vehicle_id": "vehicleId",
    "vehicle id": "vehicleId",
    "id": "id",
    "fecha": "date",
    "date": "date",
    "fecha_movimiento": "date",
    "fecha movimiento": "date",
    "fecha_hora": "fechaHora",
    "fecha hora": "fechaHora",
    "marca temporal": "timestamp",
    "timestamp": "timestamp",
    "estado": "status",
    "status": "status",
    "ubicacion": "ubicacion",
    "ubicación": "ubicacion",
    "location": "ubicacion",
    "ubicacion_reportada": "ubicacion",
    "ubicación_reportada": "ubicacion",
    "ubicacion reportada": "ubicacion",
    "accion": "action",
    "acción": "action",
    "action": "action",
    "tipo_movimiento": "action",
    "tipo movimiento": "action",
    "notas": "notes",
    "nota": "notes",
    "notes": "notes",
    "mensaje_original": "mensaje",
    "mensaje original": "mensaje",
    "mensaje": "mensaje",
    "responsable": "responsable",
    "assigned_to": "responsable",
    "assigned to": "responsable",
}


def _canonical(header: str) -> str:
    return ASSET_HEADER_MAP.get(header.strip().lower(), header.strip().lower())


def _get_sheet() -> gspread.Worksheet:
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON env var not set")
    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(ASSET_SHEET_ID).worksheet(ASSET_TAB)


def get_vehicle_history() -> list[dict]:
    """
    Reads Historico_Movimientos, groups rows by vehicleId,
    returns one entry per vehicle with latestRecord + full history.
    """
    if not ASSET_SHEET_ID:
        print("[asset_sheets] ASSET_SHEET_ID not set")
        return []

    try:
        sheet = _get_sheet()
    except Exception as e:
        print(f"[asset_sheets] Auth error: {e}")
        return []

    rows = sheet.get_all_values()
    if len(rows) < 2:
        return []

    headers = [_canonical(h) for h in rows[0]]
    print(f"[asset_sheets] Columns: {headers}")

    # Build flat record list
    records: list[dict] = []
    for i, row in enumerate(rows[1:], start=1):
        padded = row + [""] * (len(headers) - len(row))
        record = dict(zip(headers, padded))
        record["rowId"] = str(i)
        records.append(record)

    # Group by vehicleId (preserve insertion order)
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        vid = record.get("vehicleId") or record.get("id_vehiculos") or f"row-{record['rowId']}"
        groups[vid].append(record)

    # Build result — most recent = last appended row
    result = []
    for vehicle_id, history in groups.items():
        latest = history[-1]
        result.append({
            "vehicleId": vehicle_id,
            "latestRecord": latest,
            "latestDate": latest.get("fechaHora") or latest.get("date") or latest.get("timestamp") or "",
            "latestStatus": latest.get("status") or "",
            "totalRecords": len(history),
            "history": list(reversed(history)),   # newest first
        })

    # Sort vehicles by most recent date descending
    result.sort(key=lambda x: x["latestDate"], reverse=True)

    return result
