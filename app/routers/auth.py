from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status,APIRouter,Response
import os
from app.schemas import LoginData
from app.databases import get_sqlite_db
from app.utils.auth import authenticate_user,create_access_token
from datetime import timedelta
from sqlalchemy.orm import Session
from app.schemas import ApiResponse
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    

    
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_HOURS = os.getenv('ACCESS_TOKEN_EXPIRE_HOURS')
auth_router = APIRouter()


@auth_router.post("/login")
async def login_for_access_token(loginData : LoginData,response : Response,db : Session = Depends(get_sqlite_db)):
    staff = authenticate_user(loginData.email,loginData.password,db)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(hours=float(ACCESS_TOKEN_EXPIRE_HOURS))
    access_token = create_access_token(data={
        "sub" : staff.email,
    },expires_in=access_token_expires)
    
    # Set the access token in an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        max_age=int(access_token_expires.total_seconds())
    )
    
    return ApiResponse(
        status = "success",
        message = "Login successful",
        status_code = 200,
        data = {
            "user_id" : staff.staff_id,
            "email" : staff.email,
            "role" : staff.role,
            "name" : staff.name,
        }
    )

@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}



