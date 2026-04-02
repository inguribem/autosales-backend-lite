from fastapi import APIRouter
from database import get_connection

router = APIRouter(prefix="/locations", tags=["Locations"])


# -------------------------
# GET LAST LOCATION BY VIN
# -------------------------
@router.get("/{vin}")
def get_location(vin: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT address, updated_at
        FROM vehicle_locations
        WHERE vin = %s
        ORDER BY updated_at DESC
        LIMIT 1
    """, (vin,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    # ✅ IMPORTANTE: nunca retornar None
    if not row:
        return {}

    return {
        "address": row[0],
        "updatedAt": row[1]
    }