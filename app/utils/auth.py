from passlib.context import CryptContext
from app.databases import get_sqlite_db
from app.exceptions import ResourceNotFoundException,PasswordMismatchException
from app.models.staff import Staff
from datetime import timedelta,datetime,timezone
import jwt
import os
from sqlalchemy.orm import Session
from fastapi import Depends
from zoneinfo import ZoneInfo

# Define the IST timezone
ist = ZoneInfo('Asia/Kolkata')


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_HOURS = os.getenv('ACCESS_TOKEN_EXPIRE_HOURS')
    
pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
# create a new access token
def create_access_token(data : dict,expires_in : timedelta):
    to_encode = data.copy()
    if expires_in:
        expire = datetime.now(ist) + expires_in
    else:
        expire = datetime.now(ist) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt



def verify_password(plain_password,hashed_password):
    """
    Verify if the plain password matches the hashed password.
    """
    if not pwd_context.verify(plain_password, hashed_password):
        raise PasswordMismatchException()
    return True

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email : str, password : str,db:Session):
    users_collection = db.query(Staff).filter(Staff.email == email).first()
    user = users_collection
    if not user:
        raise ResourceNotFoundException("Staff","email",email)
    if not verify_password(password,user.hashed_password):
        return False
    return user


    