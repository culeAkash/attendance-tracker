from sqlalchemy import Column, Integer, String, Date, ForeignKey,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from app.databases import Base
import enum
from sqlalchemy.orm import Session
from app.exceptions import ResourceNotFoundException

class Gender(enum.Enum):
    MALE = 'Male'
    FEMALE = 'Female'

class Address(Base):
    __tablename__ = 'address'
    address_id = Column(String, primary_key=True, index=True,default=lambda:str(uuid.uuid4()))
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    student = relationship("Student", back_populates="address")

class Student(Base):
    __tablename__ = 'student'
    
    student_id = Column(String, primary_key=True, index=True,default=lambda:str(uuid.uuid4()))
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
    
    
    @staticmethod
    async def get_next_roll_number(db:Session):
        last_roll_number = db.query(Student.roll_number).order_by(Student.roll_number.desc()).first()
        if last_roll_number and last_roll_number[0]:
            next_roll_number = int(last_roll_number[0]) + 1
        else:
            next_roll_number = 1
        return next_roll_number
    
    @staticmethod
    async def get_student_by_id(db:Session, student_id: str):
        student =  db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise ResourceNotFoundException("Student","student_id",student_id)
        return student