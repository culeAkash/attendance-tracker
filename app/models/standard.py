from sqlalchemy import Column, Integer, String,ForeignKey,DateTime,Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class Standard(Base):
    __tablename__ = 'standard'
    
    standard_id = Column(String,primary_key=True,index=True,default=lambda:str(uuid.uuid4()))
    grade = Column(String,nullable=False)  # e.g., "1st Grade"
    section = Column(String,nullable=False)  # e.g., "A"
    class_teacher_id = Column(String,ForeignKey("staff.staff_id"),nullable=False,index=True)
    
    # Relationship with Student model
    students = relationship("Student", back_populates="standard")
    class_teacher = relationship("Staff", back_populates="standard",uselist=False)
    attendance_records = relationship("Attendance", back_populates="standard")
    