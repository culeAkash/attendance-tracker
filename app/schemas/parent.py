from pydantic import BaseModel,Field,EmailStr,field_validator
import phonenumbers
class ParentCreate(BaseModel):
    name : str = Field(...,min_length=3,max_length=20)
    email : EmailStr
    phone : str
    
    @field_validator("phone")
    def validate_phone(cls,phone):
        try:
            parsed_number = phonenumbers.parse(phone, "IN")
            if phonenumbers.is_valid_number(parsed_number):
                return phone
            else:
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise ValueError("Invalid phone number") from e
        
class ParentResponse(BaseModel):
    parent_id : str
    name : str = Field(...,min_length=3,max_length=20)
    email : EmailStr
    phone : str
    model_config = {'from_attributes': True}