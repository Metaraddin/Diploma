from fastapi import APIRouter, Cookie, Depends
from fastapi.responses import RedirectResponse, Response
from fastapi.security import HTTPBearer
from typing import Optional
from src.repositories import anilist
import requests
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from src.app.dependencies import get_db
from src.repositories.user import get_anilist_token, set_anilist_token
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
    query = '''
    query {
        Viewer {
            id
            name
            siteUrl
        }
    }
    '''
    url = 'https://graphql.anilist.co'
    token = get_anilist_token(int(Authorize.get_jwt_subject()), s=session)
    headers = {'Authorization': "Bearer " + token}

    response = requests.post(url, json={'query': query}, headers=headers)
    return response.json()


@router.get('/rec/', status_code=200)
async def get_rec(page: int = 1, per_page: int = 50,
                  session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    query = '''
    query ($page: Int, $perPage: Int) {
        Page (page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            recommendations {
                id
                rating
                userRating
                mediaRecommendation {
                    id
                    title {
                        romaji
                        english
                    }
                    type
                }
                media {
                    id
                    title {
                        romaji
                        english
                    }
                    type
                }
            }
        }
    }
    '''
    variables = {
        'page': page,
        'perPage': per_page
    }
    url = 'https://graphql.anilist.co'
    token = get_anilist_token(int(Authorize.get_jwt_subject()), s=session)
    headers = {'Authorization': "Bearer " + token}

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    return response.json()


@router.get('/rec_manga/', status_code=200)
async def get_manga_recommendations(manga_id: int, page=1, per_page: int = 25):
    query = '''
    query ($page: Int, $perPage: Int, $mediaId: Int){
        Page (page: $page perPage: $perPage) {
            recommendations(mediaId: $mediaId) {
                mediaRecommendation {
                    id
                    title {
                        romaji
                        english
                    }
                    type
                }
            }
        }
    }
    '''
    variables = {
        'page': page,
        'perPage': per_page,
        'mediaId': manga_id
    }
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    return response.json()


@router.get('/get/', status_code=200)
async def get_manga(uid: int):
    response = anilist.get_manga(uid)
    return response.json()


@router.get('/find/', status_code=200)
async def get_manga_by_name(name: str, page: int = 1, per_page: int = 50):
    query = """
    query ($id: Int, $page: Int, $perPage: Int, $search: String) {
        Page (page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media (id: $id, search: $search, type: MANGA) {
                id
                title {
                    romaji
                    english
                }
            }
        }
    }
    """
    variables = {
        'search': name,
        'page': page,
        'perPage': per_page
    }
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    return response.json()
