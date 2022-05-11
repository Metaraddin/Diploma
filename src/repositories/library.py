from sqlalchemy.orm import Session
from src.db.library import Library
from src.db.manga import Manga


def add_manga(user_id: int, manga_id: int, s: Session):
    library = Library()
    library.user_id = user_id
    library.manga_id = manga_id

    s.add(library)
    try:
        s.commit()
        return library
    except:
        s.rollback()
        return None


def get_manga_from_user(user_id: int, s: Session):
    return s.query(Manga).filter(Manga.id == Library.manga_id).filter(Library.user_id == user_id).join(Library).all()
