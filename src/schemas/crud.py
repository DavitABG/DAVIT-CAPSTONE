from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CustomerRead(BaseModel):
    id: str
    company_name: str
    street: Optional[str]
    unit: Optional[str]
    country: Optional[str]
    city: Optional[str]
    is_active: bool

    class Config:
        orm_mode = True


class ProductRead(BaseModel):
    product_id: int
    name: str
    price: float

    class Config:
        orm_mode = True


class SaleRead(BaseModel):
    id: int
    date: datetime
    business_unit: Optional[int]
    customer_id: str
    location_id: Optional[int]
    product_id: int
    qty: int

    class Config:
        orm_mode = True
