from sqlalchemy import Column, Integer, String, Date, ForeignKey,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from app.databases import Base
import enum

class Gender(enum.Enum):
    MALE = 'Male'
    FEMALE = 'Female'

class Address(Base):
    __tablename__ = 'address'
    address_id = Column(String, primary_key=True, index=True,default=str(uuid.uuid4()))
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    student = relationship("Student", back_populates="address")

class Student(Base):
    __tablename__ = 'student'
    
    student_id = Column(String, primary_key=True, index=True,default=str(uuid.uuid4()))
    name = Column(String, index=True)
    roll_number = Column(Integer, index=True,autoincrement=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    standard_id = Column(String, ForeignKey('standard.standard_id'))
    parent_id = Column(String, ForeignKey('parent.parent_id'))
    address_id = Column(String, ForeignKey('address.address_id'))
    
    # Relationship with Parent model
    standard = relationship("Standard", back_populates="students")
    parent = relationship("Parent", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")
    address = relationship("Address", back_populates="student",uselist=False)