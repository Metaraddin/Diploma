from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.manga import MangaOut
from src.repositories import anilist, library
from typing import List


router = APIRouter(prefix="/library", tags=["Library"])
security = HTTPBearer()


@router.patch('/import/curr_user/', status_code=200, response_model=List[int])
async def import_manga_list(session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Имтортирует список манги с Anilist для текущего пользователя
    """
    Authorize.jwt_required()
    user_anilist_id = anilist.get_user_uid(int(Authorize.get_jwt_subject()), s=session)
    response = anilist.import_library(user_anilist_id=user_anilist_id, s=session)
    for manga_id in response:
        library.add_manga(user_id=int(Authorize.get_jwt_subject()), manga_id=manga_id, s=session)
    return response


@router.get('/curr_user/', status_code=200, response_model=List[MangaOut])
async def get_manga_from_current_user(session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Список манги для текущего пользователя.
    """
    Authorize.jwt_required()
    return library.get_manga_from_user(user_id=int(Authorize.get_jwt_subject()), s=session)


@router.get('/{user_id}', status_code=200, response_model=List[MangaOut])
async def get_manga_by_user_id(user_id: int, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Список манги для пользователя по id.
    """
    return library.get_manga_from_user(user_id=user_id, s=session)
