from sqlalchemy.orm import Session
from src.db.staff import Staff
from src.models.staff import StaffCreate


def create_staff(sm: StaffCreate, s: Session):
    staff = Staff()
    staff.name = sm.name

    s.add(staff)
    s.commit()
    return staff


def get_staff_by_id(id: int, s: Session):
    return s.query(Staff).filter(Staff.id == id).first()