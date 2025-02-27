from sqlalchemy import Column, String,ForeignKey,UniqueConstraint,Enum,Boolean
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
    is_synced = Column(Boolean, default=False)
    
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
    
    @staticmethod
    def get_standard_by_id(standard_id, db:Session):
        standard = db.query(Standard).filter_by(standard_id=standard_id).first()
        if not standard:
            raise ResourceNotFoundException("Standard","standard_id",standard_id)
        return standard
    
    @staticmethod
    def get_standards_by_class_teacher_id(class_teacher_id, db:Session):
        standards = db.query(Standard).filter_by(class_teacher_id=class_teacher_id).all()
        return standards
    
    @staticmethod
    def get_mapped_grade_by_enum_string(enum_string):
        match enum_string:
            case Grade.NURSERY:
                return "NURSERY"
            case Grade.UKG:
                return "UKG"
            case Grade.LKG:
                return "LKG"
            case Grade.STD_1:
                return "STD_1"
            case Grade.STD_2:
                return "STD_2"
            case Grade.STD_3:
                return "STD_3"
            case Grade.STD_4:
                return "STD_4"
            case Grade.STD_5:
                return "STD_5"
            case Grade.STD_6:
                return "STD_6"
            case Grade.STD_7:
                return "STD_7"
            case Grade.STD_8:
                return "STD_8"
            case Grade.STD_9:
                return "STD_9"
            case Grade.STD_10:
                return "STD_10"
            case Grade.STD_11:
                return "STD_11"
            case Grade.STD_12:
                return "STD_12"
    
        
    