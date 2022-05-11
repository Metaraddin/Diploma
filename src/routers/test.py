from typing import List

from fastapi import APIRouter, Depends, HTTPException, File
from fastapi.responses import Response, FileResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.user import UserOut, UserUpdate, UserCreate, UserLogin
from src.models.manga import MangaOut
from src.models.general import UserToken
from src.repositories import user, image
from src.models.token import Token
from src.repositories import manga
from src.repositories import anilist
import requests


router = APIRouter(prefix="/test", tags=["Test"])
security = HTTPBearer()


@router.post("/import", status_code=200, response_model=List[int])
async def import_manga_list(anilist_user_uid: int,
                            session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Имтортирует список манги с Anilist.
    """
    Authorize.jwt_required()
    return anilist.import_library(user_anilist_id=anilist_user_uid, s=session)


@router.post("/")

