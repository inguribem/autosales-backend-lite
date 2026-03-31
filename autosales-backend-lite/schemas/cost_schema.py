from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# -------------------------
# ENUM de tipos de costo 🔥
# -------------------------
CostField = Literal[
    "buyer_fee",
    "inside_fees",
    "floor_plan_fees",
    "detailing",
    "mechanic",
    "bodyshop",
    "grua",
    "parts"
]


# -------------------------
# INSERT (ledger)
# -------------------------
class CostEntryCreate(BaseModel):
    field_name: CostField
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


# -------------------------
# RESPONSE resumen
# -------------------------
class CostResponse(BaseModel):
    vehicle_vin: str

    buyer_fee: float
    inside_fees: float
    floor_plan_fees: float
    detailing: float
    mechanic: float
    bodyshop: float
    grua: float
    parts: float


# -------------------------
# HISTORY RESPONSE
# -------------------------
class CostHistoryResponse(BaseModel):
    vehicle_vin: str
    field_name: CostField
    amount: float
    description: Optional[str]
    created_at: datetime