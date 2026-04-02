from fastapi import APIRouter, HTTPException, Query
from typing import List

from schemas.cost_schema import (
    CostEntryCreate,
    CostResponse,
    CostHistoryResponse
)

from services import cost_service

router = APIRouter(prefix="/costs", tags=["Costs"])


# ✅ ESTE ES EL QUE USA TU FRONTEND
@router.get("")
def get_costs(vin: str = Query(...)):
    return cost_service.get_cost_history(vin) or []

@router.get("/types")
def get_cost_types():
    return cost_service.get_cost_types()


# -------------------------
# ADD COST (ledger)
# -------------------------
@router.post("/{vin}/add")
def add_cost(vin: str, entry: CostEntryCreate):
    return cost_service.add_cost_entry(vin, entry)


# -------------------------
# GET SUMMARY
# -------------------------
@router.get("/{vin}", response_model=CostResponse)
def get_cost(vin: str):
    result = cost_service.get_cost_summary(vin)

    if not result:
        raise HTTPException(status_code=404, detail="Cost not found")

    return result


# -------------------------
# GET HISTORY
# -------------------------
@router.get("/{vin}/history", response_model=List[CostHistoryResponse])
def get_history(vin: str):
    return cost_service.get_cost_history(vin)