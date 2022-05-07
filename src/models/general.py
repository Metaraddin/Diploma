from pydantic import BaseModel
from src.models.token import Token
from src.models.user import UserOut
from src.models.manga import MangaOut
from src.models.genre import GenreOut
from src.models.staff import StaffOut
from typing import Optional, List


class UserToken(BaseModel):
    User: Optional[UserOut]
    Token: Optional[Token]


class MangaGenreStaff(BaseModel):
    Manga: Optional[MangaOut]
    Genres: Optional[List[GenreOut]]
    Staff: Optional[List[StaffOut]]

    class Config:
        orm_mode = True