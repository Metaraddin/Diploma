
from sqlalchemy import Column, Integer, String, ForeignKey
from src.db.database import DataBase


class Genre(DataBase):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)