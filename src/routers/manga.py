from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.manga import MangaCreate, MangaOut
from src.models.genre import GenreCreate
from src.models.staff import StaffCreate
from src.models.general import MangaGenreStaff
from src.repositories import manga, anilist, genre, staff

router = APIRouter(prefix="/manga", tags=["Manga"])
security = HTTPBearer()


@router.post("/manual", status_code=200, response_model=MangaOut)
async def manual_create_manga(manga_info: MangaCreate, session: Session = Depends(get_db),
                              Authorize: AuthJWT = Depends()):
    """
    Ручное создание нового типа манги (не физическую копию).\n
    Жанры и авторы добавляются отдельно.
    """
    curr_manga = manga.create_manga(m=manga_info, s=session)
    if not curr_manga:
        raise HTTPException(status_code=400, detail=[{'msg': 'This manga already exists'}])
    return curr_manga


@router.post('/manual/genre', status_code=200, response_model=MangaGenreStaff)
async def manual_add_genre(manga_id: int, genre_id: int, session: Session = Depends(get_db),
                           Authorize: AuthJWT = Depends()):
    """
    Ручное добавление жарна.
    """
    curr = manga.add_genre(manga_id=manga_id, genre_id=genre_id, s=session)
    if not curr:
        raise HTTPException(status_code=400, detail=[{'msg': 'This genre already exists'}])
    res = manga.get_manga_full(manga_id=manga_id, s=session)
    return res


@router.post('/manual/staff', status_code=200, response_model=MangaGenreStaff)
async def manual_add_staff(manga_id: int, staff_id: int, session: Session = Depends(get_db),
                           Authorize: AuthJWT = Depends()):
    """
    Ручное добавление автора.
    """
    curr_manga = manga.add_staff(manga_id=manga_id, staff_id=staff_id, s=session)
    if not curr_manga:
        raise HTTPException(status_code=400, detail=[{'msg': 'This staff already exists'}])
    return manga.get_manga_full(manga_id=manga_id, s=session)


@router.post("/auto", status_code=200, response_model=MangaGenreStaff)
async def auto_create_manga(anilist_manga_uid: int, session: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    """
    Автоматическое создание нового типа манги (не физическую копию), беря данные с Anilist.\n
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
    manga_info.is_adult = manga_json.get('isAdult')
    curr_manga = manga.create_manga(m=manga_info, s=session)
    if not curr_manga:
        raise HTTPException(status_code=400, detail=[{'msg': 'This manga already exists'}])
    if manga_json.get('genres'):
        for genre_name in manga_json.get('genres'):
            genre_id = genre.create_genre(GenreCreate(name=genre_name), s=session)
            if not genre_id:
                genre_id = genre.get_genre_by_name(genre_name, s=session).id
            else:
                genre_id = genre_id.id
            manga.add_genre(manga_id=curr_manga.id, genre_id=genre_id, s=session)
    if manga_json.get('staff'):
        for node in manga_json.get('staff').get('nodes'):
            staff_name = node.get('name').get('full')
            staff_id = staff.create_staff(StaffCreate(name=staff_name), s=session)
            if not staff_id:
                staff_id = staff.get_staff_by_name(staff_name, s=session).id
            else:
                staff_id = staff_id.id
            manga.add_staff(manga_id=curr_manga.id, staff_id=staff_id, s=session)
    return manga.get_manga_full(manga_id=curr_manga.id, s=session)


@router.get("/", status_code=200, response_model=MangaGenreStaff)
async def get_manga(manga_id: int, session: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    """
    Получение манги.
    """
    return manga.get_manga_full(manga_id=manga_id, s=session)
