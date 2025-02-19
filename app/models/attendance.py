from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.databases import Base
import uuid
class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(String, primary_key=True,index=True,default=lambda:str(uuid.uuid4()))
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # present, absent
    student_id = Column(String, ForeignKey("student.student_id"), nullable=False)
    standard_id = Column(String, ForeignKey("standard.standard_id"), nullable=False)
    recorded_by = Column(String, ForeignKey("staff.staff_id"), nullable=False)  # Teacher who marked attendance

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    standard = relationship("Standard", back_populates="attendance_records")
    recorded_by_staff = relationship("Staff", back_populates="attendance_records")