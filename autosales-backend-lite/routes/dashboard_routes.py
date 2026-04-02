from fastapi import APIRouter
from services.dashboard_service import get_dashboard_stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def stats():
    return get_dashboard_stats()