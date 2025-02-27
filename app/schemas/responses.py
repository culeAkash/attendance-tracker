from datetime import datetime,date
from datetime import timezone
from typing import Union, List, Dict, Any,Generic,TypeVar
from pydantic.generics import GenericModel
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo

# Define the IST timezone
ist = ZoneInfo('Asia/Kolkata')

# Define a type variable for the generic data type
T = TypeVar('T')
class ApiResponse(GenericModel,Generic[T]):
    status: str = 'success'
    message: str
    status_code: int
    time_stamp: str = Field(default_factory=lambda: datetime.now(ist).isoformat()) 
    data: T = []
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()  # Convert date to "YYYY-MM-DD"
        }
    
class GenericExceptionResponse(GenericModel,Generic[T]):
    status: str = 'error'
    message: str
    status_code: int
    time_stamp: datetime = datetime.now(ist)
    data: T = []