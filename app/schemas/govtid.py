from pydantic import BaseModel,field_validator
from app.exceptions import BadDataException
from app.models import GovtIdTypes

class GovtIdSchema(BaseModel):
    id_type: str
    id_number: str
    
    
    @field_validator("id_type")
    @classmethod
    def validate_id_type(cls, id_type):
        if id_type not in [GovtIdTypes.AADHAR,GovtIdTypes.DRIVINGLICENSE,GovtIdTypes.PAN,GovtIdTypes.PASSPORT,GovtIdTypes.VOTER_ID]:
            raise BadDataException("Invalid ID type")
        return id_type