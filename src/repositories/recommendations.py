from sqlalchemy.orm import Session
from src.repositories import user, genre, library, anilist
from src.db.genre import Genre
from src.db.manga import MangaGenre, Manga
from src.db.library import Library
import pandas as pd
import copy


def read_user_params(s: Session):
    params = {}
    all_user = user.get_all_user(s=s, limit=5000, skip=0)
    all_genres = genre.get_all_genre(s=s)
    empty_line = {}
    for curr_genre in all_genres:
        empty_line[curr_genre.id] = 0
    for curr_user in all_user:
        params[curr_user.id] = copy.copy(empty_line)
        genre_sum = 0
        all_manga = s.query(Manga).filter(Manga.id == Library.manga_id).filter(Library.user_id == curr_user.id).join(Library).all()
        for curr_manga in all_manga:
            all_genre = s.query(Genre).filter(Genre.id == MangaGenre.genre_id).filter(MangaGenre.manga_id == curr_manga.id).join(MangaGenre).all()
            for curr_genre in all_genre:
                genre_sum += 1
                params[curr_user.id][curr_genre.id] += 1
        if genre_sum > 0:
            for genre_id in params[curr_user.id]:
                params[curr_user.id][genre_id] = (params[curr_user.id][genre_id] * 100) / genre_sum
    params = pd.DataFrame(params)
    return params


def find_neighbors(obj_id: int, df: pd.DataFrame):
    obj = df.pop(obj_id)
    result = [dict(user_id=s, corr=obj.corr(df.T.loc[s])) for s in df]
    return sorted(result, key=lambda d: d['corr'], reverse=True)


def get_recommendation(user_id: int, s: Session, limit: int = 5):
    df = read_user_params(s=s)
    print(df)
    corr = find_neighbors(obj_id=user_id, df=df)
    print(corr)
    obj_user_manga = library.get_manga_from_user(user_id=user_id, s=s)
    result = []
    for i in corr:
        user_manga = library.get_manga_from_user(i['user_id'], s=s)
        for manga in user_manga:
            if manga not in obj_user_manga:
                result.append(manga)
                if len(result) >= limit:
                    break
    return result


def test(user_id: int, s: Session, limit: int = 50):
    data = anilist.get_rec(user_id=user_id, s=s, page=1, per_page=50).json()
    return data