from services.vehicle_service import create_vehicle
from services.cost_service import add_cost_entry, get_cost_summary, get_cost_history

# -------------------------
# 1️⃣ Crear vehículo
# -------------------------
vehicle = {
    "vin": "TEST456",
    "make": "Honda",
    "model": "Civic",
    "year": 2023,
    "trim": "EX",
    "price_purchase": 22000,
    "miles": 0,
    "dealer_name": "Demo Dealer",
    "city": "Testville",
    "state": "TS",
    "status": "new"
}

print("=== Creando vehículo ===")
create_vehicle(vehicle)

# -------------------------
# 2️⃣ Revisar costos iniciales (por defecto)
# -------------------------
print("\n=== Costos iniciales (resumen) ===")
summary = get_cost_summary("TEST456")
print(summary)

print("\n=== Historial de costos iniciales ===")
history = get_cost_history("TEST456")
for h in history:
    print(h)

# -------------------------
# 3️⃣ Agregar un costo extra
# -------------------------
print("\n=== Agregando costo extra: mechanic 500 ===")
add_cost_entry("TEST456", {
    "field_name": "mechanic",
    "amount": 500,
    "description": "Engine repair"
})

# -------------------------
# 4️⃣ Revisar resumen y historial actualizados
# -------------------------
print("\n=== Costos después de agregar mechanic 500 ===")
summary = get_cost_summary("TEST456")
print(summary)

print("\n=== Historial actualizado ===")
history = get_cost_history("TEST456")
for h in history:
    print(h)