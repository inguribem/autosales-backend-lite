from database import get_connection


def get_current_location(vin: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM movement_inventory
        WHERE vin = %s
    """, (vin,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "vin": row[1],
        "current_location": row[9],
        "vin": row[1],
        "last_responsible_name": row[14],
        "last_responsible_phone": row[13],
        "updated_at": row[16],
    }


def get_movement_history(vin: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM movement_history
        WHERE vin_reported = %s
        ORDER BY created_at DESC
    """, (vin,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": r[0],
            "vehicle_id": r[1],
            "vin_reported": r[2],
            "location_reported": r[3],
            "reported_by": r[4],
            "original_message": r[5],
            "message_type": r[6],
            "voice_link": r[7],
            "created_at": r[8],
        }
        for r in rows
    ]