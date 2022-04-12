from fastapi import APIRouter, Cookie, Depends
from fastapi.security import HTTPBearer
from typing import Optional
import requests
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from src.app.dependencies import get_db
from src.repositories.user import get_anilist_token

import doctest
import deal

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


@router.get('/rec_manga', status_code=200)
async def get_manga_recommendations(manga_id: int, page = 1, per_page: int = 25):
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


@router.get('/get', status_code=200)
async def get_manga(uid: int):
    query = '''
    query ($id: Int) {
        Media (id: $id, type: MANGA) {
            id
            title {
                romaji
                english
                native
            }
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            description
            chapters
            volumes
            countryOfOrigin
            isLicensed
            source
            hashtag
            updatedAt
            coverImage {
                extraLarge
                large
                medium
            }
            genres
            staff {
                nodes {
                    id
                    name {
                        full
                    }
                }
            }
            studios {
                nodes {
                    id
                    name
                }
            }
            isAdult
        }
    }
    '''
    variables = {'id': uid}
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    return response.json()


@router.get('/find', status_code=200)
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
