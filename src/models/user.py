from typing import Optional
from pydantic import BaseModel, EmailStr, validator, constr


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


class UserUpdate(BaseModel):
    password: constr(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=6)