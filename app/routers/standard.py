from fastapi import APIRouter,Query,Depends
from app.schemas import CreateStandardRequest,CreateStandardQueryParams,StandardResponse,ApiResponse
from app.databases import get_sqlite_db
from app.routers.auth import check_current_user_admin_principal,get_current_user
from sqlalchemy.orm import Session
from app.models import Staff,Standard
from typing import Annotated
from app.models import Staff
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
standard_router = APIRouter()


@standard_router.post("/create_standard",status_code=201)
async def create_standard(standard_data : CreateStandardRequest,standard_params : Annotated[CreateStandardQueryParams,Query()],current_user : Staff = Depends(get_current_user),db:Session = Depends(get_sqlite_db)) -> JSONResponse:
    try:
        # check if currently logged in user has the permission to create a new standard
        current_user = await check_current_user_admin_principal(current_user)
    
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
    
    
    