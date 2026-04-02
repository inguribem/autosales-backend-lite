from database import get_connection
from services.slack_notification_service import send_slack_notification
from services.cost_service import add_cost_entry

# vehicle_service.py

from database import get_connection

# ✅ 1. HELPERS (AQUÍ VA EL NORMALIZADOR)
def map_status(status: str):
    if not status:
        return "purchase"

    status = status.lower()

    if status in ["new", "purchase"]:
        return "purchase"
    if status in ["repair", "in_repair"]:
        return "repair"
    if status in ["done", "ready"]:
        return "done"

    return "purchase"


def normalize_vehicle(row: dict):
    return {
        "id": row["vin"],
        "vin": row["vin"],
        "year": row["year"] or 0,
        "make": row["make"] or "",
        "model": row["model"] or "",
        "trim": row["trim"] or "",
        "purchasePrice": float(row["price_purchase"]) if row["price_purchase"] else None,
        "mileage": row["miles"] or None,
        "status": map_status(row["status"]),
        "stockNumber": row["vin"][-6:] if row["vin"] else "",
    }


# -------------------------
# CREATE VEHICLE
# -------------------------

# Valores por defecto (puedes cambiarlos)
DEFAULT_COSTS = {
    "buyer_fee": 100,
    "inside_fees": 0,
    "floor_plan_fees": 0,
    "detailing": 0,
    "mechanic": 50,
    "bodyshop": 0,
    "grua": 0,
    "parts": 0
}

def create_vehicle(vehicle: dict):
    vin = vehicle["vin"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vehicles
        (vin, year, make, model, trim, price_purchase, miles, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (vin) DO NOTHING
    """, (
        vin,
        vehicle.get("year"),
        vehicle.get("make"),
        vehicle.get("model"),
        vehicle.get("trim"),
        vehicle.get("purchasePrice"),  # 👈 FIX
        vehicle.get("mileage"),        # 👈 FIX
        vehicle.get("status", "purchase")
    ))

    conn.commit()
    cursor.close()
    conn.close()

    send_slack_notification(vehicle)

    # DEFAULT COSTS
    for field_name, amount in DEFAULT_COSTS.items():
        add_cost_entry(vin, {
            "field_name": field_name,
            "amount": amount,
            "description": "Default"
        })

    return {"status": "saved"}


# -------------------------
# GET INVENTORY
# -------------------------
def get_inventory(search=None, make=None, year=None, status=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, vin, year, make, model, price_purchase,
               miles, trim, dealer_name, city, state, status
        FROM vehicles
        WHERE 1=1
    """

    params = []

    if search:
        query += " AND (vin ILIKE %s OR model ILIKE %s OR make ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if make:
        query += " AND make ILIKE %s"
        params.append(f"%{make}%")

    if year:
        query += " AND year = %s"
        params.append(year)

    if status:
        query += " AND LOWER(status) = LOWER(%s)"
        params.append(status)

    query += " ORDER BY year DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    vehicles = [dict(zip(columns, row)) for row in rows]

    # 🔥 NORMALIZACIÓN AQUÍ
    return [normalize_vehicle(v) for v in vehicles]


# -------------------------
# UPDATE VEHICLE
# -------------------------
def update_vehicle(vin: str, vehicle: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE vehicles
        SET year=%s,
            make=%s,
            model=%s,
            trim=%s,
            price_purchase=%s,
            miles=%s,
            status=%s
        WHERE vin=%s
    """, (
        vehicle.get("year"),
        vehicle.get("make"),
        vehicle.get("model"),
        vehicle.get("trim"),
        vehicle.get("purchasePrice"),  # FIX
        vehicle.get("mileage"),        # FIX
        vehicle.get("status"),
        vin
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "updated"}


# -------------------------
# DELETE VEHICLE
# -------------------------
def delete_vehicle(vin: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vehicles WHERE vin=%s", (vin,))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "deleted"}