from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Student(Base):
    __tablename__ = 'student'
    
    student_id = Column(String, primary_key=True, index=True,default=str(uuid.uuid4()))
    name = Column(String, index=True)
    roll_number = Column(String, index=True)
    ate_of_birth = Column(Date, nullable=False)
    standard_id = Column(Integer, ForeignKey('standard.standard_id'))
    parent_id = Column(Integer, ForeignKey('parent.parent_id'))
    
    # Relationship with Parent model
    standard = relationship("Standard", back_populates="students")
    parent = relationship("Parent", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")