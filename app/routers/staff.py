from fastapi import APIRouter,Depends,File,UploadFile
from typing import List
from fastapi.responses import JSONResponse

staff_router = APIRouter()

from app.models import Staff,GovtId,UserType,GovtIdTypes
from app.schemas.staff import StaffResponse,CreateStaff
from sqlalchemy.orm import Session
from app.databases import get_sqlite_db
from app.utils.auth import get_password_hash
from app.routers.auth import get_current_user,check_current_user_admin
from app.schemas.responses import ApiResponse
from app.schemas.govtid import GovtIdSchema


@staff_router.post("/createStaff", status_code=201)
async def create_staff(staffData: CreateStaff,db : Session = Depends(get_sqlite_db),current_user : Staff = Depends(get_current_user)):
    
    # check if staff is admin
    current_user = await check_current_user_admin(current_user)
    

    #check if staff with email or phone number already exists
    Staff.check_staff_by_email_phone(email=staffData.email,phone=staffData.phone_number,db=db)
    govt_id_data = staffData.govt_id
    hashed_password = get_password_hash(staffData.password)
    staffData.__delattr__("password")
    staffData.__delattr__("govt_id")
    to_create_staff = Staff(**staffData.model_dump(),hashed_password=hashed_password)
    # to_create_staff.__delattr__("password")
    db.add(to_create_staff)
    db.flush()
    db.refresh(to_create_staff)  # to get the newly generated id in the response
    
    # TODO : ADD govt id to database after checking
    # check if govt id exists in the database
    
    GovtId.check_if_id_exists(id_number=govt_id_data.id_number,user_type=UserType.STAFF,db=db)
    govt_id_data = GovtIdSchema(**govt_id_data.model_dump())
    govt_id_model = GovtId(id_type=govt_id_data.id_type,id_number=govt_id_data.id_number,user_id=to_create_staff.staff_id,user_type=UserType.STAFF)
    
    
    db.add(govt_id_model)
    db.flush()
    db.refresh(govt_id_model)
    db.commit()
    
    staff_response = StaffResponse(
        staff_id=to_create_staff.staff_id,
        name=to_create_staff.name,
        email=to_create_staff.email,
        role=to_create_staff.role,
        govt_id=GovtIdSchema(
            id_type=govt_id_model.id_type,
            id_number=govt_id_model.id_number,
        )
    )
    
    return ApiResponse[StaffResponse](status="success", message="Staff Created Successfully", status_code=201, data=staff_response)

@staff_router.get("/getAllStaff", response_model=ApiResponse[List[StaffResponse]])
async def get_all_staff(current_user : Staff =Depends(get_current_user),db : Session = Depends(get_sqlite_db)):
    all_staff = db.query(Staff).all()
    # print(all_staff,"........>>>>>>>>>>>>")
    staff_responses = [StaffResponse.model_validate(staff) for staff in all_staff]
    print(staff_responses)
    return ApiResponse[List[StaffResponse]](status="success", message="All Staff", status_code=200, data=staff_responses)

@staff_router.get("/get_staff_image/{staff_id}")
async def get_staff_image(staff_id :str,db: Session = Depends(get_sqlite_db)):
    staff = Staff.get_staff_by_staff_id(staff_id=staff_id,db=db)
    return ApiResponse(
        status="success",
        message="Staff Image",
        status_code=200,
        data=staff.profile_image,
    )