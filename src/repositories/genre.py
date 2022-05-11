from sqlalchemy.orm import Session
from src.db.genre import Genre
from src.models.genre import GenreCreate
from sqlalchemy.exc import IntegrityError, PendingRollbackError


def create_genre(g: GenreCreate, s: Session):
    genre = Genre()
    genre.name = g.name

    s.add(genre)
    try:
        s.commit()
        return genre
    except:
        s.rollback()
        return None


def get_genre_by_id(id: int, s: Session):
    return s.query(Genre).filter(Genre.id == id).first()


def get_genre_by_name(name: str, s: Session):
    return s.query(Genre).filter(Genre.name == name).first()


def get_all_genre(s: Session):
    return s.query(Genre).all()
