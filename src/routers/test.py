from typing import List

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.product import ProductCreate
from src.repositories import anilist, product, manga, recommendations, library


router = APIRouter(prefix="/test", tags=["Test"])
security = HTTPBearer()


@router.post("/import/", status_code=200, response_model=List[int])
async def import_manga_list(anilist_user_uid: int, user_id: int = None,
                            session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Имтортирует список манги с Anilist.
    """
    response = anilist.import_library(user_anilist_id=anilist_user_uid, s=session)
    if not user_id:
        return response
    for manga_id in response:
        library.add_manga(user_id=user_id, manga_id=manga_id, s=session)
    return response


@router.post("/replenish/", status_code=200)
async def replenish_product(product_info: ProductCreate,
                            session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Создаёт тестовый товар для всех видов манги\n
    """
    all_manga = manga.get_all_manga(s=session, limit=5000, skip=0)
    for curr_manga in all_manga:
        product.create_product(manga_id=curr_manga.id, product_info=product_info, s=session)


@router.get('/correlation/pearson/', status_code=200)
async def correlation_coefficient_pearson(user_id: int,
                                          session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    df = recommendations.read_user_params(s=session)
    return recommendations.find_neighbors(obj_id=user_id, df=df, method='pearson')


@router.get('/correlation/spearman/', status_code=200)
async def correlation_coefficient_spearman(user_id: int,
                                           session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    df = recommendations.read_user_params(s=session)
    return recommendations.find_neighbors(obj_id=user_id, df=df, method='spearman')


@router.get('/correlation/kendall/', status_code=200)
async def correlation_coefficient_kendall(user_id: int,
                                          session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    df = recommendations.read_user_params(s=session)
    return recommendations.find_neighbors(obj_id=user_id, df=df, method='kendall')


@router.get('/dataset/', status_code=200)
async def percentage_user_genres(session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    return recommendations.read_user_params(s=session)

