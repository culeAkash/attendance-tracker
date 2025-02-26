from pydantic import BaseModel,Field,EmailStr,field_validator
from typing import List, Optional
from typing import Optional
import phonenumbers
from .govtid import GovtIdSchema
from app.exceptions import BadDataException
class CreateStaff(BaseModel):
    name: str = Field(...,min_length=3,max_length=20)
    email : EmailStr
    phone_number : str
    password : str = Field(...,min_length=8)
    role : Optional[str] = Field(default="TEACHER")
    govt_id : GovtIdSchema
    
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls,phone_number):
        try:
            parsed_number = phonenumbers.parse(phone_number, "IN")
            if phonenumbers.is_valid_number(parsed_number):
                return phone_number
            else:
                raise BadDataException(detail="Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise BadDataException(detail="Invalid phone number") from e
        
    @field_validator("role")
    @classmethod
    def validate_email(cls,role):
        if role not in ["TEACHER"]:
            raise BadDataException(detail="Only one role can be assigned to a staff")
        return role
        
class StaffResponse(BaseModel):
    staff_id: str
    name: str = Field(...,min_length=3,max_length=20)
    email : EmailStr
    role : str = Field(..., enum=["TEACHER", "PRINCIPAL", "ADMIN"])
    profile_image : Optional[str] = Field(default=None)
    model_config = {'from_attributes': True}
    
    
class GiveAdminPermissionParams(BaseModel):
    staff_id : str
    role : str
    
    @classmethod
    @field_validator("role")
    def validate_role(cls,role):
        if role not in ["TEACHER", "ADMIN"]:
            raise BadDataException("Role must be one of TEACHER, ADMIN")
        return role