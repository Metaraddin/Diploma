from pydantic import BaseModel
from src.models.token import Token
from src.models.user import UserOut
from typing import Optional


class UserToken(BaseModel):
    User: Optional[UserOut]
    Token: Optional[Token]
