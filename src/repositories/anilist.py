import requests
from sqlalchemy.orm import Session
from src.repositories import user
from src.repositories import manga


def get_manga(uid: int):
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
    return requests.post(url, json={'query': query, 'variables': variables}).json()


def get_user_uid(user_id, s: Session):
    token = user.get_anilist_token(user_id, s=s)
    query = '''
            query {
                Viewer {
                    id
                }
            }
            '''
    url = 'https://graphql.anilist.co'
    headers = {'Authorization': "Bearer " + token}
    response = requests.post(url, json={'query': query}, headers=headers)
    return response.json()['data']['Viewer']['id']


def import_library(user_anilist_id: int, s: Session):
    has_next_page = True
    page = 1
    manga_id_list = []
    result = []
    while has_next_page:
        query = '''
                query ($page: Int, $perPage: Int, $userId: Int) {
                    Page (page: $page, perPage: $perPage) {
                        pageInfo {
                            currentPage
                            hasNextPage
                        }
                        mediaList (userId: $userId, type: MANGA) {
                            media {
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
                    }
                }
            '''
        variables = {
            'page': page,
            'perPage': 50,
            'userId': user_anilist_id
        }
        url = 'https://graphql.anilist.co'
        response = requests.post(url, json={'query': query, 'variables': variables}).json()
        has_next_page = response['data']['Page']['pageInfo']['hasNextPage']
        for line in response['data']['Page']['mediaList']:
            print(line)
            manga_id_list.append(line['media']['id'])
            curr_manga = manga.import_manga(line['media'], s=s)
            result.append(curr_manga.Manga.id)
    return result


def get_manga_by_name(name: str, page: int = 1, per_page: int = 50):
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
    return requests.post(url, json={'query': query, 'variables': variables}).json()


def get_manga_list(user_id: int, page: int = 1, per_page: int = 50):
    query = """
        query ($page: Int, $perPage: Int, $userId: Int) {
            Page (page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                mediaList (userId: $userId, type: MANGA) {
                    id
                    userId
                    status
                    progress
                    progressVolumes
                    repeat
                    priority
                    private
                    notes
                    hiddenFromStatusLists
                    media {
                        id
                        title {
                            romaji
                            english
                        }
                    }
                }
            }
        }
        """
    variables = {
        'page': page,
        'perPage': per_page,
        'userId': user_id
    }
    url = 'https://graphql.anilist.co'

    return requests.post(url, json={'query': query, 'variables': variables}).json()


def get_recommendations_to_manga(manga_id: int, page: int = 1, per_page: int = 50):
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
    return requests.post(url, json={'query': query, 'variables': variables}).json()


def get_user(user_id: int, s: Session):
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
    token = user.get_anilist_token(user_id, s=s)
    if not token:
        return None
    headers = {'Authorization': "Bearer " + token}

    return requests.post(url, json={'query': query}, headers=headers).json()
