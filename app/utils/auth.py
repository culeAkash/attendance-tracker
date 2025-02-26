from passlib.context import CryptContext
from app.databases import get_sqlite_db
from app.exceptions import ResourceNotFoundException,PasswordMismatchException
from app.models.staff import Staff
from datetime import timedelta,datetime
import jwt
import os
from sqlalchemy.orm import Session
from fastapi import Depends
from zoneinfo import ZoneInfo
from fastapi import Depends,HTTPException,status,Request
import os
import jwt
from jwt.exceptions import InvalidTokenError,ExpiredSignatureError
from app.databases import get_sqlite_db
from app.models.staff import Staff,StaffRole
from app.exceptions import ResourceNotFoundException,NotPermittedException
from datetime import timedelta
from sqlalchemy.orm import Session
from app.schemas import TokenData
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


def get_user(email:str,db:Session):
    user = db.query(Staff).filter(Staff.email == email).first()
    if not user:
        raise ResourceNotFoundException("Staff","email",email)
    return user

async def check_current_user_admin_principal(request: Request,db: Session = Depends(get_sqlite_db)):
    user = await get_current_user(request=request,db=db)
    print(">>>>>>>>>>>>>>>>>>",user.role)
    if user.role!= StaffRole.ADMIN and user.role!=StaffRole.PRINCIPAL:
        raise NotPermittedException()
    return user
    

async def check_current_user_teacher(request: Request,db: Session = Depends(get_sqlite_db)):
    user = await get_current_user(request=request,db=db)
    if user.role!= StaffRole.TEACHER:
        raise NotPermittedException()
    return user

async def check_current_user_principal(request: Request,db: Session = Depends(get_sqlite_db)):
    user = await get_current_user(request=request,db=db)
    if user.role!= StaffRole.PRINCIPAL:
        raise NotPermittedException()
    return user


async def check_current_user_admin(request: Request,db: Session = Depends(get_sqlite_db)):
    user = await get_current_user(request=request,db=db)
    if user.role!= StaffRole.ADMIN:
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