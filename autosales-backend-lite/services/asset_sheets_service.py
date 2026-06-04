import os
import re
import json
from collections import defaultdict

import gspread
from google.oauth2.service_account import Credentials

ASSET_SHEET_ID   = os.getenv("ASSET_SHEET_ID")
INVENTARIO_TAB   = "Inventario_Actual"
HISTORICO_TAB    = "Historico_Movimientos"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ── Header maps ───────────────────────────────────────────────────────────────

INVENTARIO_MAP = {
    "id_vehiculo":           "vehicleId",
    "id vehiculo":           "vehicleId",
    "id_vehiculos":          "vehicleId",
    "id vehiculos":          "vehicleId",
    "tag":                   "tag",
    "marca":                 "marca",
    "make":                  "marca",
    "modelo":                "modelo",
    "model":                 "modelo",
    "color":                 "color",
    "year":                  "year",
    "año":                   "year",
    "anio":                  "year",
    "status":                "status",
    "estado":                "status",
    "ubicacion":             "ubicacion",
    "ubicación":             "ubicacion",
    "location":              "ubicacion",
    "ultima_actualizacion":  "ultimaActualizacion",
    "última_actualización":  "ultimaActualizacion",
    "ultima actualizacion":  "ultimaActualizacion",
    "última actualización":  "ultimaActualizacion",
    "ubicacion_actual":      "ubicacionActual",
    "ubicación_actual":      "ubicacionActual",
    "ubicacion actual":      "ubicacionActual",
    "telefono_responsable":  "telefonoResponsable",
    "teléfono_responsable":  "telefonoResponsable",
    "telefono responsable":  "telefonoResponsable",
    "ultimo_responsable":    "ultimoResponsable",
    "último_responsable":    "ultimoResponsable",
    "ultimo responsable":    "ultimoResponsable",
}

HISTORICO_MAP = {
    "id_vehiculos":         "vehicleId",
    "id vehiculos":         "vehicleId",
    "id_vehiculo":          "vehicleId",
    "id vehiculo":          "vehicleId",
    "vehiculo":             "vehicleId",
    "vehicle":              "vehicleId",
    "fecha_hora":           "fechaHora",
    "fecha hora":           "fechaHora",
    "fecha":                "date",
    "date":                 "date",
    "fecha_movimiento":     "date",
    "marca temporal":       "timestamp",
    "timestamp":            "timestamp",
    "estado":               "status",
    "status":               "status",
    "ubicacion_reportada":  "ubicacion",
    "ubicación_reportada":  "ubicacion",
    "ubicacion reportada":  "ubicacion",
    "ubicacion":            "ubicacion",
    "ubicación":            "ubicacion",
    "location":             "ubicacion",
    "mensaje_original":     "mensaje",
    "mensaje original":     "mensaje",
    "mensaje":              "mensaje",
    "responsable":          "responsable",
    "assigned_to":          "responsable",
    "notas":                "notes",
    "notes":                "notes",
}


def _ci(h: str, map_: dict) -> str:
    return map_.get(h.strip().lower(), h.strip().lower())


# ── Auth ──────────────────────────────────────────────────────────────────────

def _get_spreadsheet() -> gspread.Spreadsheet:
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON env var not set")
    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(ASSET_SHEET_ID)


# ── Readers ───────────────────────────────────────────────────────────────────

def _read_inventario(spreadsheet: gspread.Spreadsheet) -> dict[str, dict]:
    """Returns {vehicleId: vehicle_detail_dict} from Inventario_Actual."""
    try:
        ws = spreadsheet.worksheet(INVENTARIO_TAB)
        rows = ws.get_all_values()
    except Exception as e:
        print(f"[asset_sheets] Error reading {INVENTARIO_TAB}: {e}")
        return {}

    if len(rows) < 2:
        return {}

    headers = [_ci(h, INVENTARIO_MAP) for h in rows[0]]
    print(f"[asset_sheets] Inventario columns: {headers}")

    result: dict[str, dict] = {}
    for row in rows[1:]:
        padded = row + [""] * (len(headers) - len(row))
        record = dict(zip(headers, padded))
        vid = record.get("vehicleId")
        if vid:
            result[vid] = record
    return result


def _read_historico(spreadsheet: gspread.Spreadsheet) -> dict[str, list[dict]]:
    """Returns {vehicleId: [records newest-first]} from Historico_Movimientos."""
    try:
        ws = spreadsheet.worksheet(HISTORICO_TAB)
        rows = ws.get_all_values()
    except Exception as e:
        print(f"[asset_sheets] Error reading {HISTORICO_TAB}: {e}")
        return {}

    if len(rows) < 2:
        return {}

    headers = [_ci(h, HISTORICO_MAP) for h in rows[0]]
    print(f"[asset_sheets] Historico columns: {headers}")

    groups: dict[str, list[dict]] = defaultdict(list)
    for i, row in enumerate(rows[1:], start=1):
        padded = row + [""] * (len(headers) - len(row))
        record = dict(zip(headers, padded))
        record["rowId"] = str(i)
        vid = record.get("vehicleId") or f"row-{i}"
        groups[vid].append(record)

    # Reverse each group so newest is first
    return {vid: list(reversed(recs)) for vid, recs in groups.items()}


# ── Public API ────────────────────────────────────────────────────────────────

def get_vehicle_history() -> list[dict]:
    """
    Joins Inventario_Actual (vehicle details) with Historico_Movimientos
    (movement records) on ID_Vehiculo. Returns one entry per vehicle.
    """
    if not ASSET_SHEET_ID:
        print("[asset_sheets] ASSET_SHEET_ID not set")
        return []

    try:
        spreadsheet = _get_spreadsheet()
    except Exception as e:
        print(f"[asset_sheets] Auth error: {e}")
        return []

    inventario = _read_inventario(spreadsheet)   # {vehicleId: details}
    historico  = _read_historico(spreadsheet)    # {vehicleId: [records]}

    print(f"[asset_sheets] Inventario IDs: {list(inventario.keys())}")
    print(f"[asset_sheets] Historico IDs:  {list(historico.keys())}")

    # Four-level lookup to handle casing, whitespace, punctuation, and leading zeros
    # e.g. "042507" (text) vs "42507" (number), "VH-001" vs "VH001"
    def _alphanum(s: str) -> str:
        return re.sub(r'[^a-z0-9]', '', s.lower())

    def _numeric(s: str) -> str:
        """Strip leading zeros for purely numeric IDs: '042507' → '42507'."""
        stripped = s.strip()
        return str(int(stripped)) if stripped.isdigit() else stripped

    inv_norm     = {k.strip().lower(): v for k, v in inventario.items()}
    inv_alphanum = {_alphanum(k): v      for k, v in inventario.items()}
    inv_numeric  = {_numeric(k): v       for k, v in inventario.items()}

    def _inv(vid: str) -> dict:
        result = (
            inventario.get(vid)
            or inv_norm.get(vid.strip().lower())
            or inv_alphanum.get(_alphanum(vid))
            or inv_numeric.get(_numeric(vid))
            or {}
        )
        if not result:
            print(f"[asset_sheets] No inventory match for vid='{vid}' "
                  f"(norm='{vid.strip().lower()}', alphanum='{_alphanum(vid)}', numeric='{_numeric(vid)}')")
        return result

    # Union of all vehicle IDs from both tabs
    all_ids = set(inventario.keys()) | set(historico.keys())

    result = []
    for vid in all_ids:
        details = _inv(vid)
        history = historico.get(vid, [])
        latest  = history[0] if history else {}

        result.append({
            "vehicleId":           vid,
            "tag":                 details.get("tag", ""),
            "marca":               details.get("marca", ""),
            "modelo":              details.get("modelo", ""),
            "color":               details.get("color", ""),
            "year":                details.get("year", ""),
            "ultimaActualizacion": details.get("ultimaActualizacion", ""),
            "ubicacionActual":     details.get("ubicacionActual", ""),
            "telefonoResponsable": details.get("telefonoResponsable", ""),
            "ultimoResponsable":   details.get("ultimoResponsable", ""),
            # Status: prefer inventory's current status, fall back to latest movement
            "latestStatus": details.get("status") or latest.get("status") or "",
            "latestDate":   latest.get("fechaHora") or latest.get("date") or latest.get("timestamp") or "",
            "latestRecord": latest,
            "totalRecords": len(history),
            "history":      history,
        })

    # Sort by most recent movement date descending
    result.sort(key=lambda x: x["latestDate"], reverse=True)
    return result
