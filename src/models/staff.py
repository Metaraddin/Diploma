from pydantic import BaseModel


class StaffCreate(BaseModel):
    name: str


class StaffOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True