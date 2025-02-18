from pydantic import BaseModel,Field,EmailStr,field_validator
import phonenumbers
class CreateStaff(BaseModel):
    name: str = Field(...,min_length=3,max_length=20)
    email : EmailStr
    phone_number : str
    password : str = Field(...,min_length=8)
    role : str = Field(..., enum=["TEACHER", "PRINCIPAL", "ADMIN"])
    
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls,phone_number):
        try:
            parsed_number = phonenumbers.parse(phone_number, "IN")
            if phonenumbers.is_valid_number(parsed_number):
                return phone_number
            else:
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise ValueError("Invalid phone number") from e
        
    @field_validator("role")
    @classmethod
    def validate_role(cls,role):
        if role not in ["TEACHER", "PRINCIPAL", "ADMIN"]:
            raise ValueError("Invalid role")
        return role
        
class StaffResponse(BaseModel):
    staff_id: str
    name: str = Field(...,min_length=3,max_length=20)
    email : EmailStr
    role : str = Field(..., enum=["TEACHER", "PRINCIPAL", "ADMIN"])
    
    model_config = {'from_attributes': True}