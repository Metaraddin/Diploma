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
async def auto_create_manga(anilist_manga_uid: int, session: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    """
    Автоматическое создание нового типа манги (не физическую копию), беря данные с Anilist.\n
    Обновляет тип манги, если anilist_manga_uid уже найден.\n
    Автоматически заполняет жанры и авторов c Anilist.\n
    При нахождении нового жанра/автора создаёт новую запись.
    """
    manga_json = anilist.get_manga(anilist_manga_uid).json()['data'].get('Media')
    manga_info = MangaCreate()
    manga_info.anilist_id = anilist_manga_uid
    manga_info.title_romaji = manga_json.get('title').get('romaji')
    manga_info.title_english = manga_json.get('title').get('english')
    manga_info.title_native = manga_json.get('title').get('native')
    start_date = manga_json.get('startDate')
    manga_info.start_date = f"{start_date.get('year')}-{start_date.get('month')}-{start_date.get('day')}"
    end_date = manga_json.get('endDate')
    manga_info.end_date = f"{end_date.get('year')}-{end_date.get('month')}-{end_date.get('day')}"
    manga_info.description_english = manga_json.get('description')
    manga_info.chapters = manga_json.get('chapters')
    manga_info.volumes = manga_json.get('volumes')
    manga_info.country_of_origin = manga_json.get('country_of_origin')
    manga_info.is_licensed = manga_json.get('is_licensed')
    manga_info.source = manga_json.get('source')
    manga_info.cover_image_large_anilist_url = manga_json.get('coverImage').get('large')
    manga_info.cover_image_medium_anilist_url = manga_json.get('coverImage').get('medium')

    cover_file = requests.get(manga_info.cover_image_large_anilist_url).content
    cover = image.create_image(cover_file, s=session)

    manga_info.is_adult = manga_json.get('isAdult')
    curr_manga = manga.create_manga(m=manga_info, s=session)
    manga.edit_cover_id(curr_manga.id, cover.id, s=session)
    if not curr_manga:
        raise HTTPException(status_code=400, detail=[{'msg': 'This manga already exists'}])
    if manga_json.get('genres'):
        for genre_name in manga_json.get('genres'):
            curr_genre = genre.get_genre_by_name(name=genre_name, s=session)
            if not curr_genre:
                curr_genre = genre.create_genre(GenreCreate(name=genre_name), s=session)
            manga.add_genre(manga_id=curr_manga.id, genre_id=curr_genre.id, s=session)
    if manga_json.get('staff'):
        for node in manga_json.get('staff').get('nodes'):
            curr_staff = staff.get_staff_by_name(node.get('name').get('full'), s=session)
            if not curr_staff:
                curr_staff = staff.create_staff(StaffCreate(name=node.get('name').get('full')), s=session)
            manga.add_staff(manga_id=curr_manga.id, staff_id=curr_staff.id, s=session)
    return manga.get_manga_full(manga_id=curr_manga.id, s=session)


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


@router.get("/{id}/", status_code=200, response_model=MangaGenreStaff)
async def get_manga(manga_id: int, session: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    """
    Получение манги.
    """
    return manga.get_manga_full(manga_id=manga_id, s=session)


@router.delete('/{id}/', status_code=200, response_model=MangaOut)
async def delete_manga(manga_id: int,
                     session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Удаление манги
    """
    return manga.delete_manga(manga_id, s=session)


@router.patch('/{id}/', status_code=200, response_model=MangaOut)
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


@router.get("/{manga_id}/cover/", status_code=200)
async def get_cover(manga_id: int, session: Session = Depends(get_db)):
    """
    Возвращает обложку манги по **manga.id**.
    """
    curr_manga = manga.get_manga_by_id(manga_id, s=session)
    curr_cover = image.get_image(curr_manga.cover_id, session)
    if curr_cover is None:
        return FileResponse('static/manga_default_cover.png')
    return Response(content=curr_cover.file, media_type='image/png')


@router.patch("/{manga_id}/cover/", status_code=200, response_model=MangaOut)
async def edit_cover(manga_id: int, image_file: bytes = File(...), session: Session = Depends(get_db),
                     Authorize: AuthJWT = Depends()):
    """
    Устанавливает обложку манги по **manga.id**.\n
    Обложка хранится в отдельной таблице, manga хранит только внешний ключ.
    """
    mapper = image.create_image(file=image_file, s=session)
    return manga.edit_cover_id(manga_id=manga_id, avatar_id=mapper.id, s=session)


@router.delete("/{manga_id}/cover/", status_code=200, response_model=MangaOut)
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
