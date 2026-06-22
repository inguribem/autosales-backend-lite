from database import get_connection
import traceback


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
