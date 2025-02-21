from app.databases import Base
from sqlalchemy import Column, Integer,Enum,String
import uuid
import enum
from sqlalchemy.orm import relationship
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
    
    user = relationship(
        "User", back_populates="govt_ids", primaryjoin="or_("
            "and_(Student.student_id == GovtId.user_id, GovtId.user_type == 'STUDENT'),"
            "and_(Staff.staff_id == GovtId.user_id, GovtId.user_type == 'STAFF')"
        ")"
    )