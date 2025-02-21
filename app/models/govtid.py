from app.databases import Base
from sqlalchemy import Column, Integer,Enum,String,Boolean
import uuid
import enum
from sqlalchemy.orm import relationship,Session
from app.exceptions import BadDataException
class GovtIdTypes(enum.Enum):
    PASSPORT = "PASSPORT"
    AADHAR = "AADHAR_CARD"
    DRIVINGLICENSE = "DRIVING_LICENSE"
    PAN = "PAN_CARD"
    VOTER_ID = "VOTER_ID_CARD"
    
class UserType(enum.Enum):
    STUDENT = "STUDENT"
    STAFF = "STAFF"


class GovtId(Base):
    __tablename__ = "govt_ids"
    id = Column(Integer, primary_key=True,default=lambda:str(uuid.uuid4()))
    id_type = Column(Enum(GovtIdTypes), nullable=False)
    id_number = Column(String, nullable=False, unique=True)
    
    user_id = Column(String, nullable=False,index=True, unique=True)
    user_type = Column(Enum(UserType), nullable=False, index=True)
    is_synced = Column(Boolean, default=False)
    
    @staticmethod
    def check_if_id_exists(id_number : str, user_type : str, db :Session):
        govt_id = db.query(GovtId).filter(GovtId.id_number == id_number, GovtId.user_type == user_type).first()
        if govt_id:
            raise BadDataException(f"Govt ID {id_number} already exists for another {user_type}")
        return None
        