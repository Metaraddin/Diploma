import requests


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
    return requests.post(url, json={'query': query, 'variables': variables})