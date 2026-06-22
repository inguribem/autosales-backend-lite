from fastapi import APIRouter, Query
from services.invoice_service import get_all_invoices, get_all_invoice_queue

router = APIRouter(prefix="/invoices", tags=["invoices"])
router_queue = APIRouter(prefix="/invoice_queue", tags=["invoice_queue"])


@router.get("")
def list_invoices(status: str = Query(None)):
    return get_all_invoices(status=status)


@router.get("/queue")
def list_invoice_queue_nested(status: str = Query(None)):
    return get_all_invoice_queue(status=status)


@router_queue.get("")
def list_invoice_queue(status: str = Query(None)):
    return get_all_invoice_queue(status=status)
