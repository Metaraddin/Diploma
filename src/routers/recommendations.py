from typing import List

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.models.manga import MangaOut
from src.app.dependencies import get_db
from src.repositories import recommendations


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
security = HTTPBearer()


@router.get('/correlation/pearson/', status_code=200, response_model=List[MangaOut])
async def correlation_coefficient_pearson(user_id: int,
                                          session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Создаёт dataset с пользователями и процентным соотношением жанров\n
    Сотрирует пользователей по коэффициенту корреляции\n
    Выдаёт мангу из списка пользователй в соответсвии с сортировкой\n
    """
    return recommendations.get_recommendation(user_id=user_id, s=session, method='pearson')


@router.get('/correlation/spearman/', status_code=200, response_model=List[MangaOut])
async def correlation_coefficient_spearman(user_id: int,
                                          session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    return recommendations.get_recommendation(user_id=user_id, s=session, method='spearman')


@router.get('/correlation/kendall/', status_code=200, response_model=List[MangaOut])
async def correlation_coefficient_kendall(user_id: int,
                                          session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    return recommendations.get_recommendation(user_id=user_id, s=session, method='kendall')

