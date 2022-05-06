from sqlalchemy.orm import Session
from src.db.genre import Genre
from src.models.genre import GenreCreate


def create_genre(g: GenreCreate, s: Session):
    genre = Genre()
    genre.name = g.name

    s.add(genre)
    s.commit()
    return genre


def get_genre_by_id(id: int, s: Session):
    return s.query(Genre).filter(Genre.id == id).first()