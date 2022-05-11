from sqlalchemy import Column, Integer, ForeignKey
from src.db.database import DataBase
from src.db.manga import Manga
from src.db.user import User


class Library(DataBase):
    __tablename__ = 'library'
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    manga_id = Column(Integer, ForeignKey(Manga.id), primary_key=True, nullable=False)
