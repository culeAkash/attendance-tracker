from fastapi import APIRouter,Query,Depends
from app.schemas import CreateStandardRequest,CreateStandardQueryParams,StandardResponse,ApiResponse
from app.databases import get_sqlite_db
from app.utils.auth import check_current_user_admin_principal
from sqlalchemy.orm import Session
from app.models import Staff,Standard
from typing import Annotated
from app.models import Staff
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from .student import StandardQueryParams
standard_router = APIRouter()


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
        
        standard_response = StandardResponse(standard_id=standard_model_obj.standard_id, grade=standard_model_obj.grade, section=standard_model_obj.section, class_teacher=staff)
        
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
    
    