from fastapi import FastAPI
from routes import vehicle_routes, auctions, service_orders, catalog, reports, slack, cost_routes, auth_routes, dashboard_routes, location_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (IMPORTANTE para Streamlit)
origins = [
    "https://autosales-frontend-lite.onrender.com",
    "http://localhost:3000",  # opcional para local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicle_routes.router)
app.include_router(auctions.router)
app.include_router(service_orders.router)
app.include_router(catalog.router)
app.include_router(reports.router)
app.include_router(slack.router)
app.include_router(cost_routes.router)
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(location_routes.router)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}
