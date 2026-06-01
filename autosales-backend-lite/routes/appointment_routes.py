from fastapi import APIRouter, Query, HTTPException
from services.sheets_service import (
    get_appointments_from_sheet,
    append_appointment,
    update_appointment,
    delete_appointment,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("")
def list_appointments(search: str = Query(None)):
    appointments = get_appointments_from_sheet()
    if search:
        s = search.lower()
        appointments = [
            a for a in appointments
            if s in (a.get("customerName") or "").lower()
            or s in (a.get("email") or "").lower()
            or s in (a.get("customerPhone") or "")
            or s in (a.get("company") or "").lower()
        ]
    return appointments


@router.post("")
def create_appointment(data: dict):
    try:
        return append_appointment(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{appointment_id}")
def edit_appointment(appointment_id: int, data: dict):
    try:
        return update_appointment(appointment_id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{appointment_id}")
def remove_appointment(appointment_id: int):
    try:
        return delete_appointment(appointment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
