from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.manga import MangaCreate, MangaOut
from src.models.general import MangaGenreStaff
from src.db.manga import Manga, MangaGenre, MangaStaff
from src.db.genre import Genre
from src.db.staff import Staff


def create_manga(m: MangaCreate, s: Session):
    manga = Manga()
    manga.anilist_id = m.anilist_id
    manga.title_romaji = m.title_romaji
    manga.title_english = m.title_english
    manga.title_russian = m.title_russian
    manga.title_native = m.title_native
    manga.start_date = m.start_date
    manga.end_date = m.end_date
    manga.description_english = m.description_english
    manga.description_russian = m.description_russian
    manga.chapters = m.chapters
    manga.volumes = m.volumes
    manga.country_of_origin = m.country_of_origin
    manga.is_licensed = m.is_licensed
    manga.source = m.source
    manga.cover_image_large_anilist_url = m.cover_image_large_anilist_url
    manga.cover_image_medium_anilist_url = m.cover_image_medium_anilist_url
    manga.is_adult = m.is_adult

    s.add(manga)
    try:
        s.commit()
        return manga
    except IntegrityError:
        return None


def add_genre(manga_id: int, genre_id: int, s: Session):
    manga_genre = MangaGenre()
    manga_genre.manga_id = manga_id
    manga_genre.genre_id = genre_id
    s.add(manga_genre)
    try:
        s.commit()
        return manga_genre
    except IntegrityError:
        return None


def add_staff(manga_id: int, staff_id: int, s: Session):
    manga_staff = MangaStaff()
    manga_staff.manga_id = manga_id
    manga_staff.staff_id = staff_id
    s.add(manga_staff)
    try:
        s.commit()
        return manga_staff
    except IntegrityError:
        return None


def get_manga_by_id(manga_id: int, s: Session):
    return s.query(Manga).filter(Manga.id == manga_id).first()


def get_all_manga(s: Session, limit: int = 100, skip: int = 0):
    return s.query(Manga).limit(limit).offset(skip).all()


def get_manga_full(manga_id: int, s: Session):
    manga = s.query(Manga).filter(Manga.id == manga_id).first()
    genres = s.query(Genre)\
        .filter(MangaGenre.manga_id == manga_id) \
        .filter(Genre.id == MangaGenre.genre_id) \
        .join(MangaGenre)\
        .all()
    staff = s.query(Staff) \
        .filter(MangaStaff.manga_id == manga_id) \
        .filter(Staff.id == MangaStaff.staff_id) \
        .join(MangaStaff)\
        .all()
    return MangaGenreStaff(Manga=manga, Genres=genres, Staff=staff)


def edit_cover_id(manga_id: int, avatar_id: int, s: Session):
    user = s.query(Manga).filter(Manga.id == manga_id).first()
    user.cover_id = avatar_id

    s.add(user)
    s.commit()
    return user


def delete_cover_id(manga_id: int, s: Session):
    user = s.query(Manga).filter(Manga.id == manga_id).first()
    user.cover_id = None

    s.add(user)
    s.commit()
    return user
