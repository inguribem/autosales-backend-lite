from fastapi import APIRouter, Query
from services.sheets_service import get_appointments_from_sheet

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("")
def list_appointments(
    search: str = Query(None, description="Filter by name, email, or phone"),
):
    appointments = get_appointments_from_sheet()

    if search:
        s = search.lower()
        appointments = [
            a for a in appointments
            if s in a.get("customerName", "").lower()
            or s in a.get("email", "").lower()
            or s in a.get("customerPhone", "")
            or s in a.get("company", "").lower()
        ]

    return appointments
