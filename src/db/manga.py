from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from src.db.database import DataBase


class Manga(DataBase):
    __tablename__ = 'manga'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    anilist_id = Column(Integer, nullable=True)
    title_romaji = Column(String, nullable=True)
    title_english = Column(String, nullable=True)
    title_russian = Column(String, nullable=True)
    title_native = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description_english = Column(String, nullable=True)
    description_russian = Column(String, nullable=True)
    chapters = Column(Integer, nullable=True)
    volumes = Column(Integer, nullable=True)
    country_of_origin = Column(String, nullable=True)
    country_of_origin = Column(String, nullable=True)
    is_licensed = Column(Boolean, nullable=True)
    source = Column(String, nullable=True)
    cover_image_large_anilist_url = Column(String, nullable=True)
    cover_image_medium_anilist_url = Column(String, nullable=True)
    cover_image = 1 ##############
    genres = 1 ############
    staff = 1 ############
    is_adult = Column(Boolean, nullable=True)