from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security, File
from fastapi.responses import Response, FileResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.manga import MangaCreate, MangaOut
from src.models.general import UserToken
from src.repositories import manga, anilist


router = APIRouter(prefix="/manga", tags=["Manga"])
security = HTTPBearer()


@router.post("/manual", status_code=200, response_model=MangaOut)
async def manual_create_manga(manga_info: MangaCreate, session: Session = Depends(get_db),
                              Authorize: AuthJWT = Depends()):
    """
    Вручную создаёт новый тип манги (не физическую копию).
    """
    curr_manga = manga.create_manga(m=manga_info, s=session)
    if not curr_manga:
        raise HTTPException(status_code=400, detail=[{'msg': 'This manga already exists'}])
    return curr_manga


@router.post("/auto", status_code=200, response_model=MangaOut)
async def auto_create_manga(anilist_manga_uid: int, session: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    """
    Автоматически создаёт новый тип манги (не физическую копию), беря данные с Anilist.
    """
    manga_json = anilist.get_manga(anilist_manga_uid).json()['data'].get('Media')
    print(manga_json)
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
    return curr_manga
