from fastapi import APIRouter, Depends, HTTPException, File
from fastapi.responses import Response, FileResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.manga import MangaCreate, MangaOut, MangaEdit
from src.models.genre import GenreCreate
from src.models.staff import StaffCreate
from src.models.general import MangaGenreStaff
from src.repositories import manga, anilist, genre, staff, image

from typing import List
import requests

router = APIRouter(prefix="/manga", tags=["Manga"])
security = HTTPBearer()


@router.post("/auto/", status_code=200, response_model=MangaGenreStaff)
async def import_manga(anilist_manga_uid: int, session: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    """
    Автоматическое создание нового типа манги (не физическую копию), беря данные с Anilist.\n
    Обновляет тип манги, если anilist_manga_uid уже найден.\n
    Автоматически заполняет жанры и авторов c Anilist.\n
    При нахождении нового жанра/автора создаёт новую запись.
    """
    return manga.import_manga_by_id(anilist_manga_uid=anilist_manga_uid, s=session)


@router.post("/", status_code=200, response_model=MangaOut)
async def create_manga(manga_info: MangaCreate, session: Session = Depends(get_db),
                              Authorize: AuthJWT = Depends()):
    """
    Ручное создание нового типа манги (не физическую копию).\n
    Жанры и авторы добавляются отдельно.
    """
    curr_manga = manga.create_manga(m=manga_info, s=session)
    if not curr_manga:
        raise HTTPException(status_code=400, detail=[{'msg': 'This manga already exists'}])
    return curr_manga


@router.get("/{id}", status_code=200, response_model=MangaGenreStaff)
async def get_manga(manga_id: int, session: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    """
    Получение манги.
    """
    return manga.get_manga_full(manga_id=manga_id, s=session)


@router.delete('/{id}', status_code=200, response_model=MangaOut)
async def delete_manga(manga_id: int,
                     session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Удаление манги
    """
    return manga.delete_manga(manga_id, s=session)


@router.patch('/{id}', status_code=200, response_model=MangaOut)
async def edit_manga(manga_id: int, manga_info: MangaEdit,
                     session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Редактирование манги\n
    Для изменения поля включите его в словарь\n
    Для удаления поля **явно** укажите null в качестве значения.
    """
    return manga.edit_manga(manga_id, manga_info, s=session)


@router.post('/genre/', status_code=200, response_model=MangaGenreStaff)
async def add_genre(manga_id: int, genre_id: int, session: Session = Depends(get_db),
                           Authorize: AuthJWT = Depends()):
    """
    Добавление жарна.
    """
    curr = manga.add_genre(manga_id=manga_id, genre_id=genre_id, s=session)
    if not curr:
        raise HTTPException(status_code=400, detail=[{'msg': 'This genre already exists'}])
    res = manga.get_manga_full(manga_id=manga_id, s=session)
    return res


@router.post('/staff/', status_code=200, response_model=MangaGenreStaff)
async def add_staff(manga_id: int, staff_id: int, session: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    """
    Добавление автора.
    """
    curr_manga = manga.add_staff(manga_id=manga_id, staff_id=staff_id, s=session)
    if not curr_manga:
        raise HTTPException(status_code=400, detail=[{'msg': 'This staff already exists'}])
    return manga.get_manga_full(manga_id=manga_id, s=session)


@router.get("/all/", status_code=200, response_model=List[MangaOut])
async def get_all_manga(limit: int = 100, skip: int = 0, session: Session = Depends(get_db)):
    """
    Получение краткого описания всей манги
    """
    return manga.get_all_manga(s=session, limit=limit, skip=skip)


@router.get("/cover/{manga_id}", status_code=200)
async def get_cover(manga_id: int, session: Session = Depends(get_db)):
    """
    Возвращает обложку манги по **manga.id**.
    """
    curr_manga = manga.get_manga_by_id(manga_id, s=session)
    curr_cover = image.get_image(curr_manga.cover_id, session)
    if curr_cover is None:
        return FileResponse('static/manga_default_cover.png')
    return Response(content=curr_cover.file, media_type='image/png')


@router.patch("/cover/{manga_id}", status_code=200, response_model=MangaOut)
async def edit_cover(manga_id: int, image_file: bytes = File(...), session: Session = Depends(get_db),
                     Authorize: AuthJWT = Depends()):
    """
    Устанавливает обложку манги по **manga.id**.\n
    Обложка хранится в отдельной таблице, manga хранит только внешний ключ.
    """
    mapper = image.create_image(file=image_file, s=session)
    return manga.edit_cover_id(manga_id=manga_id, avatar_id=mapper.id, s=session)


@router.delete("/cover/{manga_id}", status_code=200, response_model=MangaOut)
async def delete_cover(manga_id: int, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Удаляет обложку манги по **manga.id**.
    """
    Authorize.jwt_required()
    curr_manga = manga.get_manga_by_id(manga_id, s=session)
    curr_cover = image.get_image(curr_manga.cover_id, session)
    if curr_cover is None:
        raise HTTPException(status_code=400, detail=[{'msg': 'The user does not have an avatar'}])
    manga.delete_cover_id(manga_id, s=session)
    image.delete_image(curr_cover.id, session)
    return manga.get_manga_by_id(manga_id, s=session)
