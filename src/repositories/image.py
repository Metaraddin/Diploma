from sqlalchemy.orm import Session
from src.db.image import Image


def create_image(file, s: Session):
    avatar = Image()
    avatar.file = file

    s.add(avatar)
    s.commit()
    return avatar


def get_image(id: int, s: Session):
    return s.query(Image).filter(Image.id == id).first()


def delete_image(id: int, s: Session):
    avatar = s.query(Image).filter(Image.id == id).first()
    s.delete(avatar)
    s.commit()
    return avatar