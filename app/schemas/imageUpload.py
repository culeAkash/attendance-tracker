from pydantic import BaseModel,Field,field_validator
from app.exceptions import BadDataException
class ImageUploadQueryParams(BaseModel):
    user_type : str = Field(...,enum=["STAFF","STUDENT"])
    user_id : str
    
    @classmethod
    @field_validator("user_type")
    def validate_user_type(cls,user_type):
        if user_type not in ["STAFF","STUDENT"]:
            raise BadDataException("Invalid user type")
        return user_type