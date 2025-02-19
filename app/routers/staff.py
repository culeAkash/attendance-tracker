from fastapi import APIRouter,Depends
from typing import List
from fastapi.responses import JSONResponse

staff_router = APIRouter()

from app.models.staff import Staff
from app.schemas.staff import StaffResponse,CreateStaff
from sqlalchemy.orm import Session
from app.databases import get_sqlite_db
from app.utils.auth import get_password_hash
from app.routers.auth import get_current_user
from app.schemas.responses import ApiResponse


@staff_router.post("/createStaff", status_code=201)
async def create_staff(staffData: CreateStaff,db : Session = Depends(get_sqlite_db)):
    
    #check if staff with email or phone number already exists
    Staff.check_staff_by_email_phone(email=staffData.email,phone=staffData.phone_number,db=db)

    hashed_password = get_password_hash(staffData.password)
    staffData.__delattr__("password")
    to_create_staff = Staff(**staffData.model_dump(),hashed_password=hashed_password)
    # to_create_staff.__delattr__("password")
    db.add(to_create_staff)
    db.commit()
    db.refresh(to_create_staff)  # to get the newly generated id in the response
    return ApiResponse[StaffResponse](status="success", message="Staff Created Successfully", status_code=201, data=StaffResponse.model_validate(to_create_staff))

@staff_router.get("/getAllStaff", response_model=ApiResponse[List[StaffResponse]])
async def get_all_staff(current_user : Staff =Depends(get_current_user),db : Session = Depends(get_sqlite_db)):
    all_staff = db.query(Staff).all()
    # print(all_staff,"........>>>>>>>>>>>>")
    staff_responses = [StaffResponse.model_validate(staff) for staff in all_staff]
    print(staff_responses)
    return ApiResponse[List[StaffResponse]](status="success", message="All Staff", status_code=200, data=staff_responses)