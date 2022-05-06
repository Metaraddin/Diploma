from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.models.staff import StaffOut, StaffCreate
from src.repositories import staff


router = APIRouter(prefix="/staff", tags=["Staff"])
security = HTTPBearer()


@router.post("/", status_code=200, response_model=StaffOut)
async def create_staff(staff_info: StaffCreate, session: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Создаёт нового автора.
    """
    curr_staff = staff.create_staff(sm=staff_info, s=session)
    if not curr_staff:
        raise HTTPException(status_code=400, detail=[{'msg': 'This staff already exists'}])
    return curr_staff


@router.get("/", status_code=200, response_model=StaffOut)
async def get_staff(id: int, session: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Возвращает автора.
    """
    curr_staff = staff.get_staff_by_id(id, session)
    if not curr_staff:
        raise HTTPException(status_code=400, detail=[{'msg': 'This staff is not found'}])
    return curr_staff
