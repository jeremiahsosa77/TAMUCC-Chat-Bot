from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base

# Association table for many-to-many relationships
department_faculty = Table(
    'department_faculty',
    Base.metadata,
    Column('department_id', Integer, ForeignKey('departments.id')),
    Column('faculty_id', Integer, ForeignKey('faculty.id'))
)

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    location = Column(String)
    contact_info = Column(String)
    faculty = relationship("Faculty", secondary=department_faculty, back_populates="departments")
    programs = relationship("Program", back_populates="department")

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    degree_type = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="programs")

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    title = Column(String)
    email = Column(String)
    office_location = Column(String)
    office_hours = Column(String)
    departments = relationship("Department", secondary=department_faculty, back_populates="faculty")

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True)
    location = Column(String)
    description = Column(Text)
    hours = Column(String)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    location = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    organizer = Column(String)
    category = Column(String)

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    location = Column(String)
    contact_info = Column(String)
    hours = Column(String)
    category = Column(String) 