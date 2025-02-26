from fastapi import APIRouter,Query,UploadFile,File,Depends,File,UploadFile
from typing import Annotated

from sqlalchemy.orm import Session
from app.databases import get_sqlite_db
from app.exceptions import BadDataException
from app.models import Staff,Student
from app.utils.auth import check_current_user_admin
from app.exceptions import ResourceNotFoundException
from app.schemas import ApiResponse,ImageUploadQueryParams
import os
import uuid
import shutil
upload_file_router = APIRouter()


UPLOAD_DIR = "uploads"
STUDENT_DIR = os.path.join(UPLOAD_DIR, "students")
STAFF_DIR = os.path.join(UPLOAD_DIR, "staff")




@upload_file_router.post("/image")
async def upload_image(query_params: Annotated[ImageUploadQueryParams,Query()],profile_image : UploadFile = File(...),
                       db : Session = Depends(get_sqlite_db),current_user : Staff = Depends(check_current_user_admin)):
    # await check_current_user_admin(current_user)
    
    user_type = query_params.user_type
    user_id = query_params.user_id
    user = None
    
    
    # check if user exists
    if user_type == "STAFF":
        upload_dir = STAFF_DIR
        #check if user exists
        user = db.query(Staff).filter(Staff.staff_id == user_id).first()
        if not user:
            raise ResourceNotFoundException("Staff","staff_id",user_id)
    elif user_type == "STUDENT":
        upload_dir = STUDENT_DIR
        #check if user exists
        user = db.query(Student).filter(Student.student_id == user_id).first()
        if not user:
            raise ResourceNotFoundException("Student","student_id",user_id)
    else:
        raise BadDataException("Invalid user type")
    
    profile_image_url = None
    if profile_image:
        file_extension = profile_image.filename.split(".")[-1]
        file_name = f"{user_id}_{str(uuid.uuid4())}.{file_extension}"
        file_path = os.path.join(upload_dir, file_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
            
        profile_image_url = f"/{upload_dir}/{file_name}"
        
    # print(user_type)
        
    if user_type == "STAFF":
        print(profile_image_url)
        db.query(Staff).filter(Staff.staff_id == user_id).update({"profile_image":file_name}) 
    elif user_type == "STUDENT":
        db.query(Student).filter(Student.student_id == user_id).update({"profile_image":file_name})
    
    
    db.commit()
    db.refresh(user)

    
    user_data = {
        "user_id":user_id,
        "name" : user.name,
        "profile_image":user.profile_image,
    }
    
    api_response =  ApiResponse(status="success",message="Image uploaded successfully",status_code=200,data=user_data)
    return api_response