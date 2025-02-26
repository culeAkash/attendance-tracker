from pydantic import BaseModel,field_validator
from .staff import StaffResponse
from app.exceptions import BadDataException


class CreateStandardRequest(BaseModel):
    grade : str
    
    @field_validator("grade")
    @classmethod
    def validate_grade(cls, grade):
        if grade not in ["NURSERY", "UKG", "LKG", "STD_1", "STD_2", "STD_3", "STD_4", "STD_5", "STD_6", "STD_7", "STD_8", "STD_9", "STD_10", "STD_11", "STD_12"]:
            raise BadDataException("Invalid grade. Grade should be one of NURSERY, UKG, LKG, STD_1, STD_2, STD_3, STD_4, STD_5, STD_6, STD_7, STD_8, STD_9, STD_10, STD_11, STD_12")
        return grade
    
class CreateStandardQueryParams(BaseModel):
    class_teacher_id : str

class StandardResponse(BaseModel):
    standard_id : str
    grade : str
    section : str
    class_teacher : StaffResponse
    
    model_config = {'from_attributes': True}
    


class StandardQueryParams(BaseModel):
    grade : str
    section : str
    
    @field_validator("grade")
    @classmethod
    def validate_grade(cls, grade):
        if grade not in ["NURSERY", "UKG", "LKG", "STD_1", "STD_2", "STD_3", "STD_4", "STD_5", "STD_6", "STD_7", "STD_8", "STD_9", "STD_10", "STD_11", "STD_12"]:
            raise BadDataException("Invalid grade. Grade should be one of NURSERY, UKG, LKG, STD_1, STD_2, STD_3, STD_4, STD_5, STD_6, STD_7, STD_8, STD_9, STD_10, STD_11, STD_12")
        return grade