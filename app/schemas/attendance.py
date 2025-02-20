from pydantic import BaseModel,Field,field_validator
from datetime import date
from app.models.attendance import StatusOptions
from app.exceptions import BadDataException

class CreateAttendanceQueryParams(BaseModel):
    student_id : str

class CreateAttendanceRequest(BaseModel):
    date_of_attendance : date = Field(..., format="yyyy-MM-dd")
    standard_id : str
    
    @classmethod
    @field_validator("status")
    def validate_status(cls, status):
        if status!= StatusOptions.PRESENT and status!= StatusOptions.ABSENT:
            raise BadDataException("Status must be one of PRESENT or ABSENT")
        return status
    
class AttendanceResponse(BaseModel):
    attendance_id: str
    date_of_attendance : date = Field(..., format="yyyy-MM-dd")
    status : str
    student_id : str
    standard_id : str
    recorded_by_id : str
    model_config = {'from_attributes': True}
    
    