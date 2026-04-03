from fastapi import APIRouter, Query
from services import location_service

router = APIRouter(prefix="/locations", tags=["Locations"])


# 🔹 Current Location (movement_inventory)
@router.get("")
def get_location(vin: str = Query(...)):
    return location_service.get_current_location(vin)


# 🔹 Movement History
@router.get("/history")
def get_history(vin: str = Query(...)):
    return location_service.get_movement_history(vin)