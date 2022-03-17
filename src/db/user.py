
from sqlalchemy import Column, Integer, String, ForeignKey
from src.db.database import DataBase


class User(DataBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    anilist_auth_code = Column(String, nullable=True)