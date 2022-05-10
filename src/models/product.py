from pydantic import BaseModel
from src.models.token import Token
from src.models.user import UserOut
from typing import Optional, List
from datetime import datetime


# class Product(BaseModel):
#     id: int
#     manga_id: int
#     volume: Optional[int]
#     chapter: Optional[int]
#     description: Optional[str]
#     publisher: Optional[str]
#     language: Optional[str]
#     translator: Optional[str]
#     price_rub: int
#     quantity: int = 0


class ProductCreate(BaseModel):
    volume: Optional[int]
    chapter: Optional[int]
    description: Optional[str]
    publisher: Optional[str]
    language: Optional[str]
    translator: Optional[str]
    price_rub: int
    quantity: int = 0


class ProductOut(BaseModel):
    id: int
    manga_id: int
    volume: Optional[int]
    chapter: Optional[int]
    description: Optional[str]
    publisher: Optional[str]
    language: Optional[str]
    translator: Optional[str]
    price_rub: int
    quantity: int = 0

    class Config:
        orm_mode = True


class ProductEdit(BaseModel):
    volume: Optional[int]
    chapter: Optional[int]
    description: Optional[str]
    publisher: Optional[str]
    language: Optional[str]
    translator: Optional[str]
    price_rub: Optional[int]
    quantity: Optional[int]
