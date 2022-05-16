from fastapi import APIRouter, Cookie, Depends
from fastapi.responses import RedirectResponse, Response
from fastapi.security import HTTPBearer
from typing import Optional
from src.repositories import anilist
import requests
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from src.app.dependencies import get_db
from src.repositories.user import set_anilist_token
from src.app.dependencies import get_settings

router = APIRouter(prefix="/anilist", tags=["Anilist"])
security = HTTPBearer()


setting = get_settings()


@router.get("/auth/", response_class=RedirectResponse)
async def get_code():
    """
    Перенаправляет на Anilist для авторизации,\n
    после чего Anilist перенаправляет на /callback вместе с кодом авторизации.\n
    redirect_uri указан в настройках Anilist.\n
    **Swagger Ui не поддерживает перенаправление из-за CORS.**\n
    """
    response_type = 'code'
    url = 'https://anilist.co/api/v2/oauth/authorize'
    return f'{url}?client_id={setting.client_id}&response_type={response_type}'


@router.get('/auth/callback/')
async def callback(code: str, response: Response):
    """
    Функция обратного вызова авторизации на Anilist.\n
    Принимает код авторизации и сохраняет его в cookie\n
    """
    response.set_cookie(key='anilist_auth_code', value=code, httponly=True)
    return {"message": "Anilist auth code save in cookies"}


@router.get('/auth/token/')
async def get_token(session: Session = Depends(get_db), Authorize: AuthJWT = Depends(),
                    anilist_auth_code: Optional[str] = Cookie(None)):
    """
    Использует код авторизации для получения Access Token.\n
    и сохраняет его в базу данных, закрепляя за текущим пользователем.
    """
    Authorize.jwt_required()
    anilist_code = anilist_auth_code
    url = 'https://anilist.co/api/v2/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': f'{setting.client_id}',
        'client_secret': f'{setting.client_secret}',
        'redirect_uri': f'{setting.redirect_uri}',
        'code': f'{anilist_code}'
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200 and response.json()['access_token']:
        set_anilist_token(anilist_token=response.json()['access_token'],
                          user_id=int(Authorize.get_jwt_subject()), s=session)
    return response.json()


@router.get("/user/curr/", status_code=200)
async def get_current_user(session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return anilist.get_user(int(Authorize.get_jwt_subject()), s=session)


@router.get("/user/{user_id}", status_code=200)
async def get_user(user_id: int, session: Session = Depends(get_db)):
    return anilist.get_user(user_id, s=session)


@router.get('/recommendations/{manga_id}', status_code=200)
async def get_recommendations_to_manga(manga_id: int, page=1, per_page: int = 100):
    return anilist.get_recommendations_to_manga(manga_id=manga_id, page=page, per_page=per_page)


@router.get('/get/{uid}', status_code=200)
async def get_manga(uid: int):
    return anilist.get_manga(uid)


@router.get('/find/{name}', status_code=200)
async def get_manga_by_name(name: str, page: int = 1, per_page: int = 50):
    return anilist.get_manga_by_name(name=name, page=page, per_page=per_page)


@router.get('/list/', status_code=200)
async def get_manga_list(user_id: int, page: int = 1, per_page: int = 50):
    return anilist.get_manga_list(user_id=user_id, page=page, per_page=per_page)
