from fastapi import APIRouter, Cookie, Depends, Security
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.security import HTTPBearer
from src.models.token import Token
from typing import Optional
from src.repositories.user import set_anilist_token
from src.app.dependencies import get_db
import requests

from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth_anilist", tags=["Anilist Auth"])
security = HTTPBearer()

client_secret = '0m9cgoidK2yW7tO01yYQRixLdmk2eptGmzgOD7G7'
client_id = '7698'
redirect_uri = 'http://localhost:8000/auth_anilist/callback'


@router.get("/", response_class=RedirectResponse)
async def get_code():
    """
    Перенаправляет на Anilist для авторизации,\n
    после чего Anilist перенаправляет на /callback вместе с кодом авторизации.\n
    redirect_uri указан в настройках Anilist.\n
    **Swagger Ui не поддерживает перенаправление из-за CORS.**\n
    """
    redirect_uri = 'https://tolocalhost.com/auth_anilist/callback'
    response_type = 'code'
    url = 'https://anilist.co/api/v2/oauth/authorize'
    return f'{url}?client_id={client_id}&response_type={response_type}'


@router.get('/callback')
async def callback(code: str, response: Response):
    """
    Функция обратного вызова авторизации на Anilist.\n
    Принимает код авторизации.\n
    """
    response.set_cookie(key='anilist_auth_code', value=code, httponly=True)
    return code


@router.get('/token')
async def get_token(session: Session = Depends(get_db), Authorize: AuthJWT = Depends(),
                    anilist_auth_code: Optional[str] = Cookie(None)):
    """
    Использует код авторизации для получения Access Token.\n
    Хранит токен в cookies
    """
    Authorize.jwt_required()
    anilist_code = anilist_auth_code
    url = 'https://anilist.co/api/v2/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': f'{client_id}',
        'client_secret': f'{client_secret}',
        'redirect_uri': f'{redirect_uri}',
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
