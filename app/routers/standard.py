from fastapi import APIRouter,Query,Depends
from app.schemas import CreateStandardRequest,CreateStandardQueryParams,StandardResponse,ApiResponse,StandardQueryParams
from app.databases import get_sqlite_db
from app.utils.auth import check_current_user_admin_principal,get_current_user
from sqlalchemy.orm import Session
from app.models import Staff,Standard,UserType
from typing import Annotated
from app.models import Staff
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
import logging

standard_router = APIRouter()

# Configure logging
logging.basicConfig(filename="activity.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@standard_router.post("/create_standard",status_code=201)
async def create_standard(standard_data : CreateStandardRequest,standard_params : Annotated[CreateStandardQueryParams,Query()],current_user : Staff = Depends(check_current_user_admin_principal),db:Session = Depends(get_sqlite_db)) -> JSONResponse:
    try:
        # check if currently logged in user has the permission to create a new standard
        # current_user = await check_current_user_admin_principal(current_user)
    
        #check for valid teacher id
        staff = Staff.get_staff_by_staff_id(standard_params.class_teacher_id,db=db)
        section = Standard.get_next_section(grade=standard_data.grade,db=db)
        # create standard object
        standard_model_obj = Standard(grade=standard_data.grade,class_teacher_id=staff.staff_id,section=section)
        
        db.add(standard_model_obj)
        db.flush()
        db.refresh(standard_model_obj)
        
        standard_response = StandardResponse(standard_id=standard_model_obj.standard_id, grade=Standard.get_mapped_grade_by_enum_string(standard_model_obj.grade), section=standard_model_obj.section, class_teacher=staff)
        
        api_response = ApiResponse[StandardResponse](
            success=True,
            message="Standard created successfully",
            status_code=201,
            data=standard_response
        )
        db.commit()
        return api_response
    except HTTPException as e:
        db.rollback()
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    finally:
        db.close()
    
    
    
@standard_router.get("/get_standard_by_grade_and_section",status_code=200)
async def get_standard_class_teacher(standard_query : Annotated[StandardQueryParams,Query()],db:Session = Depends(get_sqlite_db)):
    standard = Standard.get_standard_by_grade_and_section(standard_query.grade,standard_query.section,db)
    
    standard_response = StandardResponse(standard_id=standard.standard_id, grade=standard.grade, section=standard.section, class_teacher=standard.class_teacher)
    
    return ApiResponse(
        status="success",
        message="Standard fetched successfully",
        status_code=200,
        data=standard_response
    )
    
# TODO : testing to be done
@standard_router.get("/get_all_standard_for_staff")
async def get_all_standard_of_class_teacher(db : Session = Depends(get_sqlite_db),current_user : Staff = Depends(get_current_user)):
    try:
        # if current_user is not TEACHER fetch all the classes
        # else fetch only the classes of the current user
        if  current_user.role == UserType.TEACHER:
            standards = Standard.get_standards_by_class_teacher_id(class_teacher_id=current_user.staff_id,db=db)
        else:
            standards = db.query(Standard).all()
        
        standards_response = [StandardResponse(standard_id=standard.standard_id, grade=Standard.get_mapped_grade_by_enum_string(standard.grade), section=standard.section, class_teacher=standard.class_teacher) for standard in standards]
        return ApiResponse(
            status="success",
            message="Standards fetched successfully",
            status_code=200,
            data=standards_response
        )
    except HTTPException as e:
        db.rollback()
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    finally:
        db.close()
        
        
@standard_router.get("/get_all_standards")
async def get_all_standards(db : Session = Depends(get_sqlite_db)):
    standards = db.query(Standard).all()
    # logging.info(f"grade : {standards[0].grade}, type : {type(standards[0].grade)}")
    standards_response = [StandardResponse(standard_id=standard.standard_id, grade=Standard.get_mapped_grade_by_enum_string(standard.grade), section=standard.section, class_teacher=standard.class_teacher) for standard in standards]
    return ApiResponse(
        status="success",
        message="Standards fetched successfully",
        status_code=200,
        data=standards_response
    )