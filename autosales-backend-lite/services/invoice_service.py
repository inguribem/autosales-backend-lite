from database import get_connection
import traceback
from typing import Optional


def get_all_invoices(status: str = None) -> list[dict]:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM invoices"
        params = []

        if status:
            query += " WHERE status = %s"
            params.append(status)

        query += " ORDER BY id ASC"

        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()

        return [dict(zip(columns, row)) for row in rows]
    except Exception:
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close()


def update_invoice(invoice_id: int, fields: dict) -> Optional[dict]:
    ALLOWED = {"vin_partial", "vehicle_make", "vehicle_model", "status"}
    updates = {k: v for k, v in fields.items() if k in ALLOWED and v is not None}
    if not updates:
        return None
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        set_clause = ", ".join(f"{col} = %s" for col in updates)
        values = list(updates.values()) + [invoice_id]
        cursor.execute(
            f"UPDATE invoices SET {set_clause} WHERE id = %s RETURNING *",
            values,
        )
        row = cursor.fetchone()
        conn.commit()
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        return dict(zip(columns, row))
    except Exception:
        traceback.print_exc()
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def get_all_invoice_queue(status: str = None) -> list[dict]:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM invoice_queue"
        params = []

        if status:
            query += " WHERE status = %s"
            params.append(status)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()

        return [dict(zip(columns, row)) for row in rows]
    except Exception:
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close()
