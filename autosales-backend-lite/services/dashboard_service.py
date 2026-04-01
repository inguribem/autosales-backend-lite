from database import get_connection

def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Total vehicles + status counts
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'purchase') as purchase,
            COUNT(*) FILTER (WHERE status = 'repair') as repair,
            COUNT(*) FILTER (WHERE status = 'done') as done,
            COALESCE(SUM(price_purchase), 0) as total_value
        FROM vehicles
    """)

    vehicle_data = cursor.fetchone()

    # Total costs desde history
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM cost_history
    """)

    total_costs = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "totalVehicles": vehicle_data[0],
        "purchaseCount": vehicle_data[1],
        "repairCount": vehicle_data[2],
        "doneCount": vehicle_data[3],
        "totalInventoryValue": float(vehicle_data[4] or 0),
        "totalCosts": float(total_costs or 0)
    }