from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.manga import MangaCreate, MangaEdit
from src.models.general import MangaGenreStaff
from src.db.manga import Manga, MangaGenre, MangaStaff
from src.db.genre import Genre
from src.db.staff import Staff
from src.repositories import anilist, image, genre, staff
from src.models.genre import GenreCreate
from src.models.staff import StaffCreate
import requests


def create_manga(m: MangaCreate, s: Session):
    manga = s.query(Manga).filter(Manga.anilist_id == m.anilist_id).first()
    if not manga:
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
    except IntegrityError as e:
        raise e


def edit_manga(manga_id: int, m: MangaEdit, s: Session):
    manga = s.query(Manga).filter(Manga.id == manga_id).first()
    m = m.dict(exclude_unset=True)
    if 'title_romaji' in m.keys(): manga.title_romaji = m['title_romaji']
    if 'title_english' in m.keys(): manga.title_english = m['title_english']
    if 'title_russian' in m.keys(): manga.title_russian = m['title_russian']
    if 'title_native' in m.keys(): manga.title_native = m['title_native']
    if 'start_date' in m.keys(): manga.start_date = m['start_date']
    if 'end_date' in m.keys(): manga.end_date = m['end_date']
    if 'description_english' in m.keys(): manga.description_english = m['description_english']
    if 'description_russian' in m.keys(): manga.description_russian = m['description_russian']
    if 'chapters' in m.keys(): manga.chapters = m['chapters']
    if 'volumes' in m.keys(): manga.volumes = m['volumes']
    if 'country_of_origin' in m.keys(): manga.country_of_origin = m['country_of_origin']
    if 'is_licensed' in m.keys(): manga.is_licensed = m['is_licensed']
    if 'source' in m.keys(): manga.source = m['source']
    if 'is_adult' in m.keys(): manga.is_adult = m['is_adult']
    s.add(manga)
    s.commit()
    return manga


def delete_manga(manga_id: int, s: Session):
    manga = s.query(Manga).filter(Manga.id == manga_id).first()
    genres = s.query(MangaGenre).filter(MangaGenre.manga_id == manga_id).all()
    for mg in genres:
        s.delete(mg)
    staff = s.query(MangaStaff).filter(MangaStaff.manga_id == manga_id).all()
    for ms in staff:
        s.delete(ms)
    s.commit()
    s.delete(manga)
    s.commit()
    return manga


def add_genre(manga_id: int, genre_id: int, s: Session):
    manga_genre = MangaGenre()
    manga_genre.manga_id = manga_id
    manga_genre.genre_id = genre_id
    s.add(manga_genre)
    try:
        s.commit()
        return manga_genre
    except IntegrityError:
        s.rollback()
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
        s.rollback()
        return None


def get_manga_by_id(manga_id: int, s: Session):
    return s.query(Manga).filter(Manga.id == manga_id).first()


def get_manga_by_anilist_id(anilist_manga_id: int, s: Session):
    return s.query(Manga).filter(Manga.id == anilist_manga_id).first()


def get_all_manga(s: Session, limit: int = 100, skip: int = 0):
    return s.query(Manga).limit(limit).offset(skip).all()


def get_manga_full(manga_id: int, s: Session):
    manga = s.query(Manga).filter(Manga.id == manga_id).first()
    genres = s.query(Genre) \
        .filter(MangaGenre.manga_id == manga_id) \
        .filter(Genre.id == MangaGenre.genre_id) \
        .join(MangaGenre) \
        .all()
    staff = s.query(Staff) \
        .filter(MangaStaff.manga_id == manga_id) \
        .filter(Staff.id == MangaStaff.staff_id) \
        .join(MangaStaff) \
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


def import_manga_by_id(anilist_manga_uid: int, s: Session):
    manga_json = anilist.get_manga(anilist_manga_uid).json()['data'].get('Media')
    return import_manga(manga_json, s=s)


def import_manga(manga_json: dict, s: Session):
    manga_info = MangaCreate()
    manga_info.anilist_id = manga_json.get('id')
    manga_info.title_romaji = manga_json.get('title').get('romaji')
    manga_info.title_english = manga_json.get('title').get('english')
    manga_info.title_native = manga_json.get('title').get('native')
    start_date = manga_json.get('startDate')
    if start_date.get('year') and start_date.get('month') and start_date.get('day'):
        manga_info.start_date = f"{start_date.get('year')}-{start_date.get('month')}-{start_date.get('day')}"
    end_date = manga_json.get('endDate')
    if end_date.get('year') and end_date.get('month') and end_date.get('day'):
        manga_info.end_date = f"{end_date.get('year')}-{end_date.get('month')}-{end_date.get('day')}"
    manga_info.description_english = manga_json.get('description')
    manga_info.chapters = manga_json.get('chapters')
    manga_info.volumes = manga_json.get('volumes')
    manga_info.country_of_origin = manga_json.get('country_of_origin')
    manga_info.is_licensed = manga_json.get('is_licensed')
    manga_info.source = manga_json.get('source')
    manga_info.cover_image_large_anilist_url = manga_json.get('coverImage').get('large')
    manga_info.cover_image_medium_anilist_url = manga_json.get('coverImage').get('medium')

    cover_file = requests.get(manga_info.cover_image_large_anilist_url).content
    cover = image.create_image(cover_file, s=s)

    manga_info.is_adult = manga_json.get('isAdult')
    curr_manga = create_manga(m=manga_info, s=s)
    edit_cover_id(curr_manga.id, cover.id, s=s)
    if not curr_manga:
        return None
    if manga_json.get('genres'):
        for genre_name in manga_json.get('genres'):
            curr_genre = genre.get_genre_by_name(name=genre_name, s=s)
            if not curr_genre:
                curr_genre = genre.create_genre(GenreCreate(name=genre_name), s=s)
            add_genre(manga_id=curr_manga.id, genre_id=curr_genre.id, s=s)
    if manga_json.get('staff'):
        for node in manga_json.get('staff').get('nodes'):
            curr_staff = staff.get_staff_by_name(node.get('name').get('full'), s=s)
            if not curr_staff:
                curr_staff = staff.create_staff(StaffCreate(name=node.get('name').get('full')), s=s)
            add_staff(manga_id=curr_manga.id, staff_id=curr_staff.id, s=s)
    return get_manga_full(manga_id=curr_manga.id, s=s)
