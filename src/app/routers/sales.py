from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Transaction
from src.schemas.crud import SaleRead

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=List[SaleRead])
def query_sales(
        customer_id: Optional[str] = None,
        start_date: Optional[date] = Query(None, description="YYYY-MM-DD"),
        end_date: Optional[date] = Query(None, description="YYYY-MM-DD"),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
):
    q = db.query(Transaction)
    if customer_id:
        q = q.filter(Transaction.customer_id == customer_id)
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)
    return q.offset(skip).limit(limit).all()


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    prod = db.query(Transaction).filter(Transaction.id == sale_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod
