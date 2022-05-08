from sqlalchemy import Column, Integer, String, LargeBinary
from src.db.database import DataBase


class Image(DataBase):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    file = Column(LargeBinary, nullable=False)