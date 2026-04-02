from fastapi import APIRouter, Query, HTTPException
from database import get_connection
from services.vin_service import decode_vin
from services.cost_service import add_cost_entry, get_costs_for_vin
from services.vehicle_service import (
    create_vehicle,
    get_inventory,
    update_vehicle,
    delete_vehicle,
    get_vehicle_by_id
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
def create(vehicle: dict):
    return create_vehicle(vehicle)


# -------------------------
# UPDATE VEHICLE
# -------------------------
@router.patch("/{id}")
def update(id: str, vehicle: dict):
    return update_vehicle(id, vehicle)


# -------------------------
# DELETE VEHICLE
# -------------------------
@router.delete("/{id}")
def delete(id: str):
    return delete_vehicle(id)

@router.get("/vehicles")
def get_vehicles():
    return get_inventory()
    

@router.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: str):
    vehicle = get_vehicle_by_id(vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle


# -------------------------
# GET VEHICLE DETAILS BY VIN
# -------------------------
@router.get("/vehicles/{vin}")
def get_vehicle(vin: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, vin, year, make, model, trim, price_purchase, miles,
               dealer_name, city, state, status, stock_number
        FROM vehicles
        WHERE vin=%s
    """, (vin,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    columns = ["id", "vin", "year", "make", "model", "trim", "purchasePrice",
               "mileage", "dealer_name", "city", "state", "status", "stockNumber"]
    return dict(zip(columns, row))


# -------------------------
# GET VEHICLE LOCATION BY VIN
# -------------------------
@router.get("/locations/{vin}")
def get_vehicle_location(vin: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT city, state, dealer_name FROM vehicles WHERE vin=%s", (vin,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    columns = ["city", "state", "dealer_name"]
    return dict(zip(columns, row))


# -------------------------
# GET COSTS BY VIN
# -------------------------
@router.get("/costs")
def get_costs(vin: str = Query(..., description="VIN del vehículo")):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT field_name, amount, description FROM costs WHERE vehicle_vin=%s", (vin,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Siempre devolvemos un array, incluso si está vacío
    return [dict(zip(["field_name", "amount", "description"], row)) for row in rows]


# -------------------------
# DECODE VIN
# -------------------------
@router.get("/vehicles/decode/{vin}")
def decode_vehicle_vin(vin: str):
    try:
        decoded = decode_vin(vin)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode VIN: {str(e)}")