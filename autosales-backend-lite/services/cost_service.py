from database import get_connection


def add_cost_entry(vin: str, entry):
    data = entry.model_dump()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cost_history (vehicle_vin, field_name, amount, description)
        VALUES (%s, %s, %s, %s)
    """, (
        vin,
        data["field_name"],
        data["amount"],
        data.get("description")
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "added"}


def get_cost_summary(vin: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vehicle_vin, buyer_fee, inside_fees, floor_plan_fees,
               detailing, mechanic, bodyshop, grua, parts, others
        FROM cost_mgmt
        WHERE vehicle_vin = %s
    """, (vin,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    columns = [
        "vehicle_vin", "buyer_fee", "inside_fees", "floor_plan_fees",
        "detailing", "mechanic", "bodyshop", "grua", "parts", "others"
    ]

    return dict(zip(columns, row))


def get_cost_history(vin: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vehicle_vin, field_name, amount, description, created_at
        FROM cost_history
        WHERE vehicle_vin = %s
        ORDER BY created_at DESC
    """, (vin,))

    rows = cursor.fetchall()
    columns = ["vehicle_vin", "field_name", "amount", "description", "created_at"]

    cursor.close()
    conn.close()

    return [dict(zip(columns, row)) for row in rows]

def get_cost_types():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT field_name
        FROM cost_mgmt
        ORDER BY field_name
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in rows]


def add_cost_entry(vin: str, entry):
    """
    Inserta un registro en cost_history.
    Gracias al trigger, actualiza automáticamente cost_mgmt.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cost_history (vehicle_vin, field_name, amount, description)
        VALUES (%s, %s, %s, %s)
    """, (
        vin,
        entry.field_name,
        entry.amount,
        entry.description,
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "added"}