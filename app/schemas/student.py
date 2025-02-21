from pydantic import BaseModel,Field,EmailStr,field_validator
import phonenumbers
from .parent import ParentCreate,ParentResponse
from datetime import date,datetime
from typing import Optional
from .govtid import GovtIdSchema
class AddressCreate(BaseModel):
    street : str = Field(..., min_length=5, max_length=50)
    city : str = Field(..., min_length=3, max_length=20)
    state : str = Field(..., min_length=3, max_length=20)
    country : str = Field(..., min_length=3, max_length=20)
    
class AddressResponse(BaseModel):
    address_id : str
    street : str = Field(..., min_length=5, max_length=50)
    city : str = Field(..., min_length=3, max_length=20)
    state : str = Field(..., min_length=3, max_length=20)
    country : str = Field(..., min_length=3, max_length=20)
    model_config = {'from_attributes': True}

class CreateStudent(BaseModel):
    name : str = Field(...,min_length=5,max_length=20)
    date_of_birth : date = Field(..., format="yyyy-MM-dd")
    gender : str = Field(...,enum=["MALE","FEMALE"])
    profile_image : Optional[str]
    govt_id : GovtIdSchema
    parent : ParentCreate 
    address : AddressCreate
    
    @field_validator("gender")
    @classmethod
    def validate_gender(cls,gender):
        if gender not in ["MALE","FEMALE"]:
            raise ValueError("Invalid gender")
        return gender

class StudentStandardResponse(BaseModel):
    standard_id : str
    grade : str 
    section : str 
    model_config = {'from_attributes': True}
        
class StudentResponse(BaseModel):
    student_id : str
    name : str = Field(...,min_length=5,max_length=20)
    roll_number : int = Field(..., gt=0)
    date_of_birth : date
    gender : str = Field(...,enum=["MALE","FEMALE"])
    profile_image : Optional[str]
    govt_id : GovtIdSchema
    standard : StudentStandardResponse
    address : AddressResponse
    parent : ParentResponse
    
    model_config = {'from_attributes': True}