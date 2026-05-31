import os
import requests

SHEETS_API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY")
APPOINTMENTS_SHEET_ID = os.getenv("APPOINTMENTS_SHEET_ID")
APPOINTMENTS_RANGE = "Hoja 1!A:Z"  # grab all columns regardless of count

# Maps whatever Google Form header text → canonical API field name
# Covers Spanish and English variations
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
}


def _canonical(header: str) -> str:
    key = header.strip().lower()
    return HEADER_MAP.get(key, key)


def get_appointments_from_sheet() -> list[dict]:
    if not SHEETS_API_KEY or not APPOINTMENTS_SHEET_ID:
        print("[sheets] GOOGLE_SHEETS_API_KEY or APPOINTMENTS_SHEET_ID not set")
        return []

    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/"
        f"{APPOINTMENTS_SHEET_ID}/values/{APPOINTMENTS_RANGE}"
        f"?key={SHEETS_API_KEY}"
    )

    try:
        response = requests.get(url, timeout=10)
        if not response.ok:
            print(f"[sheets] HTTP {response.status_code}: {response.text}")
            return []
        data = response.json()
    except requests.RequestException as e:
        print(f"[sheets] Request failed: {e}")
        return []

    rows = data.get("values", [])
    if len(rows) < 2:
        return []

    # Row 1 = headers; map each to a canonical name
    headers = [_canonical(h) for h in rows[0]]
    print(f"[sheets] Columns detected: {headers}")

    appointments = []
    for i, row in enumerate(rows[1:], start=1):
        padded = row + [""] * (len(headers) - len(row))
        record = dict(zip(headers, padded))
        record["id"] = str(i)
        appointments.append(record)

    return appointments
