from sqlalchemy import Column, String,ForeignKey,UniqueConstraint,Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from app.databases import Base
from app.databases import get_sqlite_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.exceptions import ResourceNotFoundException
import enum

class Grade(enum.Enum):
    NURSERY = "NURSERY",
    UKG = "UKG",
    LKG = "LKG",
    STD_1 = "STD_1",
    STD_2 = "STD_2",
    STD_3 = "STD_3",
    STD_4 = "STD_4",
    STD_5 = "STD_5",
    STD_6 = "STD_6",
    STD_7 = "STD_7",
    STD_8 = "STD_8",
    STD_9 = "STD_9",
    STD_10 = "STD_10",
    STD_11 = "STD_11",
    STD_12 = "STD_12"
    
    

class Standard(Base):
    __tablename__ = 'standard'
    
    standard_id = Column(String,primary_key=True,index=True,default=lambda:str(uuid.uuid4()))
    grade = Column(Enum(Grade),nullable=False)  # e.g., "STD_1"
    section = Column(String,nullable=False)  # e.g., "A"
    class_teacher_id = Column(String,ForeignKey("staff.staff_id"),nullable=False,index=True)
    
    # Enforce unique constraint on grade and section together
    __table_args__ = (UniqueConstraint('grade', 'section', name='unique_standard'),)
    
    # Relationship with Student model
    students = relationship("Student", back_populates="standard")
    class_teacher = relationship("Staff", back_populates="standard",uselist=False)
    attendance_records = relationship("Attendance", back_populates="standard")
    
    @staticmethod
    def get_next_section(grade,db:Session):
        last_section = db.query(Standard.section).filter_by(grade=grade).order_by(Standard.section.desc()).first()
        if last_section:
            next_section = chr(ord(last_section[0]) + 1)
        else:
            next_section = 'A'
        return next_section
    
    @staticmethod
    def get_standard_by_grade_and_section(grade, section, db:Session):
        standard = db.query(Standard).filter_by(grade=grade, section=section).first()
        if not standard:
            raise ResourceNotFoundException("Standard","grade and section",f"{grade},{section}")
        # standard.grade = standard.grade[0]
        return standard
    
    
        
    