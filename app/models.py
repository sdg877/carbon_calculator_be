from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    footprints = relationship("Footprint", back_populates="user")


# class Footprint(Base):
#     __tablename__ = "footprints"

#     id = Column(Integer, primary_key=True, index=True)
#     activity_type = Column(String, nullable=False)
#     carbon_kg = Column(Float, nullable=False)
#     details = Column(JSON, nullable=True)
#     suggested_offsets = Column(JSON, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     user_id = Column(Integer, ForeignKey("users.id"))
#     user = relationship("User", back_populates="footprints")

class Footprint(Base):
    __tablename__ = "footprints"

    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(String, nullable=False)
    carbon_kg = Column(Float, nullable=False)
    details = Column(JSON, nullable=True)
    suggested_offsets = Column(JSON, nullable=True)
    # This tracks when the entry was physically created
    created_at = Column(DateTime, default=datetime.utcnow)
    # This is the date the user chooses in the form
    entry_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="footprints")
