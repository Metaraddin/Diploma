from fastapi import APIRouter, Cookie
from fastapi.security import HTTPBearer
from typing import Optional
import requests

router = APIRouter(prefix="/anilist", tags=["Anilist"])
security = HTTPBearer()


@router.get("/", status_code=200)
async def get_current_user_id(anilist_access_token: Optional[str] = Cookie(None)):
    query = '''
    query {
        Viewer {
            id
        }
    }
    '''
    url = 'https://graphql.anilist.co'
    headers = {'Authorization': "Bearer " + anilist_access_token}

    response = requests.post(url, json={'query': query}, headers=headers)
    return response.json()


@router.get('/rec', status_code=200)
async def get_rec(page: int = 1, per_page: int = 50, anilist_access_token: Optional[str] = Cookie(None)):
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
