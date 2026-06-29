from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.invoice_service import get_all_invoices, get_all_invoice_queue, update_invoice

router = APIRouter(prefix="/invoices", tags=["invoices"])
router_queue = APIRouter(prefix="/invoice_queue", tags=["invoice_queue"])


class InvoiceUpdate(BaseModel):
    vin_partial: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    status: Optional[str] = None


@router.get("")
def list_invoices(status: str = Query(None)):
    return get_all_invoices(status=status)


@router.patch("/{invoice_id}")
def patch_invoice(invoice_id: int, body: InvoiceUpdate):
    result = update_invoice(invoice_id, body.model_dump(exclude_none=True))
    if result is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return result


@router.get("/queue")
def list_invoice_queue_nested(status: str = Query(None)):
    return get_all_invoice_queue(status=status)


@router_queue.get("")
def list_invoice_queue(status: str = Query(None)):
    return get_all_invoice_queue(status=status)
