from fastapi import APIRouter,Depends,Query
from app.schemas.student import CreateStudent,StudentResponse
from app.models.staff import Staff
from app.routers.auth import get_current_user,check_current_user_admin_principal
from app.databases import get_sqlite_db
from sqlalchemy.orm import Session
from app.models  import Student,Parent,Address,Standard
from pydantic import BaseModel
from typing import Annotated
student_router = APIRouter()

class StudentCreateParams(BaseModel):
    grade : str
    section : str

@student_router.post("/create_student")
async def create_student(student_data :CreateStudent,standard_query :Annotated[StudentCreateParams,Query()],current_user : Staff =Depends(get_current_user),db : Session = Depends(get_sqlite_db)) -> StudentResponse:
    try:
        # begin a transaction
        # db.close()
        # db.begin()
        
        # create address data
        current_user = await check_current_user_admin_principal(current_user)
        address_data = student_data.address
        address_model_data = Address(**address_data.model_dump())
        db.add(address_model_data)
        db.flush()
        # create parent data
        student_parent_data = student_data.parent
        student_parent_model_data = Parent(**student_parent_data.model_dump())
        db.add(student_parent_model_data)
        db.flush()
        #TODO : check if standard exists of given grade and section
        standard = Standard.get_standard_by_grade_and_section(standard_query.grade, standard_query.section)

    
        # create student data
        student_data.__delattr__("address")
        student_data.__delattr__("parent")
        
        db.refresh(student_parent_model_data)
        db.refresh(address_model_data)
        
        
        student_model_data = Student(**student_data.model_dump())
        student_model_data.standard_id = standard.standard_id
        student_model_data.parent_id = student_parent_model_data.parent_id
        student_model_data.address_id = address_model_data.address_id

        db.add(student_model_data)
        db.flush()
        db.refresh(student_model_data)
        print(student_data.address,address_model_data)
        db.commit()
        return student_model_data
    except Exception as e:
        db.rollback()
        print(e)
        raise Exception(e)
    finally:
        # commit the transaction
        db.close()
    
    
    
    