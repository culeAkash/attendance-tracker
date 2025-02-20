from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends,HTTPException,status,APIRouter,Response,Request
import os
import jwt
from jwt.exceptions import InvalidTokenError,ExpiredSignatureError
from pydantic import BaseModel
from app.databases import get_sqlite_db
from app.models.staff import Staff,StaffRole
from app.exceptions import ResourceNotFoundException,NotPermittedException
from app.utils.auth import authenticate_user,create_access_token
from datetime import timedelta
from sqlalchemy.orm import Session
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    
class TokenData(BaseModel):
    email : str
    
class LoginData(BaseModel):
    email : str
    password : str
    
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
    
    return "User Logged in successfully"

@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

def get_user(email:str,db:Session):
    user = db.query(Staff).filter(Staff.email == email).first()
    if not user:
        raise ResourceNotFoundException("Staff","email",email)
    return user

async def check_current_user_admin_principal(user : Staff):
    print(">>>>>>>>>>>>>>>>>>",user.role)
    if user.role!= StaffRole.ADMIN and user.role!=StaffRole.PRINCIPAL:
        raise NotPermittedException()
    return user
    

async def check_current_user_teacher(user : Staff):
    if user.role!= StaffRole.TEACHER:
        raise NotPermittedException()
    return user

async def get_current_user(request: Request,db: Session = Depends(get_sqlite_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get the token from the HTTP-only cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise credentials_exception
    
    # Remove the "Bearer " prefix
    # token = access_token.replace("Bearer ", "")
    
    print(access_token)
    try:
        payload = jwt.decode(access_token,SECRET_KEY,algorithms=[ALGORITHM])
        email = payload.get('sub')
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except ExpiredSignatureError:
        raise expired_token_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(email=token_data.email,db=db)
    if user is None:
        raise credentials_exception
    return user

