from fastapi import APIRouter,Depends

staff_router = APIRouter()

from app.models.staff import Staff
from app.schemas.staff import StaffResponse,CreateStaff
from sqlalchemy.orm import Session
from app.databases import get_sqlite_db


@staff_router.post("/createStaff", response_model=StaffResponse)
async def create_staff(staffData: CreateStaff,db : Session = Depends(get_sqlite_db)) -> StaffResponse:
    to_create_staff = Staff(**staffData.model_dump())
    db.add(to_create_staff)
    db.commit()
    db.refresh(to_create_staff)  # to get the newly generated id in the response
    return to_create_staff

@staff_router.get("/getAllStaff", response_model=list[StaffResponse])
async def get_all_staff(db : Session = Depends(get_sqlite_db)) -> list[StaffResponse]:
    all_staff = db.query(Staff).all()
    return [StaffResponse.model_validate(staff) for staff in all_staff]