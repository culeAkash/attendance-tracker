from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from app.databases import Base

class Parent(Base):
    __tablename__ = 'parent'
    
    parent_id = Column(String, primary_key=True, index=True,default= str(uuid.uuid4()))
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    
    # Relationship with Student model
    students = relationship("Student", back_populates="parent")