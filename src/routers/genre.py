from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.genre import GenreOut, GenreCreate
from src.repositories import genre


router = APIRouter(prefix="/genre", tags=["Genre"])
security = HTTPBearer()


@router.post("/", status_code=200, response_model=GenreOut)
async def create_genre(genre_info: GenreCreate, session: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Создаёт новый жанр.
    """
    curr_genre = genre.create_genre(g=genre_info, s=session)
    if not curr_genre:
        raise HTTPException(status_code=400, detail=[{'msg': 'This genre already exists'}])
    return curr_genre


@router.get("/", status_code=200, response_model=GenreOut)
async def get_genre(id: int, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Возвращает авторизованного пользователя.
    """
    curr_genre = genre.get_genre_by_id(id, session)
    if not curr_genre:
        raise HTTPException(status_code=400, detail=[{'msg': 'This genre is not found'}])
    return curr_genre
