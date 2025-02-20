from sqlalchemy import Column, String, Date, ForeignKey,Boolean,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.databases import Base
import uuid
import enum
from datetime import date

class StatusOptions(enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"

class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(String, primary_key=True,index=True,default=lambda:str(uuid.uuid4()))
    date_of_attendance = Column(Date, nullable=False)
    status = Column(Enum(StatusOptions), nullable=False,default=StatusOptions.PRESENT)  # present, absent
    student_id = Column(String, ForeignKey("student.student_id"), nullable=False)
    standard_id = Column(String, ForeignKey("standard.standard_id"), nullable=False)
    recorded_by_id = Column(String, ForeignKey("staff.staff_id"), nullable=False)  # Teacher who marked attendance
    is_synced = Column(Boolean, default=False)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    standard = relationship("Standard", back_populates="attendance_records")
    recorded_by_staff = relationship("Staff", back_populates="attendance_records")
    
    
    