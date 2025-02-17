from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # present, absent
    student_id = Column(Integer, ForeignKey("student.student_id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standard.standard_id"), nullable=False)
    recorded_by = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)  # Teacher who marked attendance

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    standard = relationship("Standard", back_populates="attendance_records")
    recorded_by_staff = relationship("Staff", back_populates="attendance_records")