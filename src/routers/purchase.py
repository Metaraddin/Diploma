from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.purchase import PurchaseOut
from src.repositories import purchase
from src.repositories import product
from typing import List


router = APIRouter(prefix="/purchase", tags=["Purchase"])
security = HTTPBearer()


@router.get("/all/", status_code=200, response_model=List[PurchaseOut])
async def get_all(limit: int = 100, skip: int = 0, session: Session = Depends(get_db)):
    """
    Получение всей истории покупок
    """
    return purchase.all_purchase(s=session, limit=limit, skip=skip)


@router.get("/user/{user_id}", status_code=200, response_model=List[PurchaseOut])
async def get_all_from_user(user_id: int, session: Session = Depends(get_db)):
    """
    Получение истории покупок пользователя
    """
    return purchase.all_user_purchase(user_id=user_id, s=session)


@router.patch("/{id}", status_code=200, response_model=PurchaseOut)
async def cancel_purchase(id: int, session: Session = Depends(get_db)):
    """
    Отмена покупки
    """
    return product.cancel_purchase(purchase_id=id, s=session)