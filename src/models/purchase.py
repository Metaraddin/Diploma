from pydantic import BaseModel
from src.models.token import Token
from src.models.user import UserOut
from typing import Optional, List
from datetime import datetime


class PurchaseOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    price: int
    datetime: datetime
    canceled: bool

    class Config:
        orm_mode = True


class PurchaseCreate(BaseModel):
    user_id: int
    product_id: int
    price: int
    datetime: datetime
