from fastapi import APIRouter, Query, HTTPException, Depends
from services.vin_service import decode_vin
from services.auth_service import get_current_user
from services.vehicle_service import (
    create_vehicle,
    get_inventory,
    update_vehicle,
    delete_vehicle,
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


# -------------------------
# GET ALL VEHICLES
# -------------------------
@router.get("")
def get_vehicles(
    search: str = Query(None),
    make: str = Query(None),
    year: int = Query(None),
    status: str = Query(None)
):
    return get_inventory(search, make, year, status)


# -------------------------
# GET SINGLE VEHICLE
# -------------------------
@router.get("/{id}")
def get_vehicle(id: str):
    vehicles = get_inventory()
    for v in vehicles:
        if v["id"] == id:
            return v
    return {"error": "Vehicle not found"}


# -------------------------
# CREATE VEHICLE
# -------------------------
@router.post("")
def create(vehicle: dict, _user: dict = Depends(get_current_user)):
    return create_vehicle(vehicle)


# -------------------------
# UPDATE VEHICLE
# -------------------------
@router.patch("/{id}")
def update(id: str, vehicle: dict, _user: dict = Depends(get_current_user)):
    return update_vehicle(id, vehicle)


# -------------------------
# DELETE VEHICLE
# -------------------------
@router.delete("/{id}")
def delete(id: str, _user: dict = Depends(get_current_user)):
    return delete_vehicle(id)


# -------------------------
# DECODE VIN
# -------------------------
@router.get("/decode/{vin}")
def decode_vehicle_vin(vin: str):
    try:
        decoded = decode_vin(vin)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode VIN: {str(e)}")