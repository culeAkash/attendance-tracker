from .staff import Staff, StaffRole
from .standard import Standard
from .student import Student
from .parent import Parent
from .attendance import Attendance
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()