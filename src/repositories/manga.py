from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.manga import MangaCreate
from src.db.manga import Manga


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
