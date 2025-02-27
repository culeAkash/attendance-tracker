from pydantic import BaseModel,field_validator,Field
from app.exceptions import BadDataException
from app.models import GovtIdTypes
from typing import Optional

class GovtIdSchema(BaseModel):
    id_type: str = Field(..., enum=["PASSPORT","AADHAR_CARD","DRIVING_LICENSE","PAN_CARD","VOTER_ID_CARD"])
    id_number: str
    
    
    @field_validator("id_type")
    @classmethod
    def validate_id_type(cls, id_type):
        if id_type not in ["PASSPORT","AADHAR_CARD","DRIVING_LICENSE","PAN_CARD","VOTER_ID_CARD"]:
            raise BadDataException("Invalid ID type")
        return id_type
    
class UpdateGovtIdSchema(BaseModel):
    id_type: Optional[str] = Field(None, enum=["PASSPORT","AADHAR_CARD","DRIVING_LICENSE","PAN_CARD","VOTER_ID_CARD"])
    id_number: Optional[str] = Field(None)
    
    @field_validator("id_type")
    @classmethod
    def validate_id_type(cls, id_type):
        if id_type is not None and id_type not in ["PASSPORT","AADHAR_CARD","DRIVING_LICENSE","PAN_CARD","VOTER_ID_CARD"]:
            raise BadDataException("Invalid ID type")
        return id_type