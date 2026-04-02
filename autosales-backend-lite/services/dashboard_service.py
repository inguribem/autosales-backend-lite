from database import get_connection

def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Total vehicles
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total_vehicles = cursor.fetchone()[0]

    # Status counts
    cursor.execute("""
        SELECT status, COUNT(*)
        FROM vehicles
        GROUP BY status
    """)
    status_rows = cursor.fetchall()

    purchase = 0
    repair = 0
    done = 0

    for status, count in status_rows:
        if status == "purchase":
            purchase = count
        elif status == "repair":
            repair = count
        elif status == "done":
            done = count

    # Total inventory value
    cursor.execute("SELECT COALESCE(SUM(price_purchase), 0) FROM vehicles")
    total_inventory_value = cursor.fetchone()[0]

    # Total costs (history)
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM cost_history")
    total_costs = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "totalVehicles": total_vehicles,
        "purchaseCount": purchase,
        "repairCount": repair,
        "doneCount": done,
        "totalInventoryValue": float(total_inventory_value),
        "totalCosts": float(total_costs),
    }