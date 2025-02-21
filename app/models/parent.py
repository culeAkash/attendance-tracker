from sqlalchemy import Column, Integer, String,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from app.databases import Base
from sqlalchemy import ForeignKey
class Parent(Base):
    __tablename__ = 'parent'
    
    parent_id = Column(String, primary_key=True, index=True,default=lambda:str(uuid.uuid4()))
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    is_synced = Column(Boolean, default=False)
    # Relationship with Student model
    students = relationship("Student", back_populates="parent")