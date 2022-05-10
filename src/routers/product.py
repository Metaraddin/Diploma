from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.product import ProductOut, ProductCreate, ProductEdit
from src.models.purchase import PurchaseOut
from src.repositories import product
from typing import List


router = APIRouter(prefix="/product", tags=["Product"])
security = HTTPBearer()


@router.post('/', status_code=200, response_model=ProductOut)
async def create_product(manga_id: int, product_info: ProductCreate,
                         session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Создание товара на основе типа манги
    """
    return product.create_product(manga_id=manga_id, product_info=product_info, s=session)


@router.patch('/{id}', status_code=200, response_model=ProductOut)
async def edit_product(id: int, product_info: ProductEdit,
                       session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Изменение товара
    """
    return product.edit_product(product_id=id, product_info=product_info, s=session)


@router.get('/{id}', status_code=200, response_model=ProductOut)
async def get_product(id: int, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Получение товара по id
    """
    return product.get_product(product_id=id, s=session)


@router.get('/manga/{manga_id}', status_code=200, response_model=List[ProductOut])
async def get_products_by_manga(manga_id: int, limit: int = 100, skip: int = 0,
                                session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Получение всех товаров на основе манги
    """
    return product.get_product_by_manga(manga_id, session)


@router.get("/all/", status_code=200, response_model=List[ProductOut])
async def get_all_product(limit: int = 100, skip: int = 0, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Получение всех товаров
    """
    return product.get_all_product(s=session)


@router.delete('/{id}', status_code=200, response_model=ProductOut)
async def delete_product(id: int, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Удаление товара
    """
    return product.delete_product(product_id=id, s=session)


@router.get('/{id}/price/', status_code=200, response_model=int)
async def get_price_with_discount(id: int, user_id: int,
                                  session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Цена товара с учётом скидки пользователя
    """
    return product.get_price_from_user(user_id=user_id, product_id=id, s=session)


@router.patch('/buy/', status_code=200, response_model=PurchaseOut)
async def buy_product(id: int, user_id: int,
                      session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Купить товар с учётом скидки пользователя
    """
    return product.buy_product(user_id=user_id, product_id=id, s=session)


@router.patch("/quantity/", status_code=200, response_model=ProductOut)
async def replenish_product(id: int, quantity: int,
                            session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Пополнить товар
    """
    return product.add_quantity(id=id, quantity=quantity, s=session)