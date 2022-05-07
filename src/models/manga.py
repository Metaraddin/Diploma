from pydantic import BaseModel
from src.models.token import Token
from src.models.user import UserOut
from typing import Optional, List
from datetime import datetime, date


# class Manga(BaseModel):
#     id: int
#     anilist_id: Optional[int]
#     title_romaji: Optional[str]
#     title_english: Optional[str]
#     title_russian: Optional[str]
#     title_native: Optional[str]
#     start_date: Optional[datetime]
#     end_date: Optional[datetime]
#     description_english: Optional[str]
#     description_russian: Optional[str]
#     chapters: Optional[int]
#     volumes: Optional[int]
#     country_of_origin: Optional[str]
#     is_licensed: Optional[bool]
#     source: Optional[str]
#     cover_image_large_anilist_url: Optional[str]
#     cover_image_medium_anilist_url: Optional[str]
#     cover_id: Optional[int]
#     genres: Optional
#     staff: Optional[List[str]]
#     is_adult: bool = False


class MangaCreate(BaseModel):
    anilist_id: Optional[int]
    title_romaji: Optional[str]
    title_english: Optional[str]
    title_russian: Optional[str]
    title_native: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    description_english: Optional[str]
    description_russian: Optional[str]
    chapters: Optional[int]
    volumes: Optional[int]
    country_of_origin: Optional[str]
    is_licensed: Optional[bool]
    source: Optional[str]
    cover_image_large_anilist_url: Optional[str]
    cover_image_medium_anilist_url: Optional[str]
    # cover_id
    # genres
    # staff
    is_adult: bool = False


class MangaOut(BaseModel):
    id: Optional[int]
    anilist_id: Optional[int]
    title_romaji: Optional[str]
    title_english: Optional[str]
    title_russian: Optional[str]
    title_native: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    description_english: Optional[str]
    description_russian: Optional[str]
    chapters: Optional[int]
    volumes: Optional[int]
    country_of_origin: Optional[str]
    is_licensed: Optional[bool]
    source: Optional[str]
    cover_image_large_anilist_url: Optional[str]
    cover_image_medium_anilist_url: Optional[str]
    # cover_id
    # genres
    # staff
    is_adult: bool = False

    class Config:
        orm_mode = True

