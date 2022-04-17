from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security, File
from fastapi.responses import Response, FileResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.user import UserOut, UserUpdate, UserCreate, UserLogin
from src.models.general import UserToken
from src.repositories import user, avatar
from src.models.token import Token


router = APIRouter(prefix="/user", tags=["User"])
security = HTTPBearer()


@router.post("/", status_code=200, response_model=UserToken)
async def create_user(user_info: UserCreate, session: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Создаёт нового пользователя и возвращает его вместе с access token.
    """
    curr_user = user.create_user(u=user_info, s=session)
    if not curr_user:
        raise HTTPException(status_code=400, detail=[{'msg': 'User with this email already exists'}])
    token = user.create_user_token(curr_user.id, Authorize)
    return UserToken(User=curr_user, Token=token)


@router.post("/login", status_code=200, response_model=Token)
async def login(user_info: UserLogin, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Возвращает access token пользователя в случае успешной проверки.
    """
    curr_user = user.get_user_by_email(email=user_info.email, s=session)
    if not curr_user:
        raise HTTPException(status_code=400, detail=[{'msg': 'User with this email does not exist'}])
    if not user.validate_password(password=user_info.password, hashed_password=curr_user.hashed_password):
        raise HTTPException(status_code=400, detail=[{'msg': 'Incorrect email or password'}])
    return user.create_user_token(id=curr_user.id, Authorize=Authorize)


@router.get("/all", status_code=200, response_model=List[UserOut])
async def get_all_user(limit: int = 100, skip: int = 0, session: Session = Depends(get_db)):
    """
    Возвращает список всех пользователей.
    """
    return user.get_all_user(session, limit, skip)


@router.get("/curr", status_code=200, response_model=UserOut)
async def get_current_user(session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Возвращает авторизованного пользователя.
    """
    Authorize.jwt_required()
    curr_user = user.get_user_by_id(int(Authorize.get_jwt_subject()), session)
    if not curr_user:
        raise HTTPException(status_code=400, detail=[{'msg': 'User with this email does not exist'}])
    return curr_user


@router.delete('/curr', status_code=200, response_model=UserOut)
async def delete_current_user(session: Session = Depends(get_db),
                              Authorize: AuthJWT = Depends()):
    """
    Удаляет и возвращает авторизованного пользователя.
    """
    Authorize.jwt_required()
    return user.delete_user(user_id=int(Authorize.get_jwt_subject()), s=session)


@router.patch("/curr", status_code=200, response_model=UserOut)
async def edit_current_user(user_info: UserUpdate, session: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Перезаписывает поля у авторизованного пользователя.\n
    Необходимо указать **все запрошенные поля**.\n
    Неотправленное/пустое поле приведёт к записи **null** в базу.\n
    Не запрошенные поля недоступны для редактирования.
    """
    Authorize.jwt_required()
    curr_user = user.edit_user(u=user_info, id=int(Authorize.get_jwt_subject()), s=session)
    if not curr_user:
        raise HTTPException(status_code=400, detail=[{'msg': 'Editing failed'}])
    return curr_user


@router.get("/curr/avatar", status_code=200, response_model=UserOut)
async def get_avatar(user_id: int, session: Session = Depends(get_db)):
    """
    Возвращает аватар пользователя по **user.id**.
    """
    curr_user = user.get_user_by_id(user_id, s=session)
    curr_avatar = avatar.get_avatar(curr_user.avatar_id, session)
    if curr_avatar is None:
        return FileResponse('src/avatars/user_default_avatar.png')
    return Response(content=curr_avatar.file, media_type='image/png')


@router.patch("/curr/avatar", status_code=200, response_model=UserOut)
async def edit_current_user_avatar(image: bytes = File(...), session: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends(), auth: HTTPAuthorizationCredentials = Security(security)):
    """
    Устанавливает аватар пользователя по **user.id**.\n
    Аватар хранится в отдельной таблице, user хранит только внешний ключ.
    """
    Authorize.jwt_required()
    mapper = avatar.create_avatar(file=image, s=session)
    return user.edit_avatar_id(user_id=int(Authorize.get_jwt_subject()), avatar_id=mapper.id, s=session)


@router.delete("/curr/avatar", status_code=200, response_model=UserOut)
async def delete_current_user_avatar(session: Session = Depends(get_db),
                                     Authorize: AuthJWT = Depends()):
    """
    Удаляет аватар пользователя по **user.id**.
    """
    Authorize.jwt_required()
    curr_user = user.get_user_by_id(int(Authorize.get_jwt_subject()), s=session)
    curr_avatar = avatar.get_avatar(curr_user.avatar_id, session)
    if curr_avatar is None:
        raise HTTPException(status_code=400, detail=[{'msg': 'The user does not have an avatar'}])
    avatar.delete_avatar(curr_avatar.id, session)
    return user.delete_avatar_id(int(Authorize.get_jwt_subject()), session)


@router.get("/{id}", status_code=200, response_model=UserOut)
async def get_user(id: int, session: Session = Depends(get_db)):
    """
    Возвращает пользователя по **user.id**
    """
    curr_user = user.get_user_by_id(id, session)
    if not curr_user:
        raise HTTPException(status_code=400, detail=[{'msg': 'User with this id does not exist'}])
    return curr_user