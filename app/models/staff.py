from sqlalchemy import Column,Integer,String,Enum,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import enum
from app.databases import Base

class StaffRole(enum.Enum):
    TEACHER = "TEACHER"
    PRINCIPAL = "PRINCIPAL"
    ADMIN = "ADMIN"
    
class Staff(Base):
    __tablename__ = "staff"
    staff_id = Column(String,primary_key=True,index=True,default=lambda:str(uuid.uuid4()))
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True,index=True)
    phone_number = Column(String,nullable=False,unique=True)
    hashed_password = Column(String,nullable=False)
    role = Column(Enum(StaffRole),nullable=False)
    
    #relationships
    standard = relationship("Standard",back_populates="class_teacher",uselist=False)
    attendance_records = relationship("Attendance", back_populates="recorded_by_staff")
    
    