import random
import hashlib
import string

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.user import UserCreate, UserUpdate
from src.models.token import Token
from src.db.user import User


def __hash_password(**password: str, salt: str = None):
    if salt is None:
        salt = "".join(random.choice(string.ascii_letters) for _ in range(12))
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


def validate_password(password: str, hashed_password: str):
    salt, hashed = hashed_password.split("$")
    return __hash_password(password, salt) == hashed


def create_user_token(id: int, Authorize):
    access_token = Authorize.create_access_token(subject=id)
    Authorize.set_access_cookies(access_token)
    return Token(access_token=access_token)


def create_user(u: UserCreate, s: Session):
    user = User()
    user.email = u.email
    salt = "".join(random.choice(string.ascii_letters) for _ in range(12))
    hashed_password = __hash_password(salt=salt, password=u.password)
    user.hashed_password = f"{salt}${hashed_password}"

    s.add(user)
    try:
        s.commit()
        return user
    except IntegrityError:
        return None


def get_user_by_email(email: str, s: Session):
    return s.query(User).filter(User.email == email).first()


def get_user_by_id(id: int, s: Session):
    return s.query(User).filter(User.id == id).first()


def get_all_user(s: Session, limit: int = 100, skip: int = 0):
    return s.query(User).limit(limit).offset(skip).all()


def edit_user(u: UserUpdate, id: int, s: Session):
    user = s.query(User).filter(User.id == id).first()
    salt = "".join(random.choice(string.ascii_letters) for _ in range(12))
    hashed_password = __hash_password(salt=salt, password=u.password)
    user.hashed_password = f"{salt}${hashed_password}"

    s.add(user)
    s.commit()
    return user


def edit_walker_id(user_id: int, walker_id: int, s: Session):
    user = s.query(User).filter(User.id == user_id).first()
    user.walker_id = walker_id

    s.add(user)
    s.commit()
    return user


def delete_user(user_id: int, s: Session):
    user = s.query(User).filter(User.id == user_id).first()
    s.delete(user)
    s.commit()
    return user


def edit_avatar_id(user_id: int, avatar_id: int, s: Session):
    user = s.query(User).filter(User.id == user_id).first()
    user.avatar_id = avatar_id

    s.add(user)
    s.commit()
    return user


def delete_avatar_id(user_id: int, s: Session):
    user = s.query(User).filter(User.id == user_id).first()
    user.avatar_id = None

    s.add(user)
    s.commit()
    return user


def set_anilist_token(anilist_token: str, user_id: int, s: Session):
    user = s.query(User).filter(User.id == user_id).first()
    user.anilist_token = anilist_token

    s.add(user)
    s.commit()
    return anilist_token


def get_anilist_token(user_id: int, s: Session):
    return s.query(User.anilist_token).filter(User.id == user_id).first()[0]
