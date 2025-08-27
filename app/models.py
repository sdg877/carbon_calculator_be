from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    footprints = relationship("Footprint", back_populates="user")

class Footprint(Base):
    __tablename__ = "footprints"

    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(String, nullable=False)
    carbon_kg = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="footprints")
