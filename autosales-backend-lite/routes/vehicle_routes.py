from fastapi import APIRouter, Query
from typing import Optional
from services import vehicle_service, vin_service

router = APIRouter(prefix="/vehicles")

@router.get("/vin/{vin}")
def lookup_vin(vin: str):
    return vin_service.decode_vin(vin)


@router.post("/")
def add_vehicle(vehicle: dict):
    return vehicle_service.create_vehicle(vehicle)


@router.get("/inventory")
def get_inventory(
    search: Optional[str] = Query(None),
    make: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    status: Optional[str] = Query(None)
):
    return vehicle_service.get_inventory(search, make, year, status)


@router.put("/{vin}")
def update_vehicle(vin: str, vehicle: dict):
    return vehicle_service.update_vehicle(vin, vehicle)


@router.delete("/{vin}")
def delete_vehicle(vin: str):
    return vehicle_service.delete_vehicle(vin)


