from fastapi import APIRouter, Cookie, Depends, Security
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.security import HTTPBearer
from src.models.token import Token
from typing import Optional
from src.repositories.user import add_anilist_code, get_anilist_code
from src.app.dependencies import get_db
import requests

from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session


router = APIRouter(prefix="/auth_anilist", tags=["Anilist Auth"])
security = HTTPBearer()


@router.get("/", response_class=RedirectResponse)
async def get_code():
    client_id = '7698'
    redirect_uri = 'https://tolocalhost.com/auth_anilist/callback'
    response_type = 'code'
    url = 'https://anilist.co/api/v2/oauth/authorize'
    return f'{url}?client_id={client_id}&response_type={response_type}'


@router.get('/callback')
async def add_code(code: str, session: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends(), auth: HTTPAuthorizationCredentials = Security(security)):
    Authorize.jwt_required()
    add_anilist_code(anilist_auth_code=code, user_id=int(Authorize.get_jwt_subject()), s=session)
    return code #####################


@router.get('/token')
async def get_token():
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
                media {
                    id
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
    headers = {'Authorization': "Bearer " + anilist_access_token}

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    return response.json()



@router.get('/callback2')
async def read_token():
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <script>
                let post = JSON.stringify({ "access_token": window.location.hash });
                const url = "/auth_anilist/token";
                let xhr = new XMLHttpRequest();
                xhr.open('POST', url, true);
                xhr.setRequestHeader('Content-type', 'application/json; charset=UTF-8');
                xhr.onreadystatechange = function() {
                    if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
                        document.write(window.location.hash);
                    }
                }
                xhr.send(post);
            </script>
        </head>
        <body>
        </body>
    </html>
    """
    return HTMLResponse(html)


@router.post('/token')
async def save_token(token: Token, response: Response):
    access_token = token.access_token.split('=')[1].split('&')[0]
    response.set_cookie(key='anilist_access_token', value=access_token, httponly=True)
    return {"anilist_access_token": access_token}


@router.get('/token')
async def read_token(anilist_access_token: Optional[str] = Cookie(None)):
    return {'anilist_access_token': anilist_access_token}

