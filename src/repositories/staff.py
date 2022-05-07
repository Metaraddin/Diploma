from sqlalchemy.orm import Session
from src.db.staff import Staff
from src.models.staff import StaffCreate
from sqlalchemy.exc import IntegrityError, PendingRollbackError


def create_staff(sm: StaffCreate, s: Session):
    staff = Staff()
    staff.name = sm.name

    s.add(staff)
    try:
        s.commit()
    except IntegrityError:
        s.rollback()
        return None
    return staff


def get_staff_by_id(id: int, s: Session):
    return s.query(Staff).filter(Staff.id == id).first()


def get_staff_by_name(name: str, s: Session):
    return s.query(Staff).filter(Staff.name == name).first()
