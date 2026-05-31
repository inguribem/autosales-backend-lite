import os
import requests

SHEETS_API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY")
APPOINTMENTS_SHEET_ID = os.getenv("APPOINTMENTS_SHEET_ID")

# Google Forms response sheet — column order:
# A: Timestamp | B: Name | C: Company | D: Email | E: Phone | F: Date | G: Time | H: Notes
APPOINTMENTS_RANGE = "Sheet1!A:H"


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
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"[sheets] Error fetching appointments: {e}")
        return []

    rows = data.get("values", [])
    if len(rows) < 2:
        return []

    appointments = []
    for i, row in enumerate(rows[1:], start=1):
        # Pad to 8 columns in case trailing empty cells are omitted by Sheets API
        padded = row + [""] * (8 - len(row))
        appointments.append({
            "id": str(i),
            "timestamp":      padded[0],
            "customerName":   padded[1],
            "company":        padded[2],
            "email":          padded[3],
            "customerPhone":  padded[4],
            "date":           padded[5],
            "time":           padded[6],
            "notes":          padded[7],
        })

    return appointments
