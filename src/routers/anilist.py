from fastapi import APIRouter, Cookie, Depends
from fastapi.security import HTTPBearer
from typing import Optional
import requests
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from src.app.dependencies import get_db
from src.repositories.user import get_anilist_token

router = APIRouter(prefix="/anilist", tags=["Anilist"])
security = HTTPBearer()


@router.get("/", status_code=200)
async def get_current_user_id(session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    query = '''
    query {
        Viewer {
            id
        }
    }
    '''
    url = 'https://graphql.anilist.co'
    token = get_anilist_token(int(Authorize.get_jwt_subject()), s=session)
    headers = {'Authorization': "Bearer " + token}

    response = requests.post(url, json={'query': query}, headers=headers)
    return response.json()


@router.get('/rec', status_code=200)
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
    token = get_anilist_token(int(Authorize.get_jwt_subject()), s=session)
    headers = {'Authorization': "Bearer " + token}

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    return response.json()
