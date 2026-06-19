from fastapi import APIRouter, Query
from services.asset_sheets_service import get_vehicle_history, get_debug_info

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("")
def list_assets(
    search: str = Query(None),
    status: str = Query(None),
):
    assets = get_vehicle_history()

    if search:
        s = search.lower()
        assets = [
            a for a in assets
            if s in a["vehicleId"].lower()
            or s in (a["latestRecord"].get("status") or "").lower()
            or s in (a["latestRecord"].get("location") or "").lower()
            or s in (a["latestRecord"].get("action") or "").lower()
        ]

    if status:
        assets = [
            a for a in assets
            if (a["latestRecord"].get("status") or "").lower() == status.lower()
        ]

    return assets


@router.get("/debug")
def debug_assets():
    return get_debug_info()
