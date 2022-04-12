from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from src.db.database import DataBase


class Manga(DataBase):
    __tablename__ = 'manga'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    manga_id = 1 ###########
    volume = Column(Integer, nullable=True)
    chapter = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    language = Column(String, nullable=True)
    translator = Column(String, nullable=True)
    price_rub = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)